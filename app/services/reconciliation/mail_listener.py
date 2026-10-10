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


def sync_mailbox_invoices(db: Session, account_rfc: str = "DEGF851127TK1") -> Dict[str, Any]:
    """
    Se conecta al buzón dedicado de correo vía IMAP para la entidad seleccionada (HIPHA o AMDI),
    extrae adjuntos .xml y .csv de correos no leídos, los procesa e inserta en la base de datos
    asociándolos a la entidad respectiva.
    """
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
        mail = imaplib.IMAP4_SSL(host, port)
        mail.login(user, password)
        status, _ = mail.select(folder)
        if status != "OK":
            raise ValueError(f"No se pudo acceder a la carpeta {folder} en el servidor IMAP.")

        # Buscar correos no leídos
        status, data = mail.search(None, "UNSEEN")
        if status != "OK" or not data or not data[0]:
            return {
                "success": True,
                "connected": True,
                "message": "Buzón sincronizado. No hay correos nuevos sin leer.",
                "processed_xmls": 0,
                "processed_statements": 0,
            }

        mail_ids = data[0].split()

        for mid in mail_ids:
            try:
                res, msg_data = mail.fetch(mid, "(RFC822)")
                if res != "OK":
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                subject = _decode_mime_header(msg.get("Subject", ""))
                sender = _decode_mime_header(msg.get("From", ""))

                for part in msg.walk():
                    # Si no es adjunto, saltar
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    filename = part.get_filename()
                    if not filename:
                        continue

                    filename = _decode_mime_header(filename)
                    filename_lower = filename.lower()
                    payload = part.get_payload(decode=True)

                    if not payload:
                        continue

                    # 1. Enrutar si es XML
                    if filename_lower.endswith(".xml"):
                        try:
                            cfdi_data = parse_cfdi_xml(payload, mi_rfc=entity_rfc)
                            uuid = cfdi_data["uuid"]
                            
                            existing = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid).first()
                            if not existing:
                                new_invoice = CFDIInvoice(
                                    uuid=uuid,
                                    account_rfc=entity_rfc,
                                    area_proyecto=entity_name,
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
                                    conciliado=False,
                                    fuente="EMAIL",
                                    xml_raw=payload.decode("utf-8", errors="ignore")
                                )
                                db.add(new_invoice)
                                processed_xmls += 1
                        except Exception as e_xml:
                            errors.append(f"Error procesando {filename}: {str(e_xml)}")

                    # 2. Enrutar si es CSV / XLSX (Estado de cuenta)
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
                "tipo": t.tipo
            } for t in tx_pendientes]

            if facturas_dict and tx_list:
                conciliados = conciliar_movimientos(tx_list, facturas_dict)
                for res in conciliados:
                    if res.get("uuid_cfdi"):
                        db_tx = db.query(BankTransaction).filter(BankTransaction.id_transaccion == res["id_transaccion"]).first()
                        if db_tx:
                            db_tx.uuid_cfdi = res["uuid_cfdi"]
                            db_tx.status_conciliacion = res["status_conciliacion"]
                            db_tx.confianza_score = res["confianza_score"]
                            db_tx.nota_revision = res["nota_revision"]

                        if res["status_conciliacion"] == "CONCILIADO":
                            db_f = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == res["uuid_cfdi"]).first()
                            if db_f:
                                db_f.conciliado = True

                db.commit()

        except Exception as e_match:
            errors.append(f"Error en conciliación posterior al buzón: {e_match}")

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
