import imaplib
import email
from email.header import decode_header
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.config import settings, get_reconciliation_entity_config
from app.models.reconciliation import CFDIInvoice, BankTransaction
from app.services.reconciliation.cfdi_parser import parse_cfdi_xml
from app.services.reconciliation.bbva_parser import parse_bbva_statement
from app.services.reconciliation.matching_engine import conciliar_movimientos


def _decode_mime_header(header_val: str) -> str:
    if not header_val:
        return ""
    decoded_fragments = decode_header(header_val)
    result = []
    for frag, enc in decoded_fragments:
        if isinstance(frag, bytes):
            result.append(frag.decode(enc or 'utf-8', errors='ignore'))
        else:
            result.append(str(frag))
    return "".join(result)


def auto_reconcile_cash_expenses(db: Session, effective_rfc: str = None) -> int:
    """
    Concilia y ampara automáticamente todas las facturas de egreso pagadas en efectivo (forma_pago == '01').
    Las facturas en efectivo no generan movimientos bancarios en la cuenta fiscal (BBVA) y quedan
    amparadas directamente como comprobadas/conciliadas fuera de banco sin requerir intervención del usuario.
    """
    from sqlalchemy import or_
    query = db.query(CFDIInvoice).filter(
        CFDIInvoice.tipo == "EGRESO",
        or_(
            CFDIInvoice.forma_pago == "01",
            CFDIInvoice.forma_pago.ilike("%01%"),
            CFDIInvoice.forma_pago.ilike("%efectivo%")
        ),
        or_(
            CFDIInvoice.conciliado == False,
            CFDIInvoice.comprobado == False,
            CFDIInvoice.motivo_comprobacion != "Pago efectivo"
        )
    )
    if effective_rfc:
        query = query.filter(CFDIInvoice.account_rfc == effective_rfc)

    cash_invoices = query.all()
    count = len(cash_invoices)
    if count > 0:
        for inv in cash_invoices:
            inv.conciliado = True
            inv.comprobado = True
            inv.motivo_comprobacion = "Pago efectivo"
        db.commit()
    return count


def reclassify_invoices_by_fiscal_rfc(db: Session) -> int:
    """
    Reclasifica las facturas CFDI en la base de datos a su entidad correcta según el RFC del receptor o emisor:
    - Si el receptor o emisor es MEHA850118Q96 (AMDI), su account_rfc DEBE ser MEHA850118Q96 y area_proyecto 'AMDI'.
    - Si el receptor o emisor es DEGF851127TK1 (HIPHA), su account_rfc DEBE ser DEGF851127TK1 y area_proyecto 'HiphaMX'.
    Esto soluciona comprobantes recibidos en el buzón compartido o reenviados (ej. EXPO OBRA BLANCA)
    que fueron guardados con el account_rfc de la casilla IMAP en lugar del RFC fiscal del comprobante.
    """
    from sqlalchemy import or_
    reclassified = 0

    # 1. Facturas que pertenecen a AMDI pero están asignadas a otra cuenta
    amdi_invoices = db.query(CFDIInvoice).filter(
        or_(
            CFDIInvoice.rfc_receptor == "MEHA850118Q96",
            CFDIInvoice.rfc_emisor == "MEHA850118Q96"
        ),
        CFDIInvoice.account_rfc != "MEHA850118Q96"
    ).all()
    for inv in amdi_invoices:
        inv.account_rfc = "MEHA850118Q96"
        inv.area_proyecto = "AMDI"
        if inv.rfc_emisor == "MEHA850118Q96" and inv.tipo != "EGRESO":
            inv.tipo = "INGRESO"
        elif inv.rfc_receptor == "MEHA850118Q96" and inv.tipo != "INGRESO":
            inv.tipo = "EGRESO"
        reclassified += 1

    # 2. Facturas que pertenecen a HIPHA pero están asignadas a otra cuenta
    hipha_invoices = db.query(CFDIInvoice).filter(
        or_(
            CFDIInvoice.rfc_receptor == "DEGF851127TK1",
            CFDIInvoice.rfc_emisor == "DEGF851127TK1"
        ),
        CFDIInvoice.account_rfc != "DEGF851127TK1"
    ).all()
    for inv in hipha_invoices:
        inv.account_rfc = "DEGF851127TK1"
        inv.area_proyecto = "HiphaMX"
        if inv.rfc_emisor == "DEGF851127TK1" and inv.tipo != "EGRESO":
            inv.tipo = "INGRESO"
        elif inv.rfc_receptor == "DEGF851127TK1" and inv.tipo != "INGRESO":
            inv.tipo = "EGRESO"
        reclassified += 1

    if reclassified > 0:
        db.commit()
    return reclassified


