from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query, Header
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List, Dict
import io
import zipfile
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from app.core.config import settings, get_reconciliation_entity_config
from app.models.reconciliation import CFDIInvoice, BankTransaction
from app.services.reconciliation.cfdi_parser import parse_cfdi_xml
from app.services.reconciliation.bbva_parser import parse_bbva_statement
from app.services.reconciliation.matching_engine import conciliar_movimientos
from app.services.reconciliation.excel_exporter import export_reconciliation_excel
from app.services.reconciliation.pdf_reporter import generate_discrepancies_pdf
from app.services.reconciliation.backfill import import_historical_excel
from app.services.reconciliation.mail_listener import sync_mailbox_invoices

router = APIRouter()


@router.get("/overview")
def get_reconciliation_overview(
    month: Optional[str] = Query(None, description="Mes en formato YYYY-MM"),
    account_rfc: str = Query("DEGF851127TK1", description="RFC de la entidad: DEGF851127TK1 (HIPHA) o MEHA850118Q96 (AMDI)"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retorna métricas KPI consolidadas de conciliación bancaria y fiscal para el período y entidad solicitados.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]
    entity_name = entity_cfg["name"]

    # Meses disponibles en la base de datos para esta entidad
    months_query = db.query(BankTransaction.periodo_mes).filter(
        BankTransaction.account_rfc == effective_rfc
    ).distinct().order_by(desc(BankTransaction.periodo_mes)).all()
    available_months = [m[0] for m in months_query if m[0]]

    # Si no se pasó mes y hay meses disponibles, tomar el más reciente
    selected_month = month
    if not selected_month and available_months:
        selected_month = available_months[0]
    elif not selected_month:
        selected_month = datetime.now().strftime("%Y-%m")

    # Filtro base por entidad y mes
    query = db.query(BankTransaction).filter(
        BankTransaction.account_rfc == effective_rfc,
        BankTransaction.periodo_mes == selected_month
    )
    all_txs = query.all()

    ingresos_txs = [t for t in all_txs if t.tipo == "INGRESO"]
    egresos_txs = [t for t in all_txs if t.tipo == "EGRESO"]

    total_ingresos_banco = sum(t.monto for t in ingresos_txs)
    total_egresos_banco = sum(t.monto for t in egresos_txs)

    conciliados_ingresos = [t for t in ingresos_txs if t.status_conciliacion == "CONCILIADO"]
    conciliados_egresos = [t for t in egresos_txs if t.status_conciliacion == "CONCILIADO"]

    sin_cfdi_egresos = [t for t in egresos_txs if t.status_conciliacion == "SIN_CFDI"]
    monto_sin_cfdi = sum(t.monto for t in sin_cfdi_egresos)
    count_sin_cfdi = len(sin_cfdi_egresos)

    monto_egresos_conciliados = sum(t.monto for t in conciliados_egresos)
    pct_egresos_facturados = round((monto_egresos_conciliados / total_egresos_banco * 100), 1) if total_egresos_banco > 0 else 0.0

    monto_ingresos_conciliados = sum(t.monto for t in conciliados_ingresos)
    pct_ingresos_facturados = round((monto_ingresos_conciliados / total_ingresos_banco * 100), 1) if total_ingresos_banco > 0 else 0.0

    # Facturas disponibles sin conciliar para esta entidad
    facturas_disponibles_count = db.query(CFDIInvoice).filter(
        CFDIInvoice.account_rfc == effective_rfc,
        CFDIInvoice.conciliado == False
    ).count()

    return {
        "entity": {
            "rfc": effective_rfc,
            "name": entity_name
        },
        "entity_name": entity_name,
        "account_rfc": effective_rfc,
        "selected_month": selected_month,
        "available_months": available_months,
        "kpis": {
            "total_ingresos_banco": round(total_ingresos_banco, 2),
            "count_ingresos_banco": len(ingresos_txs),
            "total_egresos_banco": round(total_egresos_banco, 2),
            "count_egresos_banco": len(egresos_txs),
            "monto_sin_cfdi": round(monto_sin_cfdi, 2),
            "count_sin_cfdi": count_sin_cfdi,
            "pct_egresos_facturados": pct_egresos_facturados,
            "pct_ingresos_facturados": pct_ingresos_facturados,
            "monto_egresos_conciliados": round(monto_egresos_conciliados, 2),
            "count_egresos_conciliados": len(conciliados_egresos),
            "monto_ingresos_conciliados": round(monto_ingresos_conciliados, 2),
            "count_ingresos_conciliados": len(conciliados_ingresos),
            "monto_conciliado": round(monto_egresos_conciliados, 2),
            "count_conciliado": len(conciliados_egresos),
            "facturas_disponibles_count": facturas_disponibles_count,
            "total_transacciones": len(all_txs)
        }
    }


@router.get("/transactions")
def get_reconciliation_transactions(
    month: Optional[str] = Query(None),
    status: Optional[str] = Query("ALL"),
    tipo: Optional[str] = Query("ALL"),
    search: Optional[str] = Query(None),
    account_rfc: str = Query("DEGF851127TK1"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retorna la lista de transacciones bancarias del mes con datos del CFDI asociado y las 14 columnas fiscales.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]
    entity_name = entity_cfg["name"]

    query = db.query(BankTransaction).filter(BankTransaction.account_rfc == effective_rfc)

    if month:
        query = query.filter(BankTransaction.periodo_mes == month)

    if status and status != "ALL":
        query = query.filter(BankTransaction.status_conciliacion == status)

    if tipo and tipo != "ALL":
        query = query.filter(BankTransaction.tipo == tipo)

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            (BankTransaction.concepto.ilike(search_filter)) |
            (BankTransaction.uuid_cfdi.ilike(search_filter))
        )

    # Ordenar por fecha descendente
    txs = query.order_by(desc(BankTransaction.fecha), desc(BankTransaction.id)).all()

    results = []
    for t in txs:
        cfdi_data = None
        contraparte = ""
        metodo_pago = ""
        subtotal_val = 0.0
        iva_ing_val = 0.0
        ret_isr_val = 0.0
        iva_egr_val = 0.0

        if t.factura:
            f = t.factura
            contraparte = f.nombre_receptor if t.tipo == "INGRESO" else f.nombre_emisor
            metodo_pago = f.metodo_pago or "PUE"
            subtotal_val = float(f.subtotal or 0.0)
            ret_isr_val = float(getattr(f, "retencion_isr", 0.0) or f.retenciones or 0.0)

            if t.tipo == "INGRESO":
                iva_ing_val = float(f.iva_trasladado or 0.0)
            else:
                iva_egr_val = float(f.iva_trasladado or 0.0)

            cfdi_data = {
                "uuid": f.uuid,
                "rfc_emisor": f.rfc_emisor,
                "nombre_emisor": f.nombre_emisor,
                "rfc_receptor": f.rfc_receptor,
                "nombre_receptor": f.nombre_receptor,
                "fecha_emision": f.fecha_emision.strftime("%Y-%m-%d") if f.fecha_emision else "",
                "subtotal": f.subtotal,
                "iva": f.iva_trasladado,
                "retenciones": f.retenciones,
                "retencion_isr": ret_isr_val,
                "retencion_iva": getattr(f, "retencion_iva", 0.0),
                "total": f.total,
                "metodo_pago": f.metodo_pago,
                "conceptos_resumen": f.conceptos_resumen
            }

        area_proyecto = t.area_proyecto or entity_name
        tipo_cat = t.tipo_categoria or ("INGRESO" if t.tipo == "INGRESO" else "GASTO")
        cfdi_status_label = "CONCILIADO" if t.uuid_cfdi else ("POR REVISAR" if t.status_conciliacion == "POR_REVISAR" else "SIN CFDI")

        results.append({
            "id": t.id,
            "account_rfc": t.account_rfc,
            "id_transaccion": t.id_transaccion,
            "fecha": t.fecha.strftime("%Y-%m-%d") if t.fecha else "",
            "area_proyecto": area_proyecto,
            "uuid_cfdi": t.uuid_cfdi,
            "contraparte": contraparte,
            "concepto": t.concepto,
            "metodo_pago": metodo_pago,
            "ingresos": t.monto if t.tipo == "INGRESO" else 0.0,
            "egresos": t.monto if t.tipo == "EGRESO" else 0.0,
            "cfdi_status": cfdi_status_label,
            "tipo_categoria": tipo_cat,
            "subtotal": subtotal_val,
            "iva_ingresos": iva_ing_val,
            "retencion_isr": ret_isr_val,
            "iva_egresos": iva_egr_val,
            "monto": t.monto,
            "tipo": t.tipo,
            "saldo": t.saldo,
            "status_conciliacion": t.status_conciliacion,
            "confianza_score": t.confianza_score,
            "nota_revision": t.nota_revision,
            "periodo_mes": t.periodo_mes,
            "cfdi": cfdi_data
        })

    return results


@router.get("/pending-invoices")
def get_pending_invoices(
    tipo: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    account_rfc: str = Query("DEGF851127TK1"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retorna las facturas registradas de la entidad que aún no han sido conciliadas con ningún movimiento bancario.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]

    query = db.query(CFDIInvoice).filter(
        CFDIInvoice.conciliado == False,
        CFDIInvoice.account_rfc == effective_rfc
    )

    if tipo and tipo != "ALL":
        query = query.filter(CFDIInvoice.tipo == tipo)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (CFDIInvoice.nombre_emisor.ilike(s)) |
            (CFDIInvoice.nombre_receptor.ilike(s)) |
            (CFDIInvoice.rfc_emisor.ilike(s)) |
            (CFDIInvoice.rfc_receptor.ilike(s)) |
            (CFDIInvoice.uuid.ilike(s))
        )

    invoices = query.order_by(desc(CFDIInvoice.fecha_emision)).limit(100).all()

    return [{
        "uuid": inv.uuid,
        "account_rfc": inv.account_rfc,
        "area_proyecto": inv.area_proyecto,
        "tipo": inv.tipo,
        "rfc_emisor": inv.rfc_emisor,
        "nombre_emisor": inv.nombre_emisor,
        "rfc_receptor": inv.rfc_receptor,
        "nombre_receptor": inv.nombre_receptor,
        "fecha_emision": inv.fecha_emision.strftime("%Y-%m-%d") if inv.fecha_emision else "",
        "subtotal": inv.subtotal,
        "iva": inv.iva_trasladado,
        "retencion_isr": getattr(inv, "retencion_isr", 0.0),
        "retencion_iva": getattr(inv, "retencion_iva", 0.0),
        "total": inv.total,
        "metodo_pago": inv.metodo_pago,
        "conceptos_resumen": inv.conceptos_resumen
    } for inv in invoices]


@router.post("/upload-files")
async def upload_reconciliation_files(
    files: List[UploadFile] = File(...),
    account_rfc: str = Form("DEGF851127TK1"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Recibe archivos múltiples (XML de CFDI, ZIP de XMLs, o CSV/XLSX de estados de cuenta de BBVA),
    los parsea, almacena y detona el motor de conciliación automático para la entidad fiscal indicada.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]
    entity_name = entity_cfg["name"]

    processed_xmls = 0
    processed_statements = 0
    errors = []

    for file in files:
        filename = file.filename or ""
        filename_lower = filename.lower()
        content = await file.read()

        # 1. Archivo ZIP (descomprimir y procesar XMLs contenidos)
        if filename_lower.endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as z:
                    for zip_info in z.infolist():
                        if zip_info.filename.lower().endswith(".xml"):
                            xml_bytes = z.read(zip_info.filename)
                            try:
                                cfdi_data = parse_cfdi_xml(xml_bytes, mi_rfc=effective_rfc)
                                existing = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == cfdi_data["uuid"]).first()
                                if not existing:
                                    inv = CFDIInvoice(
                                        uuid=cfdi_data["uuid"],
                                        account_rfc=effective_rfc,
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
                                        fuente="DASHBOARD",
                                        xml_raw=xml_bytes.decode("utf-8", errors="ignore")
                                    )
                                    db.add(inv)
                                    processed_xmls += 1
                            except Exception as e_zip_xml:
                                errors.append(f"{zip_info.filename}: {str(e_zip_xml)}")
            except Exception as e_zip:
                errors.append(f"Error abriendo ZIP {filename}: {str(e_zip)}")

        # 2. Archivo XML individual
        elif filename_lower.endswith(".xml"):
            try:
                cfdi_data = parse_cfdi_xml(content, mi_rfc=effective_rfc)
                existing = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == cfdi_data["uuid"]).first()
                if not existing:
                    inv = CFDIInvoice(
                        uuid=cfdi_data["uuid"],
                        account_rfc=effective_rfc,
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
                        fuente="DASHBOARD",
                        xml_raw=content.decode("utf-8", errors="ignore")
                    )
                    db.add(inv)
                    processed_xmls += 1
            except Exception as e_xml:
                errors.append(f"{filename}: {str(e_xml)}")

        # 3. Estado de cuenta BBVA (CSV o Excel)
        elif filename_lower.endswith(".csv") or filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls"):
            try:
                transacciones = parse_bbva_statement(content, filename, account_rfc=effective_rfc)
                for tx in transacciones:
                    existing_tx = db.query(BankTransaction).filter(BankTransaction.id_transaccion == tx["id_transaccion"]).first()
                    if not existing_tx:
                        new_tx = BankTransaction(
                            account_rfc=effective_rfc,
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
                errors.append(f"{filename}: {str(e_stmt)}")

    db.commit()

    # 4. Detonar conciliación automática filtrando por la entidad activa
    matches_creados = 0
    try:
        facturas_pendientes = db.query(CFDIInvoice).filter(
            CFDIInvoice.conciliado == False,
            CFDIInvoice.account_rfc == effective_rfc
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

        tx_pendientes = db.query(BankTransaction).filter(
            BankTransaction.status_conciliacion != "CONCILIADO",
            BankTransaction.account_rfc == effective_rfc
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
                        matches_creados += 1

            db.commit()
    except Exception as e_engine:
        errors.append(f"Error en motor de conciliación: {e_engine}")

    return {
        "success": True,
        "entity": {"rfc": effective_rfc, "name": entity_name},
        "processed_xmls": processed_xmls,
        "processed_statements": processed_statements,
        "matches_creados": matches_creados,
        "errors": errors
    }


@router.post("/match-manual")
def match_manual(
    transaction_id: int = Form(...),
    uuid_cfdi: str = Form(...),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Enlaza manualmente una transacción bancaria con un CFDI específico o aprueba una sugerencia.
    """
    tx = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada.")

    factura = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_cfdi.strip().upper()).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura CFDI no encontrada.")

    # Si la transacción ya tenía otra factura, liberar la anterior
    if tx.uuid_cfdi and tx.uuid_cfdi != factura.uuid:
        prev_f = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == tx.uuid_cfdi).first()
        if prev_f:
            prev_f.conciliado = False

    tx.uuid_cfdi = factura.uuid
    tx.status_conciliacion = "CONCILIADO"
    tx.confianza_score = 1.0
    tx.nota_revision = f"Conciliado manualmente con {factura.nombre_emisor if tx.tipo == 'EGRESO' else factura.nombre_receptor}."
    factura.conciliado = True

    db.commit()

    return {"success": True, "message": "Movimiento conciliado exitosamente."}


@router.post("/unmatch")
def unmatch_transaction(
    transaction_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Desvincula una transacción bancaria de su CFDI y devuelve la factura al pool de pendientes.
    """
    tx = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada.")

    if tx.uuid_cfdi:
        uuid_to_free = tx.uuid_cfdi
        tx.uuid_cfdi = None
        tx.status_conciliacion = "SIN_CFDI"
        tx.confianza_score = 0.0
        tx.nota_revision = "Desvinculado manualmente por el usuario."

        # Liberar la factura si no está vinculada a otra transacción
        other = db.query(BankTransaction).filter(BankTransaction.uuid_cfdi == uuid_to_free, BankTransaction.id != tx.id).first()
        if not other:
            factura = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_to_free).first()
            if factura:
                factura.conciliado = False

    db.commit()

    return {"success": True, "message": "Movimiento desvinculado exitosamente."}


@router.delete("/transactions/{transaction_id}")
def delete_bank_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Elimina un registro de transacción bancaria. Si estaba vinculado a un CFDI,
    libera la factura para que vuelva al pool de pendientes y no quede bloqueada.
    """
    tx = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada.")

    if tx.uuid_cfdi:
        uuid_to_free = tx.uuid_cfdi
        other = db.query(BankTransaction).filter(
            BankTransaction.uuid_cfdi == uuid_to_free,
            BankTransaction.id != tx.id
        ).first()
        if not other:
            factura = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_to_free).first()
            if factura:
                factura.conciliado = False

    db.delete(tx)
    db.commit()

    return {"success": True, "message": "Movimiento bancario eliminado correctamente."}


@router.post("/deduplicate")
def deduplicate_transactions(
    account_rfc: str = Query("DEGF851127TK1"),
    month: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Escanea y depura transacciones duplicadas para la entidad (y mes si se especifica).
    Conserva la transacción conciliada (con folio fiscal) o la más completa, y elimina los duplicados redundantes.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]

    query = db.query(BankTransaction).filter(BankTransaction.account_rfc == effective_rfc)
    if month:
        query = query.filter(BankTransaction.periodo_mes == month)

    txs = query.order_by(BankTransaction.fecha.asc(), BankTransaction.id.asc()).all()

    groups: Dict[str, List[BankTransaction]] = {}
    for t in txs:
        fecha_str = t.fecha.strftime("%Y-%m-%d") if t.fecha else "NODATE"
        monto_str = f"{float(t.monto or 0.0):.2f}"
        tipo_str = str(t.tipo or "").upper()
        conc_str = str(t.concepto or "").strip().upper()
        area_str = str(t.area_proyecto or "").strip().upper()
        key = f"{fecha_str}|{monto_str}|{tipo_str}|{conc_str}|{area_str}"
        groups.setdefault(key, []).append(t)

    deleted_count = 0
    for key, items in groups.items():
        if len(items) <= 1:
            continue

        # Ordenar para conservar el mejor registro:
        # 1) Aquel que tenga uuid_cfdi
        # 2) Mayor confianza_score
        # 3) Menor ID (el original)
        items_sorted = sorted(
            items,
            key=lambda x: (
                1 if x.uuid_cfdi else 0,
                x.confianza_score or 0.0,
                -x.id
            ),
            reverse=True
        )

        primary = items_sorted[0]
        duplicates = items_sorted[1:]

        for dup in duplicates:
            if dup.uuid_cfdi and not primary.uuid_cfdi:
                primary.uuid_cfdi = dup.uuid_cfdi
                primary.status_conciliacion = dup.status_conciliacion
                primary.confianza_score = dup.confianza_score
                primary.nota_revision = dup.nota_revision

            db.delete(dup)
            deleted_count += 1

    db.commit()

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"Se eliminaron {deleted_count} registros duplicados exitosamente." if deleted_count > 0 else "No se encontraron registros duplicados en este período."
    }


@router.post("/backfill-excel")
async def backfill_historical(
    file: UploadFile = File(...),
    account_rfc: str = Form("DEGF851127TK1"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Sube y procesa una hoja de cálculo con datos históricos ya conciliados (14 columnas o estándar).
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]
    content = await file.read()
    result = import_historical_excel(
        content,
        file.filename or "historico.xlsx",
        db,
        mi_rfc=effective_rfc,
        account_rfc=effective_rfc
    )
    return result


@router.post("/sync-mailbox")
def sync_mailbox(
    account_rfc: str = Query("DEGF851127TK1"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Detona la lectura y sincronización del buzón de correo dedicado vía IMAP para la entidad solicitada.
    """
    res = sync_mailbox_invoices(db, account_rfc=account_rfc)
    return res


def _get_export_user(
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Optional[UserSchema]:
    from app.main import app
    if get_current_active_user in app.dependency_overrides:
        return app.dependency_overrides[get_current_active_user]()
    if token:
        try:
            from jose import jwt
            from app.schemas.token import TokenPayload
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            token_data = TokenPayload(**payload)
            return UserSchema(id=1, email=token_data.sub or "hola@hipha.mx", full_name="Admin", is_active=True, is_superuser=True)
        except Exception:
            raise HTTPException(status_code=401, detail="Token de descarga inválido o expirado.")
    raise HTTPException(status_code=401, detail="Autenticación requerida para descargar el reporte.")


@router.get("/export/excel")
def export_excel(
    month: Optional[str] = Query(None),
    account_rfc: str = Query("DEGF851127TK1"),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[UserSchema] = Depends(_get_export_user)
):
    """
    Genera y descarga la sábana de conciliación mensual en formato Excel (.xlsx) con las 14 columnas exactas.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]
    entity_name = entity_cfg["name"]

    query = db.query(BankTransaction).filter(BankTransaction.account_rfc == effective_rfc)
    if month:
        query = query.filter(BankTransaction.periodo_mes == month)
    txs = query.order_by(desc(BankTransaction.fecha), desc(BankTransaction.id)).all()

    tx_list = []
    for t in txs:
        tx_dict = {
            "fecha": t.fecha,
            "area_proyecto": t.area_proyecto or entity_name,
            "concepto": t.concepto,
            "tipo": t.tipo,
            "tipo_categoria": t.tipo_categoria,
            "monto": t.monto,
            "status_conciliacion": t.status_conciliacion,
            "uuid_cfdi": t.uuid_cfdi,
            "nota_revision": t.nota_revision,
            "factura": t.factura
        }
        tx_list.append(tx_dict)

    excel_bytes = export_reconciliation_excel(
        tx_list,
        mes_label=month or "Consolidado",
        entity_name=entity_name
    )
    
    clean_month = (month or 'General').replace('/', '-')
    filename = f"Conciliacion_{entity_name}_{clean_month}.xlsx"
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/pdf-faltantes")
def export_pdf_faltantes(
    month: Optional[str] = Query(None),
    account_rfc: str = Query("DEGF851127TK1"),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[UserSchema] = Depends(_get_export_user)
):
    """
    Genera y descarga el reporte ejecutivo en PDF con los gastos no deducibles / faltantes de factura de la entidad.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]
    entity_name = entity_cfg["name"]

    query = db.query(BankTransaction).filter(BankTransaction.account_rfc == effective_rfc)
    if month:
        query = query.filter(BankTransaction.periodo_mes == month)
    txs = query.order_by(desc(BankTransaction.fecha), desc(BankTransaction.id)).all()

    tx_list = [{
        "fecha": t.fecha,
        "concepto": t.concepto,
        "tipo": t.tipo,
        "monto": t.monto,
        "status_conciliacion": t.status_conciliacion,
        "nota_revision": t.nota_revision
    } for t in txs]

    pdf_bytes = generate_discrepancies_pdf(
        tx_list,
        mes_label=f"{entity_name} ({effective_rfc}) - {month or 'Actual'}"
    )

    clean_month = (month or 'Actual').replace('/', '-')
    filename = f"Reporte_Faltantes_{entity_name}_{clean_month}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

