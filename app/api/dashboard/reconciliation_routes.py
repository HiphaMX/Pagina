from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query, Header
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import Optional, List, Dict, Tuple
import io
import re
import zipfile
from datetime import datetime, timedelta
from pydantic import BaseModel

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
from app.services.reconciliation.pdf_parser import parse_bank_pdf_statement, is_own_account_transfer


class UpdateTransactionProjectRequest(BaseModel):
    area_proyecto: str
    update_cfdi: bool = True


class UpdateTransactionStatusRequest(BaseModel):
    status_conciliacion: str  # "NO_APLICA", "SIN_CFDI"
    motivo: Optional[str] = None


class BatchUpdateStatusRequest(BaseModel):
    transaction_ids: List[int]
    status_conciliacion: str  # "NO_APLICA", "SIN_CFDI", "POR_REVISAR"
    motivo: Optional[str] = None
    area_proyecto: Optional[str] = None


class BatchUpdateProjectRequest(BaseModel):
    transaction_ids: List[int]
    area_proyecto: str
    update_cfdi: bool = True


class ComprobarInvoiceRequest(BaseModel):
    motivo: str


router = APIRouter()


def _find_existing_transaction(db: Session, tx: dict, effective_rfc: str) -> Optional[BankTransaction]:
    """
    Busca si una transacción bancaria ya existe en la base de datos de forma idempotente,
    verificando primero por hash id_transaccion y como respaldo por identidad de negocio
    (mismo RFC, misma fecha calendario, mismo tipo, mismo importe y coincidencia de saldo/concepto).
    """
    tx_id = tx.get("id_transaccion")
    if tx_id:
        exact = db.query(BankTransaction).filter(
            BankTransaction.id_transaccion == tx_id,
            BankTransaction.account_rfc == effective_rfc
        ).first()
        if exact:
            return exact

    tx_fecha = tx.get("fecha")
    tx_monto = tx.get("monto")
    tx_tipo = tx.get("tipo")
    if not (tx_fecha and tx_monto is not None and tx_tipo):
        return None

    if isinstance(tx_fecha, datetime):
        dia_inicio = tx_fecha.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        dia_inicio = datetime.combine(tx_fecha, datetime.min.time())
    dia_fin = dia_inicio + timedelta(days=1)

    candidates = db.query(BankTransaction).filter(
        BankTransaction.account_rfc == effective_rfc,
        BankTransaction.fecha >= dia_inicio,
        BankTransaction.fecha < dia_fin,
        BankTransaction.tipo == tx_tipo,
        func.abs(BankTransaction.monto - float(tx_monto)) <= 0.02
    ).all()

    if not candidates:
        return None

    tx_saldo = tx.get("saldo")
    tx_conc_norm = re.sub(r'[^A-Z0-9]', '', str(tx.get("concepto") or "").upper())

    for c in candidates:
        if tx_saldo is not None and c.saldo is not None:
            if abs(float(c.saldo) - float(tx_saldo)) <= 0.05:
                return c
        c_conc_norm = re.sub(r'[^A-Z0-9]', '', str(c.concepto or "").upper())
        if tx_conc_norm and c_conc_norm:
            if tx_conc_norm[:20] == c_conc_norm[:20] or tx_conc_norm in c_conc_norm or c_conc_norm in tx_conc_norm:
                return c

    if len(candidates) == 1:
        c = candidates[0]
        c_conc_norm = re.sub(r'[^A-Z0-9]', '', str(c.concepto or "").upper())
        if tx_conc_norm[:10] and tx_conc_norm[:10] == c_conc_norm[:10]:
            return c
        # Si el candidato existente proviene de sábana (saldo is None) y el entrante es de extracto bancario
        if c.saldo is None:
            return c

    return None



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

    # También incluir meses donde existan facturas CFDI
    try:
        cfdi_dates = db.query(CFDIInvoice.fecha_emision).filter(
            CFDIInvoice.account_rfc == effective_rfc
        ).all()
        for d in cfdi_dates:
            if d[0]:
                m_str = d[0].strftime("%Y-%m")
                if m_str not in available_months:
                    available_months.append(m_str)
        available_months.sort(reverse=True)
    except Exception:
        pass

    # Asegurar que el mes calendario actual esté en available_months
    current_cal_month = datetime.now().strftime("%Y-%m")
    if current_cal_month not in available_months:
        available_months.append(current_cal_month)
        available_months.sort(reverse=True)

    # Si no se pasó mes, tomar por defecto el mes actual del calendario para partir de ahí
    selected_month = month or current_cal_month

    # Filtro base por entidad y mes
    query = db.query(BankTransaction).filter(
        BankTransaction.account_rfc == effective_rfc,
        BankTransaction.periodo_mes == selected_month
    )
    all_txs = query.all()

    ingresos_txs = [t for t in all_txs if t.tipo == "INGRESO"]
    egresos_txs = [t for t in all_txs if t.tipo == "EGRESO"]

    # Separar traspasos entre cuentas propias (no computan como ingreso del negocio ni requieren CFDI)
    traspasos_ingresos = [
        t for t in ingresos_txs
        if t.status_conciliacion in ("NO_APLICA", "EXENTO") or is_own_account_transfer(t.concepto, effective_rfc)
    ]
    ingresos_comerciales = [t for t in ingresos_txs if t not in traspasos_ingresos]

    total_ingresos_banco = sum(t.monto for t in ingresos_comerciales)
    total_traspasos_ingresos = sum(t.monto for t in traspasos_ingresos)
    count_traspasos_ingresos = len(traspasos_ingresos)

    total_egresos_banco = sum(t.monto for t in egresos_txs)

    conciliados_ingresos = [t for t in ingresos_comerciales if t.status_conciliacion == "CONCILIADO"]
    conciliados_egresos = [t for t in egresos_txs if t.status_conciliacion == "CONCILIADO"]

    sin_cfdi_egresos = [t for t in egresos_txs if t.status_conciliacion == "SIN_CFDI"]
    monto_sin_cfdi = sum(t.monto for t in sin_cfdi_egresos)
    count_sin_cfdi = len(sin_cfdi_egresos)

    no_aplica_egresos = [t for t in egresos_txs if t.status_conciliacion in ("NO_APLICA", "EXENTO")]
    monto_no_aplica = sum(t.monto for t in no_aplica_egresos)
    count_no_aplica = len(no_aplica_egresos)

    monto_egresos_conciliados = sum(t.monto for t in conciliados_egresos)
    pct_egresos_facturados = round((monto_egresos_conciliados / total_egresos_banco * 100), 1) if total_egresos_banco > 0 else 0.0

    monto_ingresos_conciliados = sum(t.monto for t in conciliados_ingresos)
    pct_ingresos_facturados = round((monto_ingresos_conciliados / total_ingresos_banco * 100), 1) if total_ingresos_banco > 0 else 0.0

    # Detección de posibles movimientos duplicados en el periodo (misma fecha, mismo monto y mismo tipo)
    amount_freq = {}
    for t in all_txs:
        f_str = t.fecha.strftime("%Y-%m-%d") if t.fecha else "NODATE"
        key = (f_str, round(float(t.monto or 0.0), 2), t.tipo)
        amount_freq[key] = amount_freq.get(key, 0) + 1
    dup_txs = [t for t in all_txs if amount_freq.get((t.fecha.strftime("%Y-%m-%d") if t.fecha else "NODATE", round(float(t.monto or 0.0), 2), t.tipo), 0) > 1]
    count_posibles_duplicados = len(dup_txs)
    monto_posibles_duplicados = round(sum(t.monto for t in dup_txs), 2)

    # Mes completo: Si existen movimientos y no hay ningún egreso pendiente de CFDI
    mes_completo = bool(len(all_txs) > 0 and count_sin_cfdi == 0)

    # Facturas disponibles sin conciliar ni comprobadas fuera de banco
    facturas_disponibles_count = db.query(CFDIInvoice).filter(
        CFDIInvoice.account_rfc == effective_rfc,
        CFDIInvoice.conciliado == False,
        CFDIInvoice.comprobado == False
    ).count()

    count_facturas_comprobadas = db.query(CFDIInvoice).filter(
        CFDIInvoice.account_rfc == effective_rfc,
        CFDIInvoice.comprobado == True
    ).count()

    # -------------------------------------------------------------
    # Métricas Fiscales e IVA para el período seleccionado
    # -------------------------------------------------------------
    start_dt = None
    end_dt = None
    if selected_month:
        try:
            parts = selected_month.strip().split("-")
            y, m = int(parts[0]), int(parts[1])
            start_dt = datetime(y, m, 1)
            if m == 12:
                end_dt = datetime(y + 1, 1, 1)
            else:
                end_dt = datetime(y, m + 1, 1)
        except Exception:
            pass

    # 1. Facturas de Ingreso Cobradas (CFDI efectivamente cobrados vía banco o comprobados en el período - LIVA Art. 1-B)
    ingresos_invoices_map: Dict[str, CFDIInvoice] = {}
    if start_dt and end_dt:
        cfdis_mes_ing = db.query(CFDIInvoice).filter(
            CFDIInvoice.account_rfc == effective_rfc,
            CFDIInvoice.tipo == "INGRESO",
            (CFDIInvoice.conciliado == True) | (CFDIInvoice.comprobado == True),
            CFDIInvoice.fecha_emision >= start_dt,
            CFDIInvoice.fecha_emision < end_dt
        ).all()
        for inv in cfdis_mes_ing:
            ingresos_invoices_map[inv.uuid] = inv

    linked_ing_uuids = [t.uuid_cfdi for t in conciliados_ingresos if t.uuid_cfdi]
    if linked_ing_uuids:
        linked_cfdis = db.query(CFDIInvoice).filter(
            CFDIInvoice.uuid.in_(linked_ing_uuids),
            CFDIInvoice.account_rfc == effective_rfc
        ).all()
        for inv in linked_cfdis:
            ingresos_invoices_map[inv.uuid] = inv

    subtotal_ingresos_facturados = round(sum(float(inv.subtotal or 0.0) for inv in ingresos_invoices_map.values()), 2)
    iva_trasladado_ingresos = round(sum(float(inv.iva_trasladado or 0.0) for inv in ingresos_invoices_map.values()), 2)
    total_ingresos_facturados = round(sum(float(inv.total or 0.0) for inv in ingresos_invoices_map.values()), 2)
    count_ingresos_facturados = len(ingresos_invoices_map)

    # 2. Facturas de Egreso / Gastos Comprobados (CFDI Recibidos amparados vía banco o comprobados fuera de banco)
    egresos_invoices_map: Dict[str, CFDIInvoice] = {}
    if start_dt and end_dt:
        cfdis_mes_egr = db.query(CFDIInvoice).filter(
            CFDIInvoice.account_rfc == effective_rfc,
            CFDIInvoice.tipo == "EGRESO",
            (CFDIInvoice.comprobado == True) | (CFDIInvoice.conciliado == True),
            CFDIInvoice.fecha_emision >= start_dt,
            CFDIInvoice.fecha_emision < end_dt
        ).all()
        for inv in cfdis_mes_egr:
            egresos_invoices_map[inv.uuid] = inv

    linked_egr_uuids = [t.uuid_cfdi for t in conciliados_egresos if t.uuid_cfdi]
    if linked_egr_uuids:
        linked_egr_cfdis = db.query(CFDIInvoice).filter(
            CFDIInvoice.uuid.in_(linked_egr_uuids),
            CFDIInvoice.account_rfc == effective_rfc
        ).all()
        for inv in linked_egr_cfdis:
            egresos_invoices_map[inv.uuid] = inv

    subtotal_egresos_comprobados = round(sum(float(inv.subtotal or 0.0) for inv in egresos_invoices_map.values()), 2)
    iva_acreditable_egresos = round(sum(float(inv.iva_trasladado or 0.0) for inv in egresos_invoices_map.values()), 2)
    total_egresos_comprobados = round(sum(float(inv.total or 0.0) for inv in egresos_invoices_map.values()), 2)
    count_egresos_comprobados = len(egresos_invoices_map)

    # 3. Balance Estimado de IVA (Cobrado en Ingresos - Acreditable en Gastos Comprobados)
    balance_iva_estimado = round(iva_trasladado_ingresos - iva_acreditable_egresos, 2)

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
            "count_ingresos_banco": len(ingresos_comerciales),
            "total_ingresos_bruto": round(sum(t.monto for t in ingresos_txs), 2),
            "total_traspasos_ingresos": round(total_traspasos_ingresos, 2),
            "count_traspasos_ingresos": count_traspasos_ingresos,
            "total_egresos_banco": round(total_egresos_banco, 2),
            "count_egresos_banco": len(egresos_txs),
            "monto_sin_cfdi": round(monto_sin_cfdi, 2),
            "count_sin_cfdi": count_sin_cfdi,
            "monto_no_aplica": round(monto_no_aplica, 2),
            "count_no_aplica": count_no_aplica,
            "count_posibles_duplicados": count_posibles_duplicados,
            "monto_posibles_duplicados": round(monto_posibles_duplicados, 2),
            "mes_completo": mes_completo,
            "pct_egresos_facturados": pct_egresos_facturados,
            "pct_ingresos_facturados": pct_ingresos_facturados,
            "monto_egresos_conciliados": round(monto_egresos_conciliados, 2),
            "count_egresos_conciliados": len(conciliados_egresos),
            "monto_ingresos_conciliados": round(monto_ingresos_conciliados, 2),
            "count_ingresos_conciliados": len(conciliados_ingresos),
            "monto_conciliado": round(monto_egresos_conciliados, 2),
            "count_conciliado": len(conciliados_egresos),
            "facturas_disponibles_count": facturas_disponibles_count,
            "count_facturas_comprobadas": count_facturas_comprobadas,
            "total_transacciones": len(all_txs),
            "subtotal_ingresos_facturados": subtotal_ingresos_facturados,
            "iva_trasladado_ingresos": iva_trasladado_ingresos,
            "total_ingresos_facturados": total_ingresos_facturados,
            "count_ingresos_facturados": count_ingresos_facturados,
            "subtotal_egresos_comprobados": subtotal_egresos_comprobados,
            "iva_acreditable_egresos": iva_acreditable_egresos,
            "total_egresos_comprobados": total_egresos_comprobados,
            "count_egresos_comprobados": count_egresos_comprobados,
            "balance_iva_estimado": balance_iva_estimado
        }
    }