def sync_mailbox_invoices(db: Session, account_rfc: str = "DEGF851127TK1", lookback_days: int = 60) -> Dict[str, Any]:
    """
    Se conecta al buzón dedicado de correo vía IMAP para la entidad seleccionada (HIPHA o AMDI),
    extrae adjuntos .xml y .csv de correos (tanto no leídos como recientes de los últimos lookback_days),
    los procesa e inserta en la base de datos asociándolos a la entidad respectiva.
    """
    import datetime
    import io
    import zipfile

    entity_cfg = get_reconciliation_entity_config(account_rfc)
    host = entity_cfg["host"]
    user = entity_cfg["user"]
    password = entity_cfg["password"]
    port = entity_cfg["port"]
    folder = entity_cfg["folder"]
    entity_rfc = entity_cfg["rfc"]
    entity_name = entity_cfg["name"]

    if not host or not user or not password:
        return {
            "success": False,
            "connected": False,
            "message": f"Credenciales IMAP no configuradas para {entity_name} ({entity_rfc}).",
            "processed_xmls": 0,
            "processed_statements": 0,
        }

    processed_xmls = 0
    processed_statements = 0
    errors: List[str] = []

    mail = None
    try:
        try:
            mail = imaplib.IMAP4_SSL(host, port)
        except Exception:
            # Fallback en caso de mismatch de certificado de servidor compartido (ej. Neubox cPanel)
            import ssl
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            mail = imaplib.IMAP4_SSL(host, port, ssl_context=ssl_ctx)

        mail.login(user, password)
        status, _ = mail.select(folder)
        if status != "OK":
            raise ValueError(f"No se pudo acceder a la carpeta {folder} en el servidor IMAP.")

        # 1. Buscar correos no leídos (sin importar fecha)
        status_unseen, data_unseen = mail.search(None, "UNSEEN")
        unseen_ids = [int(i) for i in data_unseen[0].split()] if (status_unseen == "OK" and data_unseen and data_unseen[0]) else []

        # 2. Buscar correos recientes (últimos lookback_days) para no perder facturas abiertas/leídas en Webmail o móvil
        since_date = (datetime.date.today() - datetime.timedelta(days=max(1, lookback_days))).strftime("%d-%b-%Y")
        status_since, data_since = mail.search(None, f"(SINCE {since_date})")
        since_ids = [int(i) for i in data_since[0].split()] if (status_since == "OK" and data_since and data_since[0]) else []

        # 3. Combinar IDs únicos y ordenar del más reciente al más antiguo (máximo 100 correos para no exceder timeout)
        all_ids = sorted(list(set(unseen_ids + since_ids)), reverse=True)
        mail_ids = all_ids[:100]

        if not mail_ids:
            return {
                "success": True,
                "connected": True,
                "message": "Buzón sincronizado. No hay correos en el período evaluado.",
                "processed_xmls": 0,
                "processed_statements": 0,
            }

        def process_xml_bytes(xml_bytes: bytes, src_filename: str):
            nonlocal processed_xmls
            try:
                cfdi_data = parse_cfdi_xml(xml_bytes, mi_rfc=entity_rfc)
                uuid = cfdi_data["uuid"]
                
                # Determinar la entidad fiscal real según receptor/emisor del CFDI
                rec_rfc = (cfdi_data.get("rfc_receptor") or "").strip().upper()
                emi_rfc = (cfdi_data.get("rfc_emisor") or "").strip().upper()

                target_account_rfc = entity_rfc
                target_area_name = entity_name

                if rec_rfc == "MEHA850118Q96" or emi_rfc == "MEHA850118Q96":
                    target_account_rfc = "MEHA850118Q96"
                    target_area_name = "AMDI"
                elif rec_rfc == "DEGF851127TK1" or emi_rfc == "DEGF851127TK1":
                    target_account_rfc = "DEGF851127TK1"
                    target_area_name = "HiphaMX"

                # Re-parsear clasificación fiscal si target_account_rfc difiere de entity_rfc
                if target_account_rfc != entity_rfc:
                    cfdi_data = parse_cfdi_xml(xml_bytes, mi_rfc=target_account_rfc)

                forma_pago_val = str(cfdi_data.get("forma_pago") or "").strip()
                is_cash_egreso = (cfdi_data["tipo"] == "EGRESO" and (forma_pago_val == "01" or "01" in forma_pago_val or "efectivo" in forma_pago_val.lower()))

                existing = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid).first()
                if not existing:
                    new_invoice = CFDIInvoice(
                        uuid=uuid,
                        account_rfc=target_account_rfc,
                        area_proyecto=target_area_name,
                        tipo=cfdi_data["tipo"],
                        rfc_emisor=cfdi_data["rfc_emisor"],
                        nombre_emisor=cfdi_data["nombre_emisor"],
                        rfc_receptor=cfdi_data["rfc_receptor"],
                        nombre_receptor=cfdi_data["nombre_receptor"],
                        fecha_emision=cfdi_data["fecha_emision"],
                        subtotal=cfdi_data["subtotal"],
                        iva_trasladado=cfdi_data["iva_trasladado"],
                        retencion_isr=cfdi_data.get("retencion_isr", 0.0),
                        retencion_iva=cfdi_data.get("retencion_iva", 0.0),
                        retenciones=cfdi_data["retenciones"],
                        total=cfdi_data["total"],
                        metodo_pago=cfdi_data["metodo_pago"],
                        forma_pago=cfdi_data["forma_pago"],
                        conceptos_resumen=cfdi_data["conceptos_resumen"],
                        conciliado=is_cash_egreso,
                        comprobado=is_cash_egreso,
                        motivo_comprobacion="Pago efectivo" if is_cash_egreso else None,
                        fuente="EMAIL",
                        xml_raw=xml_bytes.decode("utf-8", errors="ignore")
                    )
                    db.add(new_invoice)
                    processed_xmls += 1
                else:
                    if existing.account_rfc != target_account_rfc:
                        existing.account_rfc = target_account_rfc
                        existing.area_proyecto = target_area_name
                    if is_cash_egreso and (not existing.conciliado or not existing.comprobado or existing.motivo_comprobacion != "Pago efectivo"):
                        existing.conciliado = True
                        existing.comprobado = True
                        existing.motivo_comprobacion = "Pago efectivo"
            except Exception as e_xml:
                errors.append(f"Error procesando {src_filename}: {str(e_xml)}")

        for mid in mail_ids:
            try:
                res, msg_data = mail.fetch(str(mid).encode(), "(RFC822)")
                if res != "OK":
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue

                    filename = part.get_filename()
                    content_type = part.get_content_type()
                    
                    if not filename:
                        if content_type in ['text/xml', 'application/xml']:
                            filename = "cfdi_attachment.xml"
                        else:
                            continue

                    filename = _decode_mime_header(filename)
                    filename_lower = filename.lower()
                    payload = part.get_payload(decode=True)

                    if not payload:
                        continue

                    # 1. Enrutar si es XML
                    if filename_lower.endswith(".xml") or (b"<cfdi:Comprobante" in payload or b"cfdi" in payload[:200].lower()):
                        process_xml_bytes(payload, filename)

                    # 2. Enrutar si es ZIP (descomprimir en memoria y buscar XMLs)
                    elif filename_lower.endswith(".zip"):
                        try:
                            with zipfile.ZipFile(io.BytesIO(payload)) as z:
                                for z_name in z.namelist():
                                    if z_name.lower().endswith(".xml"):
                                        z_payload = z.read(z_name)
                                        process_xml_bytes(z_payload, f"{filename}/{z_name}")
                        except Exception as e_zip:
                            errors.append(f"Error descomprimiendo ZIP {filename}: {str(e_zip)}")

                    # 3. Enrutar si es CSV / XLSX (Estado de cuenta)
                    elif filename_lower.endswith(".csv") or filename_lower.endswith(".xlsx"):
                        try:
                            transacciones = parse_bbva_statement(payload, filename, account_rfc=entity_rfc)
                            for tx in transacciones:
                                existing_tx = db.query(BankTransaction).filter(BankTransaction.id_transaccion == tx["id_transaccion"]).first()
                                if not existing_tx:
                                    new_tx = BankTransaction(
                                        account_rfc=entity_rfc,
                                        area_proyecto=entity_name,
                                        tipo_categoria="INGRESO" if tx["tipo"] == "INGRESO" else "GASTO",
                                        id_transaccion=tx["id_transaccion"],
                                        banco=tx["banco"],
                                        fecha=tx["fecha"],
                                        concepto=tx["concepto"],
                                        monto=tx["monto"],
                                        tipo=tx["tipo"],
                                        saldo=tx.get("saldo"),
                                        status_conciliacion="SIN_CFDI",
                                        confianza_score=0.0,
                                        periodo_mes=tx["periodo_mes"]
                                    )
                                    db.add(new_tx)
                                    processed_statements += 1
                        except Exception as e_stmt:
                            # Puede no ser un estado de cuenta sino otro archivo de Excel
                            pass

                # Guardar en base de datos cada correo
                db.commit()

            except Exception as e_mid:
                errors.append(f"Error procesando mensaje ID {mid}: {str(e_mid)}")

        # Ejecutar corrida del motor de conciliación automática filtrando por la entidad activa
        try:
            # Facturas disponibles de la entidad
            facturas_pendientes = db.query(CFDIInvoice).filter(
                CFDIInvoice.conciliado == False,
                CFDIInvoice.account_rfc == entity_rfc
            ).all()
            facturas_dict = [{
                "uuid": f.uuid,
                "tipo": f.tipo,
                "rfc_emisor": f.rfc_emisor,
                "nombre_emisor": f.nombre_emisor,
                "rfc_receptor": f.rfc_receptor,
                "nombre_receptor": f.nombre_receptor,
                "fecha_emision": f.fecha_emision,
                "subtotal": f.subtotal,
                "iva": f.iva_trasladado,
                "total": f.total
            } for f in facturas_pendientes]

            # Transacciones bancarias pendientes de conciliar de la entidad
            tx_pendientes = db.query(BankTransaction).filter(
                BankTransaction.status_conciliacion != "CONCILIADO",
                BankTransaction.account_rfc == entity_rfc
            ).all()
            tx_list = [{
                "id": t.id,
                "id_transaccion": t.id_transaccion,
                "fecha": t.fecha,
                "concepto": t.concepto,
                "monto": t.monto,
                "tipo": t.tipo,
                "banco": t.banco,
                "area_proyecto": t.area_proyecto
            } for t in tx_pendientes]

            if facturas_dict and tx_list:
                conciliados = conciliar_movimientos(tx_list, facturas_dict)
                for res in conciliados:
                    db_tx = db.query(BankTransaction).filter(BankTransaction.id_transaccion == res["id_transaccion"]).first()
                    if db_tx:
                        if res.get("uuid_cfdi"):
                            db_tx.uuid_cfdi = res["uuid_cfdi"]
                            db_tx.status_conciliacion = res["status_conciliacion"]
                            db_tx.confianza_score = res["confianza_score"]
                            db_tx.nota_revision = res["nota_revision"]

                            if res["status_conciliacion"] == "CONCILIADO":
                                db_f = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == res["uuid_cfdi"]).first()
                                if db_f:
                                    db_f.conciliado = True
                        else:
                            if res.get("area_proyecto") and (not db_tx.area_proyecto or db_tx.area_proyecto in [entity_name, "General"]):
                                db_tx.area_proyecto = res["area_proyecto"]
                            if res.get("nota_revision") and not db_tx.nota_revision:
                                db_tx.nota_revision = res["nota_revision"]

                db.commit()

        except Exception as e_match:
            errors.append(f"Error en conciliación posterior al buzón: {e_match}")

        # Reclasificar facturas por RFC fiscal y auto-conciliar egresos en efectivo
        try:
            reclassify_invoices_by_fiscal_rfc(db)
            auto_reconcile_cash_expenses(db, entity_rfc)
        except Exception as e_post:
            errors.append(f"Error en post-proceso de buzón: {e_post}")

        return {
            "success": True,
            "connected": True,
            "message": f"Sincronización completada. Se procesaron {processed_xmls} facturas XML y {processed_statements} transacciones bancarias.",
            "processed_xmls": processed_xmls,
            "processed_statements": processed_statements,
            "errors": errors[:5]
        }

    except Exception as e_imap:
        return {
            "success": False,
            "connected": False,
            "message": f"Falla de conexión IMAP: {str(e_imap)}",
            "processed_xmls": processed_xmls,
            "processed_statements": processed_statements,
            "errors": [str(e_imap)]
        }
    finally:
        if mail:
            try:
                mail.close()
                mail.logout()
            except Exception:
                pass