@router.get("/transactions")
def get_reconciliation_transactions(
    month: Optional[str] = Query(None),
    status: Optional[str] = Query("ALL"),
    tipo: Optional[str] = Query("ALL"),
    search: Optional[str] = Query(None),
    amount: Optional[float] = Query(None, description="Filtrar por cantidad exacta o aproximada ($$)"),
    only_duplicates: Optional[bool] = Query(False, description="Filtrar solo transacciones con montos duplicados en el período"),
    account_rfc: str = Query("DEGF851127TK1"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retorna la lista de transacciones bancarias del mes con datos del CFDI asociado y las 14 columnas fiscales,
    con soporte para filtrado por cantidad ($$) y detección de posibles movimientos duplicados.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]
    entity_name = entity_cfg["name"]

    # Detección de posibles duplicados en el periodo (misma fecha, mismo monto y mismo tipo)
    base_month_query = db.query(BankTransaction.id, BankTransaction.fecha, BankTransaction.monto, BankTransaction.tipo).filter(BankTransaction.account_rfc == effective_rfc)
    if month:
        base_month_query = base_month_query.filter(BankTransaction.periodo_mes == month)
    
    amount_counts = {}
    month_tx_meta = base_month_query.all()
    for (t_id, f_val, m, tip) in month_tx_meta:
        f_str = f_val.strftime("%Y-%m-%d") if f_val else "NODATE"
        key = (f_str, round(float(m or 0.0), 2), tip)
        amount_counts[key] = amount_counts.get(key, 0) + 1

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

    if amount is not None:
        query = query.filter(func.abs(BankTransaction.monto - amount) <= 0.05)

    if only_duplicates:
        dup_ids = [
            t_id for (t_id, f_val, m, tip) in month_tx_meta
            if amount_counts.get((f_val.strftime("%Y-%m-%d") if f_val else "NODATE", round(float(m or 0.0), 2), tip), 0) > 1
        ]
        if dup_ids:
            query = query.filter(BankTransaction.id.in_(dup_ids))
        else:
            return []

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
        if t.uuid_cfdi:
            cfdi_status_label = "CONCILIADO"
        elif t.status_conciliacion == "POR_REVISAR":
            cfdi_status_label = "POR REVISAR"
        elif t.status_conciliacion in ("NO_APLICA", "EXENTO"):
            cfdi_status_label = "NO REQUIERE CFDI"
        else:
            cfdi_status_label = "SIN CFDI"

        f_str = t.fecha.strftime("%Y-%m-%d") if t.fecha else "NODATE"
        m_val = round(float(t.monto or 0.0), 2)
        dup_count = amount_counts.get((f_str, m_val, t.tipo), 1)

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
            "duplicate_count": dup_count,
            "is_possible_duplicate": dup_count > 1,
            "tipo": t.tipo,
            "banco": t.banco or "BBVA",
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
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: INGRESO, EGRESO o ALL"),
    month: Optional[str] = Query(None, description="Filtrar por mes en formato YYYY-MM"),
    include_reconciled: bool = Query(False, description="Incluir facturas ya vinculadas para asociar múltiples pagos"),
    include_comprobados: bool = Query(False, description="Incluir facturas marcadas como comprobadas fuera de banco"),
    comprobado_status: Optional[str] = Query("ALL", description="Filtrar por estatus de comprobación: ALL, PENDIENTE o COMPROBADO"),
    search: Optional[str] = Query(None),
    account_rfc: str = Query("DEGF851127TK1"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retorna las facturas registradas de la entidad disponibles para conciliar o comprobar,
    con soporte para filtrado por mes, tipo, estatus de comprobación (efectivo, hipoteca, rendimientos, etc.),
    e inclusión de facturas ya vinculadas para permitir asociar múltiples pagos bancarios.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]

    query = db.query(CFDIInvoice).filter(
        CFDIInvoice.account_rfc == effective_rfc
    )

    if not include_reconciled:
        query = query.filter(CFDIInvoice.conciliado == False)

    if comprobado_status == "PENDIENTE":
        query = query.filter(CFDIInvoice.comprobado == False)
    elif comprobado_status == "COMPROBADO":
        query = query.filter(CFDIInvoice.comprobado == True)
    elif not include_comprobados:
        query = query.filter(CFDIInvoice.comprobado == False)

    if tipo and tipo != "ALL":
        query = query.filter(CFDIInvoice.tipo == tipo)

    if month:
        try:
            parts = month.strip().split("-")
            y, m = int(parts[0]), int(parts[1])
            start_dt = datetime(y, m, 1)
            if m == 12:
                end_dt = datetime(y + 1, 1, 1)
            else:
                end_dt = datetime(y, m + 1, 1)
            query = query.filter(CFDIInvoice.fecha_emision >= start_dt, CFDIInvoice.fecha_emision < end_dt)
        except Exception:
            pass

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (CFDIInvoice.nombre_emisor.ilike(s)) |
            (CFDIInvoice.nombre_receptor.ilike(s)) |
            (CFDIInvoice.rfc_emisor.ilike(s)) |
            (CFDIInvoice.rfc_receptor.ilike(s)) |
            (CFDIInvoice.uuid.ilike(s))
        )

    invoices = query.order_by(desc(CFDIInvoice.fecha_emision)).limit(150).all()

    # Precalcular montos vinculados para facturas retornadas
    inv_uuids = [inv.uuid for inv in invoices]
    linked_tx_map: Dict[str, List[BankTransaction]] = {}
    if inv_uuids:
        all_linked = db.query(BankTransaction).filter(
            BankTransaction.uuid_cfdi.in_(inv_uuids),
            BankTransaction.account_rfc == effective_rfc
        ).all()
        for t in all_linked:
            linked_tx_map.setdefault(t.uuid_cfdi, []).append(t)

    results = []
    for inv in invoices:
        txs_for_inv = linked_tx_map.get(inv.uuid, [])
        monto_vinculado = round(sum(float(t.monto or 0) for t in txs_for_inv), 2)
        total_inv = float(inv.total or 0)
        saldo_pendiente = max(0.0, round(total_inv - monto_vinculado, 2))

        results.append({
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
            "conceptos_resumen": inv.conceptos_resumen,
            "conciliado": inv.conciliado,
            "comprobado": bool(getattr(inv, "comprobado", False)),
            "motivo_comprobacion": getattr(inv, "motivo_comprobacion", None) or "",
            "monto_vinculado": monto_vinculado,
            "saldo_pendiente": saldo_pendiente,
            "pagos_vinculados_count": len(txs_for_inv)
        })

    return results


def _run_reconciliation_pass(
    db: Session,
    effective_rfc: str,
    entity_name: str,
    periodo_mes: Optional[str] = None
) -> int:
    """
    Ejecuta el motor de conciliación avanzada sobre las facturas pendientes y movimientos
    bancarios pendientes de la entidad:
    - Extrae método de pago, conceptos y documentos relacionados de complementos de pago.
    - Soporta matches 1:1 con ventana comercial flexible para transferencias de crédito.
    - Soporta pagos consolidados (1 depósito ampara 2 o 3 facturas).
    - Marca como conciliadas tanto las transacciones como todas las facturas hijas y consolidadas.
    """
    facturas_query = db.query(CFDIInvoice).filter(
        CFDIInvoice.conciliado == False,
        CFDIInvoice.comprobado == False,
        CFDIInvoice.account_rfc == effective_rfc
    )
    facturas_pendientes = facturas_query.all()
    facturas_dict = []
    for f in facturas_pendientes:
        f_item = {
            "uuid": f.uuid,
            "tipo": f.tipo,
            "rfc_emisor": f.rfc_emisor,
            "nombre_emisor": f.nombre_emisor,
            "rfc_receptor": f.rfc_receptor,
            "nombre_receptor": f.nombre_receptor,
            "fecha_emision": f.fecha_emision,
            "subtotal": f.subtotal,
            "iva": f.iva_trasladado,
            "total": f.total,
            "metodo_pago": f.metodo_pago,
            "conceptos_resumen": f.conceptos_resumen,
            "doctos_relacionados": []
        }
        if f.metodo_pago == "PAGO" and f.xml_raw:
            try:
                rep_data = parse_cfdi_xml(f.xml_raw.encode("utf-8"), mi_rfc=effective_rfc)
                f_item["doctos_relacionados"] = rep_data.get("doctos_relacionados", [])
            except Exception:
                pass
        facturas_dict.append(f_item)

    tx_query = db.query(BankTransaction).filter(
        BankTransaction.status_conciliacion.notin_(["CONCILIADO", "NO_APLICA", "EXENTO"]),
        BankTransaction.account_rfc == effective_rfc
    )
    if periodo_mes:
        tx_query = tx_query.filter(BankTransaction.periodo_mes == periodo_mes)
    tx_pendientes = tx_query.all()

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

    matches_creados = 0
    if facturas_dict and tx_list:
        conciliados = conciliar_movimientos(tx_list, facturas_dict)
        for res in conciliados:
            db_tx = db.query(BankTransaction).filter(BankTransaction.id_transaccion == res["id_transaccion"]).first()
            if not db_tx:
                continue
            if res.get("uuid_cfdi"):
                db_tx.uuid_cfdi = res["uuid_cfdi"]
                db_tx.status_conciliacion = res["status_conciliacion"]
                db_tx.confianza_score = res["confianza_score"]
                db_tx.nota_revision = res["nota_revision"]

                if res["status_conciliacion"] == "CONCILIADO":
                    db_f = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == res["uuid_cfdi"]).first()
                    if db_f:
                        db_f.conciliado = True
                    for rel_uuid in res.get("related_cfdi_uuids", []):
                        if rel_uuid and rel_uuid != res["uuid_cfdi"]:
                            rel_f = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == rel_uuid).first()
                            if rel_f:
                                rel_f.conciliado = True
                    matches_creados += 1
            else:
                if res.get("status_conciliacion") in ("NO_APLICA", "EXENTO"):
                    db_tx.status_conciliacion = res["status_conciliacion"]
                    db_tx.confianza_score = res["confianza_score"]
                    db_tx.nota_revision = res["nota_revision"]
                elif res.get("area_proyecto") and (not db_tx.area_proyecto or db_tx.area_proyecto in [entity_name, "General"]):
                    db_tx.area_proyecto = res["area_proyecto"]
                if res.get("nota_revision") and not db_tx.nota_revision:
                    db_tx.nota_revision = res["nota_revision"]
        db.commit()
    return matches_creados


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
    detected_months = set()

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
                                if cfdi_data.get("fecha_emision"):
                                    detected_months.add(cfdi_data["fecha_emision"].strftime("%Y-%m"))
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
                                else:
                                    if cfdi_data["total"] > 0 and (existing.total == 0 or existing.total != cfdi_data["total"]):
                                        existing.total = cfdi_data["total"]
                                    if cfdi_data.get("subtotal", 0.0) > 0 and existing.subtotal == 0:
                                        existing.subtotal = cfdi_data["subtotal"]
                                    if cfdi_data.get("metodo_pago") and existing.metodo_pago != cfdi_data["metodo_pago"]:
                                        existing.metodo_pago = cfdi_data["metodo_pago"]
                                    if cfdi_data.get("tipo") and existing.tipo != cfdi_data["tipo"]:
                                        existing.tipo = cfdi_data["tipo"]
                                    if cfdi_data.get("conceptos_resumen") and existing.conceptos_resumen != cfdi_data["conceptos_resumen"]:
                                        existing.conceptos_resumen = cfdi_data["conceptos_resumen"]
                                    if not existing.xml_raw:
                                        existing.xml_raw = xml_bytes.decode("utf-8", errors="ignore")
                            except Exception as e_zip_xml:
                                errors.append(f"{zip_info.filename}: {str(e_zip_xml)}")
            except Exception as e_zip:
                errors.append(f"Error abriendo ZIP {filename}: {str(e_zip)}")

        # 2. Archivo XML individual
        elif filename_lower.endswith(".xml"):
            try:
                cfdi_data = parse_cfdi_xml(content, mi_rfc=effective_rfc)
                if cfdi_data.get("fecha_emision"):
                    detected_months.add(cfdi_data["fecha_emision"].strftime("%Y-%m"))
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
                else:
                    if cfdi_data["total"] > 0 and (existing.total == 0 or existing.total != cfdi_data["total"]):
                        existing.total = cfdi_data["total"]
                    if cfdi_data.get("subtotal", 0.0) > 0 and existing.subtotal == 0:
                        existing.subtotal = cfdi_data["subtotal"]
                    if cfdi_data.get("metodo_pago") and existing.metodo_pago != cfdi_data["metodo_pago"]:
                        existing.metodo_pago = cfdi_data["metodo_pago"]
                    if cfdi_data.get("tipo") and existing.tipo != cfdi_data["tipo"]:
                        existing.tipo = cfdi_data["tipo"]
                    if cfdi_data.get("conceptos_resumen") and existing.conceptos_resumen != cfdi_data["conceptos_resumen"]:
                        existing.conceptos_resumen = cfdi_data["conceptos_resumen"]
                    if not existing.xml_raw:
                        existing.xml_raw = content.decode("utf-8", errors="ignore")
            except Exception as e_xml:
                errors.append(f"{filename}: {str(e_xml)}")

        # 3. Estado de cuenta BBVA (CSV o Excel) o Sábana contable
        elif filename_lower.endswith(".csv") or filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls"):
            is_sabana = False
            try:
                snippet = content[:2048].decode("utf-8", errors="ignore").upper()
                if any(k in snippet for k in ["FOLIO FISCAL", "AREA/PROYECTO", "CLIENTE/PROVEEDOR", "IVA INGRESOS", "IVA EGR"]):
                    is_sabana = True
            except Exception:
                pass

            if is_sabana:
                try:
                    res_bf = import_historical_excel(content, filename, db, mi_rfc=effective_rfc)
                    st_cnt = res_bf.get("transacciones_importadas", 0) or res_bf.get("imported_transactions", 0)
                    inv_cnt = res_bf.get("facturas_importadas", 0) or res_bf.get("imported_invoices", 0)
                    processed_statements += st_cnt
                    processed_xmls += inv_cnt
                    if res_bf.get("meses_afectados"):
                        detected_months.update(res_bf["meses_afectados"])
                except Exception as e_bf:
                    errors.append(f"{filename} (sábana): {str(e_bf)}")
            else:
                try:
                    transacciones = parse_bbva_statement(content, filename, account_rfc=effective_rfc)
                    for tx in transacciones:
                        detected_months.add(tx["periodo_mes"])
                        existing_tx = _find_existing_transaction(db, tx, effective_rfc)
                        is_own = is_own_account_transfer(tx.get("concepto", ""), account_rfc=effective_rfc)
                        status_init = "NO_APLICA" if is_own else "SIN_CFDI"
                        nota_init = "Traspaso entre Cuentas Propias" if is_own else "Transacción bancaria sin CFDI registrado en el período."
                        area_init = "DELGADILLO MEDINA" if is_own else entity_name

                        if not existing_tx:
                            new_tx = BankTransaction(
                                account_rfc=effective_rfc,
                                area_proyecto=area_init,
                                tipo_categoria="INGRESO" if tx["tipo"] == "INGRESO" else "GASTO",
                                id_transaccion=tx["id_transaccion"],
                                banco=tx["banco"],
                                fecha=tx["fecha"],
                                concepto=tx["concepto"],
                                monto=tx["monto"],
                                tipo=tx["tipo"],
                                saldo=tx.get("saldo"),
                                status_conciliacion=status_init,
                                nota_revision=nota_init,
                                confianza_score=1.0 if is_own else 0.0,
                                periodo_mes=tx["periodo_mes"]
                            )
                            db.add(new_tx)
                            processed_statements += 1
                        else:
                            if is_own and existing_tx.status_conciliacion in ("SIN_CFDI", "POR_REVISAR"):
                                existing_tx.status_conciliacion = "NO_APLICA"
                                existing_tx.nota_revision = "Traspaso entre Cuentas Propias"
                                existing_tx.area_proyecto = "DELGADILLO MEDINA"
                                existing_tx.confianza_score = 1.0
                            if existing_tx.saldo is None and tx.get("saldo") is not None:
                                existing_tx.saldo = tx.get("saldo")
                                if tx.get("concepto") and existing_tx.concepto != tx["concepto"]:
                                    if not existing_tx.nota_revision:
                                        existing_tx.nota_revision = f"Sábana: {existing_tx.concepto}"
                                    existing_tx.concepto = tx["concepto"]
                            processed_statements += 1
                except Exception as e_stmt:
                    errors.append(f"{filename}: {str(e_stmt)}")

        # 4. Estado de cuenta o comprobante bancario en PDF
        elif filename_lower.endswith(".pdf"):
            try:
                transacciones = parse_bank_pdf_statement(content, filename, account_rfc=effective_rfc)
                for tx in transacciones:
                    detected_months.add(tx["periodo_mes"])
                    existing_tx = _find_existing_transaction(db, tx, effective_rfc)
                    is_own = is_own_account_transfer(tx.get("concepto", ""), account_rfc=effective_rfc)
                    status_init = "NO_APLICA" if is_own else (tx.get("status_conciliacion") or "SIN_CFDI")
                    nota_init = "Traspaso entre Cuentas Propias" if is_own else (tx.get("nota_revision") or "Transacción bancaria sin CFDI registrado en el período.")
                    area_init = "DELGADILLO MEDINA" if is_own else (tx.get("area_proyecto") or entity_name)

                    if not existing_tx:
                        new_tx = BankTransaction(
                            account_rfc=tx["account_rfc"],
                            area_proyecto=area_init,
                            tipo_categoria="INGRESO" if tx["tipo"] == "INGRESO" else "GASTO",
                            id_transaccion=tx["id_transaccion"],
                            banco=tx["banco"],
                            fecha=tx["fecha"],
                            concepto=tx["concepto"],
                            monto=tx["monto"],
                            tipo=tx["tipo"],
                            saldo=tx.get("saldo"),
                            status_conciliacion=status_init,
                            nota_revision=nota_init,
                            confianza_score=1.0 if is_own else 0.0,
                            periodo_mes=tx["periodo_mes"]
                        )
                        db.add(new_tx)
                        processed_statements += 1
                    else:
                        if is_own and existing_tx.status_conciliacion in ("SIN_CFDI", "POR_REVISAR"):
                            existing_tx.status_conciliacion = "NO_APLICA"
                            existing_tx.nota_revision = "Traspaso entre Cuentas Propias"
                            existing_tx.area_proyecto = "DELGADILLO MEDINA"
                            existing_tx.confianza_score = 1.0
                        else:
                            if tx.get("area_proyecto") and (not existing_tx.area_proyecto or existing_tx.area_proyecto == entity_name):
                                existing_tx.area_proyecto = tx["area_proyecto"]
                            if tx.get("nota_revision") and not existing_tx.nota_revision:
                                existing_tx.nota_revision = tx["nota_revision"]
                        if existing_tx.saldo is None and tx.get("saldo") is not None:
                            existing_tx.saldo = tx.get("saldo")
                            if tx.get("concepto") and existing_tx.concepto != tx["concepto"]:
                                if not existing_tx.nota_revision:
                                    existing_tx.nota_revision = f"Sábana: {existing_tx.concepto}"
                                existing_tx.concepto = tx["concepto"]
                        processed_statements += 1
            except Exception as e_pdf:
                errors.append(f"{filename} (PDF bancario): {str(e_pdf)}")

    db.commit()

    # 4. Detonar conciliación automática filtrando por la entidad activa
    matches_creados = 0
    try:
        matches_creados = _run_reconciliation_pass(db, effective_rfc, entity_name)
    except Exception as e_engine:
        errors.append(f"Error en motor de conciliación: {e_engine}")

    return {
        "success": True,
        "entity": {"rfc": effective_rfc, "name": entity_name},
        "processed_xmls": processed_xmls,
        "processed_statements": processed_statements,
        "matches_creados": matches_creados,
        "detected_months": sorted(list(detected_months), reverse=True),
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
    Soporta vincular múltiples transacciones a una misma factura y alinea automáticamente
    el tipo de flujo si el movimiento bancario fue clasificado con la dirección opuesta.
    """
    tx = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada.")

    factura = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_cfdi.strip().upper()).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura CFDI no encontrada.")

    # Si la transacción ya tenía otra factura, liberar la anterior si nadie más la usa
    if tx.uuid_cfdi and tx.uuid_cfdi != factura.uuid:
        prev_uuid = tx.uuid_cfdi
        prev_f = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == prev_uuid).first()
        if prev_f:
            other_tx = db.query(BankTransaction).filter(
                BankTransaction.uuid_cfdi == prev_uuid,
                BankTransaction.id != tx.id
            ).first()
            if not other_tx:
                prev_f.conciliado = False

    # Alinear tipo de flujo contable si difiere
    if tx.tipo != factura.tipo:
        tx.tipo = factura.tipo
        if tx.tipo == "INGRESO":
            tx.ingresos = tx.monto
            tx.egresos = 0.0
            tx.tipo_categoria = "INGRESO"
        else:
            tx.egresos = tx.monto
            tx.ingresos = 0.0
            tx.tipo_categoria = "GASTO"

    tx.uuid_cfdi = factura.uuid
    tx.status_conciliacion = "CONCILIADO"
    tx.confianza_score = 1.0
    tx.contraparte = factura.nombre_receptor if tx.tipo == "INGRESO" else factura.nombre_emisor
    tx.nota_revision = f"Conciliado manualmente con {tx.contraparte}."

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


@router.patch("/transactions/{transaction_id}/project")
def update_transaction_project(
    transaction_id: int,
    payload: UpdateTransactionProjectRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Actualiza el proyecto o área asignada a una transacción bancaria y, opcionalmente,
    a la factura CFDI que tenga vinculada.
    """
    tx = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada.")

    new_project = payload.area_proyecto.strip()
    tx.area_proyecto = new_project

    if payload.update_cfdi and tx.uuid_cfdi:
        factura = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == tx.uuid_cfdi).first()
        if factura:
            factura.area_proyecto = new_project

    db.commit()
    db.refresh(tx)

    return {
        "success": True,
        "message": f"Proyecto actualizado a '{new_project}' exitosamente.",
        "transaction_id": tx.id,
        "area_proyecto": tx.area_proyecto
    }


@router.patch("/transactions/{transaction_id}/status")
def update_transaction_status(
    transaction_id: int,
    payload: UpdateTransactionStatusRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Actualiza el estatus de conciliación de una transacción bancaria.
    Permite marcar movimientos como NO_APLICA (ej. Traspasos entre cuentas,
    pago de impuestos al SAT, liquidación de saldo de tarjeta de crédito) para que
    no compute como faltante y permita activar el Check de Mes Completo.
    """
    tx = db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada.")

    target_status = payload.status_conciliacion.upper().strip()
    if target_status not in ("NO_APLICA", "SIN_CFDI", "POR_REVISAR"):
        raise HTTPException(status_code=400, detail="Estatus no válido para actualización manual.")

    if target_status == "NO_APLICA":
        # Si estaba vinculada a una factura, desvincularla para no dejarla bloqueada
        if tx.uuid_cfdi:
            uuid_to_free = tx.uuid_cfdi
            tx.uuid_cfdi = None
            other = db.query(BankTransaction).filter(
                BankTransaction.uuid_cfdi == uuid_to_free,
                BankTransaction.id != tx.id
            ).first()
            if not other:
                factura = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_to_free).first()
                if factura:
                    factura.conciliado = False

        tx.status_conciliacion = "NO_APLICA"
        if payload.motivo:
            tx.nota_revision = payload.motivo.strip()
    elif target_status == "SIN_CFDI":
        tx.status_conciliacion = "SIN_CFDI"
        # Limpiar nota si era un motivo de exención
        if tx.nota_revision and any(k in tx.nota_revision.lower() for k in ["impuesto", "traspaso", "tarjeta", "no aplica", "no deducible"]):
            tx.nota_revision = None

    db.commit()
    db.refresh(tx)

    return {
        "success": True,
        "message": f"Estatus actualizado a '{tx.status_conciliacion}' exitosamente.",
        "transaction_id": tx.id,
        "status_conciliacion": tx.status_conciliacion,
        "nota_revision": tx.nota_revision
    }


@router.post("/transactions/batch-status")
def batch_update_transaction_status(
    payload: BatchUpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Actualiza el estatus de conciliación y justificación en lote para múltiples transacciones bancarias.
    Permite marcar con 1 clic múltiples gastos como NO_APLICA (ej. Gasto Personal / DELGADILLO MEDINA).
    """
    if not payload.transaction_ids:
        raise HTTPException(status_code=400, detail="No se proporcionaron transacciones para actualizar.")

    target_status = payload.status_conciliacion.upper().strip()
    if target_status not in ("NO_APLICA", "SIN_CFDI", "POR_REVISAR"):
        raise HTTPException(status_code=400, detail="Estatus no válido para actualización manual.")

    txs = db.query(BankTransaction).filter(BankTransaction.id.in_(payload.transaction_ids)).all()
    if not txs:
        raise HTTPException(status_code=404, detail="No se encontraron transacciones con los IDs especificados.")

    updated_count = 0
    motivo_clean = payload.motivo.strip() if payload.motivo else None
    new_area = payload.area_proyecto.strip() if payload.area_proyecto else None

    # Si el motivo es gasto personal o menciona Delgadillo Medina y no se especificó proyecto, auto-asignar DELGADILLO MEDINA
    if motivo_clean and any(k in motivo_clean.lower() for k in ["personal", "delgadillo", "medina"]) and not new_area:
        new_area = "DELGADILLO MEDINA"

    for tx in txs:
        if target_status == "NO_APLICA":
            # Desvincular factura asociada si la tenía
            if tx.uuid_cfdi:
                uuid_to_free = tx.uuid_cfdi
                tx.uuid_cfdi = None
                other = db.query(BankTransaction).filter(
                    BankTransaction.uuid_cfdi == uuid_to_free,
                    BankTransaction.id != tx.id
                ).first()
                if not other:
                    factura = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_to_free).first()
                    if factura:
                        factura.conciliado = False

            tx.status_conciliacion = "NO_APLICA"
            if motivo_clean:
                tx.nota_revision = motivo_clean
            if new_area:
                tx.area_proyecto = new_area
            updated_count += 1

        elif target_status == "SIN_CFDI":
            tx.status_conciliacion = "SIN_CFDI"
            if tx.nota_revision and any(k in tx.nota_revision.lower() for k in ["impuesto", "traspaso", "tarjeta", "no aplica", "no deducible", "personal"]):
                tx.nota_revision = None
            if new_area:
                tx.area_proyecto = new_area
            updated_count += 1

        elif target_status == "POR_REVISAR":
            tx.status_conciliacion = "POR_REVISAR"
            if motivo_clean:
                tx.nota_revision = motivo_clean
            if new_area:
                tx.area_proyecto = new_area
            updated_count += 1

    db.commit()

    return {
        "success": True,
        "updated_count": updated_count,
        "status_conciliacion": target_status,
        "area_proyecto": new_area,
        "message": f"Se actualizaron {updated_count} transacciones exitosamente."
    }


@router.post("/transactions/batch-project")
def batch_update_transaction_project(
    payload: BatchUpdateProjectRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Actualiza el proyecto / área en lote para múltiples transacciones bancarias.
    """
    if not payload.transaction_ids:
        raise HTTPException(status_code=400, detail="No se proporcionaron transacciones para actualizar.")

    new_project = payload.area_proyecto.strip()
    if not new_project:
        raise HTTPException(status_code=400, detail="El nombre del proyecto no puede estar vacío.")

    txs = db.query(BankTransaction).filter(BankTransaction.id.in_(payload.transaction_ids)).all()
    if not txs:
        raise HTTPException(status_code=404, detail="No se encontraron transacciones con los IDs especificados.")

    updated_count = 0
    for tx in txs:
        tx.area_proyecto = new_project
        if payload.update_cfdi and tx.uuid_cfdi:
            factura = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == tx.uuid_cfdi).first()
            if factura:
                factura.area_proyecto = new_project
        updated_count += 1

    db.commit()

    return {
        "success": True,
        "updated_count": updated_count,
        "area_proyecto": new_project,
        "message": f"Se actualizó el proyecto a '{new_project}' para {updated_count} transacciones."
    }


@router.post("/deduplicate")
def deduplicate_transactions(
    account_rfc: str = Query("DEGF851127TK1"),
    month: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Escanea, reclasifica depósitos mal categorizados, corrige desfases de periodo
    y depura transacciones duplicadas para la entidad.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]

    # 1. Reclasificar depósitos que hayan sido marcados por error como EGRESO debido a layouts de PDF
    all_txs = db.query(BankTransaction).filter(BankTransaction.account_rfc == effective_rfc).all()
    reclassified_count = 0
    periods_fixed = 0

    for t in all_txs:
        conc_up = str(t.concepto or "").upper()
        is_deposito = any(k in conc_up for k in [
            "DEPOSITO DE TERCERO", "DEPOSITO EN EFECTIVO", "DEPOSITO POR SPEI",
            "ABONO POR LIQUIDACION", "ABONO DE INTERESES"
        ])
        if is_deposito and t.tipo == "EGRESO":
            t.tipo = "INGRESO"
            t.tipo_categoria = "INGRESO"
            reclassified_count += 1

        # 2. Corregir periodo_mes si la fecha real no coincide (excepto TC Mercado Pago que va por corte mensual)
        if t.fecha and t.banco != "TC MERCADO PAGO":
            real_period = t.fecha.strftime("%Y-%m")
            if t.periodo_mes != real_period:
                t.periodo_mes = real_period
                periods_fixed += 1

    db.commit()

    # 3. Deduplicación inteligente
    query = db.query(BankTransaction).filter(BankTransaction.account_rfc == effective_rfc)
    if month:
        query = query.filter(BankTransaction.periodo_mes == month)

    txs = query.order_by(BankTransaction.fecha.asc(), BankTransaction.id.asc()).all()

    # Agrupar transacciones por fecha (día), monto y tipo
    day_groups: Dict[Tuple[str, str, str], List[BankTransaction]] = {}
    for t in txs:
        fecha_str = t.fecha.strftime("%Y-%m-%d") if t.fecha else "NODATE"
        monto_str = f"{float(t.monto or 0.0):.2f}"
        tipo_str = str(t.tipo or "").upper()
        key = (fecha_str, monto_str, tipo_str)
        day_groups.setdefault(key, []).append(t)

    deleted_count = 0
    for (fecha_str, monto_str, tipo_str), items in day_groups.items():
        if len(items) <= 1:
            continue

        # Separar transacciones oficiales de extracto bancario (con saldo) y transacciones de sábana/histórico (sin saldo)
        bank_txs = [x for x in items if x.saldo is not None]
        sabana_txs = [x for x in items if x.saldo is None]

        # Caso A: Fusión cross-source (Banco oficial vs Sábana)
        if bank_txs and sabana_txs:
            used_bank_ids = set()
            for s_tx in list(sabana_txs):
                best_bank = None
                for b_tx in bank_txs:
                    if b_tx.id in used_bank_ids:
                        continue
                    best_bank = b_tx
                    break

                if best_bank:
                    used_bank_ids.add(best_bank.id)
                    # Transferir metadatos de la sábana al registro bancario oficial
                    if s_tx.area_proyecto:
                        best_bank.area_proyecto = s_tx.area_proyecto
                    if s_tx.tipo_categoria and not best_bank.tipo_categoria:
                        best_bank.tipo_categoria = s_tx.tipo_categoria
                    if s_tx.uuid_cfdi and not best_bank.uuid_cfdi:
                        best_bank.uuid_cfdi = s_tx.uuid_cfdi
                        best_bank.status_conciliacion = s_tx.status_conciliacion or "CONCILIADO"
                        best_bank.confianza_score = s_tx.confianza_score or 1.0
                        best_bank.nota_revision = s_tx.nota_revision or "Conciliado con folio fiscal histórico (sábana)."
                    elif s_tx.concepto and not best_bank.nota_revision:
                        best_bank.nota_revision = f"Sábana: {s_tx.concepto}"

                    db.delete(s_tx)
                    deleted_count += 1
                    sabana_txs.remove(s_tx)

        # Caso B: Duplicados entre sábanas (ambos sin saldo)
        if len(sabana_txs) > 1:
            s_subgroups: Dict[str, List[BankTransaction]] = {}
            for st in sabana_txs:
                c_norm = re.sub(r'[^A-Z0-9]', '', str(st.concepto or "").upper())[:25]
                s_subgroups.setdefault(c_norm, []).append(st)

            for c_norm, s_items in s_subgroups.items():
                if len(s_items) > 1:
                    s_sorted = sorted(
                        s_items,
                        key=lambda x: (1 if x.uuid_cfdi else 0, x.confianza_score or 0.0, -x.id),
                        reverse=True
                    )
                    s_primary = s_sorted[0]
                    for s_dup in s_sorted[1:]:
                        if s_dup.uuid_cfdi and not s_primary.uuid_cfdi:
                            s_primary.uuid_cfdi = s_dup.uuid_cfdi
                            s_primary.status_conciliacion = s_dup.status_conciliacion
                            s_primary.confianza_score = s_dup.confianza_score
                            s_primary.nota_revision = s_dup.nota_revision
                        db.delete(s_dup)
                        deleted_count += 1

        # Caso C: Duplicados idénticos en banco (mismo saldo y concepto o mismo id_transaccion)
        if len(bank_txs) > 1:
            b_subgroups: Dict[Tuple[str, str], List[BankTransaction]] = {}
            for bt in bank_txs:
                s_val = f"{float(bt.saldo or 0.0):.2f}"
                c_norm = re.sub(r'[^A-Z0-9]', '', str(bt.concepto or "").upper())[:25]
                b_subgroups.setdefault((s_val, c_norm), []).append(bt)

            for (s_val, c_norm), b_items in b_subgroups.items():
                if len(b_items) > 1:
                    b_sorted = sorted(
                        b_items,
                        key=lambda x: (1 if x.uuid_cfdi else 0, x.confianza_score or 0.0, -x.id),
                        reverse=True
                    )
                    b_primary = b_sorted[0]
                    for b_dup in b_sorted[1:]:
                        if b_dup.uuid_cfdi and not b_primary.uuid_cfdi:
                            b_primary.uuid_cfdi = b_dup.uuid_cfdi
                            b_primary.status_conciliacion = b_dup.status_conciliacion
                            b_primary.confianza_score = b_dup.confianza_score
                            b_primary.nota_revision = b_dup.nota_revision
                        db.delete(b_dup)
                        deleted_count += 1

    db.commit()

    # 4. Detonar conciliación automática para emparejar movimientos corregidos
    matches_creados = 0
    try:
        matches_creados = _run_reconciliation_pass(db, effective_rfc, entity_name, periodo_mes=month)
    except Exception as e_recon:
        print(f"Error en conciliación automática tras deduplicar: {e_recon}")

    msg_parts = []
    if reclassified_count > 0:
        msg_parts.append(f"{reclassified_count} depósitos reclasificados")
    if periods_fixed > 0:
        msg_parts.append(f"{periods_fixed} periodos corregidos")
    if deleted_count > 0:
        msg_parts.append(f"{deleted_count} duplicados eliminados")
    if matches_creados > 0:
        msg_parts.append(f"{matches_creados} facturas conciliadas")

    msg = f"Optimización completada: {', '.join(msg_parts)}." if msg_parts else "Registros al día, no se requirieron correcciones."

    return {
        "success": True,
        "deleted_count": deleted_count,
        "reclassified_count": reclassified_count,
        "periods_fixed": periods_fixed,
        "matches_creados": matches_creados,
        "message": msg
    }


@router.post("/reprocess")
def reprocess_entity_reconciliation(
    account_rfc: str = Query("MEHA850118Q96", description="RFC de la entidad: DEGF851127TK1 o MEHA850118Q96"),
    year: Optional[str] = Query(None, description="Año opcional a reprocesar (ej. '2026')"),
    month: Optional[str] = Query(None, description="Mes opcional a reprocesar (ej. '2026-03')"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Reprocesa de forma integral todas las facturas XML y estados de cuenta de la entidad:
    1. Re-analiza los XMLs almacenados (xml_raw) actualizando montos de Complementos de Pago (REPs),
       reclasificando Nóminas como EGRESO y enriqueciendo conceptos/doctos relacionados.
    2. Reclasifica depósitos bancarios marcados como EGRESO y corrige periodos desfasados.
    3. Resetea conciliaciones automáticas previas para permitir un emparejamiento limpio de punta a punta.
    4. Ejecuta el motor avanzado de conciliación (coincidencias 1:1, complementos de pago y pagos consolidados).
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]
    entity_name = entity_cfg["name"]

    # 1. Re-procesar facturas CFDI con xml_raw
    inv_query = db.query(CFDIInvoice).filter(CFDIInvoice.account_rfc == effective_rfc)
    all_invs = inv_query.all()
    invoices_reparsed = 0
    zeros_fixed = 0
    nominas_reclassified = 0

    for inv in all_invs:
        if inv.xml_raw:
            try:
                cfdi_data = parse_cfdi_xml(inv.xml_raw.encode("utf-8"), mi_rfc=effective_rfc)
                old_total = inv.total or 0.0
                new_total = cfdi_data.get("total", 0.0)

                if old_total == 0.0 and new_total > 0:
                    zeros_fixed += 1

                if inv.tipo != cfdi_data["tipo"]:
                    if cfdi_data["tipo"] == "EGRESO" and cfdi_data.get("es_nomina"):
                        nominas_reclassified += 1

                inv.total = new_total
                inv.subtotal = cfdi_data.get("subtotal", 0.0)
                inv.iva_trasladado = cfdi_data.get("iva_trasladado", 0.0)
                inv.retencion_isr = cfdi_data.get("retencion_isr", 0.0)
                inv.retencion_iva = cfdi_data.get("retencion_iva", 0.0)
                inv.retenciones = cfdi_data.get("retenciones", 0.0)
                inv.metodo_pago = cfdi_data.get("metodo_pago")
                inv.forma_pago = cfdi_data.get("forma_pago")
                inv.tipo = cfdi_data["tipo"]
                if cfdi_data.get("conceptos_resumen"):
                    inv.conceptos_resumen = cfdi_data["conceptos_resumen"]

                # Reset conciliado flag si no está comprobada manualmente
                if not inv.comprobado:
                    inv.conciliado = False

                invoices_reparsed += 1
            except Exception:
                pass
        else:
            if not inv.comprobado:
                inv.conciliado = False

    # 2. Reclasificar y limpiar transacciones bancarias
    tx_query = db.query(BankTransaction).filter(BankTransaction.account_rfc == effective_rfc)
    if month:
        tx_query = tx_query.filter(BankTransaction.periodo_mes == month)
    elif year:
        tx_query = tx_query.filter(BankTransaction.periodo_mes.startswith(f"{year}-"))

    all_txs = tx_query.all()
    deposits_reclassified = 0
    periods_fixed = 0

    for tx in all_txs:
        conc_up = str(tx.concepto or "").upper()
        is_deposito = any(k in conc_up for k in [
            "DEPOSITO DE TERCERO", "DEPOSITO EN EFECTIVO", "DEPOSITO POR SPEI",
            "ABONO POR LIQUIDACION", "ABONO DE INTERESES"
        ])
        if is_deposito and tx.tipo == "EGRESO":
            tx.tipo = "INGRESO"
            tx.tipo_categoria = "INGRESO"
            deposits_reclassified += 1

        if tx.fecha and tx.banco != "TC MERCADO PAGO":
            real_period = tx.fecha.strftime("%Y-%m")
            if tx.periodo_mes != real_period:
                tx.periodo_mes = real_period
                periods_fixed += 1

        is_own = is_own_account_transfer(tx.concepto, account_rfc=effective_rfc)
        if is_own:
            tx.status_conciliacion = "NO_APLICA"
            tx.nota_revision = "Traspaso entre Cuentas Propias"
            tx.confianza_score = 1.0
        else:
            tx.status_conciliacion = "SIN_CFDI"
            tx.uuid_cfdi = None
            tx.confianza_score = 0.0

    db.commit()

    # 3. Ejecutar pasada integral del motor de conciliación
    matches_creados = _run_reconciliation_pass(db, effective_rfc, entity_name, periodo_mes=month)

    # 4. Estadísticas finales
    total_txs = len(all_txs)
    total_conciliados = db.query(BankTransaction).filter(
        BankTransaction.account_rfc == effective_rfc,
        BankTransaction.status_conciliacion == "CONCILIADO"
    ).count()

    msg = (
        f"Reprocesamiento exitoso para {entity_name}: {invoices_reparsed} facturas analizadas "
        f"({zeros_fixed} complementos de pago con monto asignado, {nominas_reclassified} nóminas a egreso), "
        f"{deposits_reclassified} depósitos reclasificados. Se lograron {matches_creados} conciliaciones automáticas "
        f"({total_conciliados} de {total_txs} transacciones ahora en estatus CONCILIADO)."
    )

    return {
        "success": True,
        "entity": {"rfc": effective_rfc, "name": entity_name},
        "invoices_reparsed": invoices_reparsed,
        "zeros_fixed": zeros_fixed,
        "nominas_reclassified": nominas_reclassified,
        "deposits_reclassified": deposits_reclassified,
        "periods_fixed": periods_fixed,
        "matches_creados": matches_creados,
        "total_conciliados": total_conciliados,
        "total_transactions": total_txs,
        "message": msg
    }


@router.post("/invoices/{uuid}/comprobar")
def comprobar_invoice(
    uuid: str,
    payload: ComprobarInvoiceRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Marca una factura CFDI como comprobada fuera de la cuenta bancaria principal
    (ej. Pago efectivo, Hipoteca, Rendimientos, Otra TC).
    """
    clean_uuid = uuid.strip()
    factura = db.query(CFDIInvoice).filter(func.lower(CFDIInvoice.uuid) == clean_uuid.lower()).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura CFDI no encontrada.")

    motivo = payload.motivo.strip()
    if not motivo:
        raise HTTPException(status_code=400, detail="El motivo de comprobación es obligatorio.")

    factura.comprobado = True
    factura.motivo_comprobacion = motivo
    db.commit()
    db.refresh(factura)

    return {
        "success": True,
        "uuid": factura.uuid,
        "comprobado": True,
        "motivo_comprobacion": factura.motivo_comprobacion,
        "message": f"Factura amparada exitosamente como comprobada ({factura.motivo_comprobacion})."
    }


@router.post("/invoices/{uuid}/revert-comprobar")
def revert_comprobar_invoice(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Desmarca la comprobación de una factura CFDI, devolviéndola al estado 'Pendiente Banco'.
    """
    clean_uuid = uuid.strip()
    factura = db.query(CFDIInvoice).filter(func.lower(CFDIInvoice.uuid) == clean_uuid.lower()).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura CFDI no encontrada.")

    factura.comprobado = False
    factura.motivo_comprobacion = None
    db.commit()
    db.refresh(factura)

    return {
        "success": True,
        "uuid": factura.uuid,
        "comprobado": False,
        "motivo_comprobacion": None,
        "message": f"Factura {factura.uuid} desmarcada. Vuelve a estar pendiente de conciliación bancaria."
    }


@router.post("/purge-credit-card-transactions")
def purge_credit_card_transactions(
    account_rfc: str = Query("DEGF851127TK1"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Elimina todos los movimientos de tarjeta de crédito (Mercado Pago / Mercado Libre)
    de la tabla bank_transactions para mantener la conciliación bancaria enfocada 100%
    en la cuenta bancaria fiscal (BBVA).
    
    Las facturas CFDI que se encontraban vinculadas a estos movimientos se amparan
    automáticamente como 'comprobado = True' con motivo 'TC Mercado Libre',
    para preservar su trazabilidad contable y deducibilidad en el buzón.
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]

    # 1. Buscar transacciones de TC asociadas a la entidad
    tc_query = db.query(BankTransaction).filter(
        BankTransaction.account_rfc == effective_rfc,
        (
            (BankTransaction.banco.ilike("%MERCADO%")) |
            (BankTransaction.banco.ilike("%LIBRE%")) |
            (BankTransaction.banco.ilike("TC%"))
        )
    )
    tc_txs = tc_query.all()
    
    # 2. Facturas vinculadas que deben preservarse como 'TC Mercado Libre'
    migrated_uuids = []
    cfdi_uuids = [t.uuid_cfdi for t in tc_txs if t.uuid_cfdi]
    if cfdi_uuids:
        cfdis = db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_(cfdi_uuids)).all()
        for cfdi in cfdis:
            cfdi.comprobado = True
            cfdi.motivo_comprobacion = "TC Mercado Libre"
            cfdi.conciliado = False
            migrated_uuids.append(cfdi.uuid)
    
    # 3. Eliminar las transacciones de tarjeta de crédito
    deleted_count = len(tc_txs)
    tc_ids = [t.id for t in tc_txs]
    if tc_ids:
        db.query(BankTransaction).filter(BankTransaction.id.in_(tc_ids)).delete(synchronize_session=False)

    db.commit()

    return {
        "success": True,
        "deleted_transactions_count": deleted_count,
        "migrated_invoices_count": len(migrated_uuids),
        "migrated_cfdi_uuids": migrated_uuids,
        "message": f"Se eliminaron {deleted_count} movimientos de tarjeta de crédito y se ampararon {len(migrated_uuids)} facturas CFDI con 'TC Mercado Libre'."
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
    lookback_days: int = Query(60),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Detona la lectura y sincronización del buzón de correo dedicado vía IMAP para la entidad solicitada.
    """
    res = sync_mailbox_invoices(db, account_rfc=account_rfc, lookback_days=lookback_days)
    return res


@router.get("/cron-sync")
def cron_sync_all_mailboxes(
    db: Session = Depends(get_db)
):
    """
    Detonador periódico (Vercel Cron / Tareas en segundo plano) para sincronizar
    automáticamente los buzones de todas las entidades (HIPHA y AMDI).
    """
    res_hipha = sync_mailbox_invoices(db, account_rfc="DEGF851127TK1", lookback_days=30)
    res_amdi = sync_mailbox_invoices(db, account_rfc="MEHA850118Q96", lookback_days=30)
    return {
        "success": True,
        "hipha": res_hipha,
        "amdi": res_amdi
    }


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

