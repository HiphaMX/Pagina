import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_

from app.core.config import settings, get_reconciliation_entity_config
from app.models.reconciliation import BankTransaction, CFDIInvoice
from app.services.reconciliation.pdf_parser import is_own_account_transfer

logger = logging.getLogger(__name__)


def audit_month_fiscal_health(
    db: Session,
    account_rfc: str,
    month: str,
    use_ai: bool = True
) -> Dict[str, Any]:
    """
    Ejecuta la auditoría fiscal y contable del mes para una entidad (HIPHA o AMDI).
    Calcula balances de IVA, porcentaje de comprobación, detecta cargos pendientes de justificar,
    facturas PPD sin complemento de pago y genera una síntesis ejecutiva con Gemini (o heurística).
    """
    entity_cfg = get_reconciliation_entity_config(account_rfc)
    effective_rfc = entity_cfg["rfc"]
    entity_name = entity_cfg["name"]

    # 1. Obtener transacciones del mes
    query_txs = db.query(BankTransaction).filter(
        BankTransaction.account_rfc == effective_rfc,
        BankTransaction.periodo_mes == month
    ).order_by(BankTransaction.fecha.asc()).all()

    ingresos_txs = [t for t in query_txs if t.tipo == "INGRESO"]
    egresos_txs = [t for t in query_txs if t.tipo == "EGRESO"]

    # Traspasos entre cuentas propias excluidos
    traspasos_ingresos = [
        t for t in ingresos_txs
        if not t.uuid_cfdi and (
            t.status_conciliacion in ("NO_APLICA", "EXENTO") or
            is_own_account_transfer(t.concepto, effective_rfc) or
            (t.nota_revision and "Traspaso entre Cuentas Propias" in t.nota_revision)
        )
    ]
    ingresos_comerciales = [t for t in ingresos_txs if t not in traspasos_ingresos]

    traspasos_egresos = [
        t for t in egresos_txs
        if not t.uuid_cfdi and (
            t.status_conciliacion in ("NO_APLICA", "EXENTO") or
            is_own_account_transfer(t.concepto, effective_rfc) or
            (t.nota_revision and "Traspaso entre Cuentas Propias" in t.nota_revision)
        )
    ]
    egresos_operativos = [t for t in egresos_txs if t not in traspasos_egresos]

    total_ingresos_banco = sum(t.monto for t in ingresos_comerciales)
    total_egresos_banco = sum(t.monto for t in egresos_operativos)

    # 2. Análisis de comprobación y pendientes
    sin_cfdi_egresos = [t for t in egresos_operativos if t.status_conciliacion == "SIN_CFDI" and not t.uuid_cfdi]
    monto_sin_cfdi = sum(t.monto for t in sin_cfdi_egresos)
    count_sin_cfdi = len(sin_cfdi_egresos)

    conciliados_egresos = [t for t in egresos_operativos if t.status_conciliacion in ("CONCILIADO", "CONCILIADO_DIRECTO", "CONCILIADO_POR_REGLA", "COMPROBADO_FUERA", "COMPROBADO") or t.uuid_cfdi is not None]
    no_aplica_egresos = [t for t in egresos_operativos if t.status_conciliacion in ("NO_APLICA", "EXENTO")]

    total_egresos_comprobados_o_justificados = sum(t.monto for t in conciliados_egresos) + sum(t.monto for t in no_aplica_egresos)
    pct_egresos_comprobados = round((total_egresos_comprobados_o_justificados / total_egresos_banco * 100), 1) if total_egresos_banco > 0 else (100.0 if not sin_cfdi_egresos else 0.0)
    pct_egresos_comprobados = min(100.0, pct_egresos_comprobados)

    # Top cargos pendientes más significativos
    top_pendientes = sorted(sin_cfdi_egresos, key=lambda x: x.monto, reverse=True)[:5]
    top_pendientes_data = [
        {
            "id": t.id,
            "fecha": t.fecha.strftime("%d/%m/%Y") if hasattr(t.fecha, "strftime") else str(t.fecha)[:10],
            "concepto": t.concepto,
            "monto": round(float(t.monto), 2),
            "area_proyecto": t.area_proyecto or "No asignado"
        }
        for t in top_pendientes
    ]

    # 3. Facturas e Impuestos (IVA Trasladado vs Acreditable)
    start_dt = None
    end_dt = None
    try:
        parts = month.split("-")
        y, m = int(parts[0]), int(parts[1])
        start_dt = datetime(y, m, 1)
        end_dt = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    except Exception:
        pass

    cfdis_mes = []
    if start_dt and end_dt:
        cfdis_mes = db.query(CFDIInvoice).filter(
            CFDIInvoice.account_rfc == effective_rfc,
            CFDIInvoice.fecha_emision >= start_dt,
            CFDIInvoice.fecha_emision < end_dt
        ).all()

    # Ingresos facturados que no sean PPD amparados por REP
    def _is_ppd_covered(inv: CFDIInvoice) -> bool:
        if getattr(inv, "complemento_pago_uuid", None):
            return True
        motivo = str(getattr(inv, "motivo_comprobacion", None) or "").upper()
        return "PAGADA_CON_REP" in motivo or "PAGADA_CON_COMPLEMENTO" in motivo

    ingresos_cfdis = [c for c in cfdis_mes if c.tipo == "INGRESO" and not _is_ppd_covered(c)]
    egresos_cfdis = [c for c in cfdis_mes if c.tipo == "EGRESO" and (c.conciliado or c.comprobado)]

    iva_trasladado_ingresos = round(sum(float(c.iva_trasladado or 0.0) for c in ingresos_cfdis), 2)
    iva_acreditable_egresos = round(sum(float(c.iva_trasladado or 0.0) for c in egresos_cfdis), 2)
    balance_iva = round(iva_trasladado_ingresos - iva_acreditable_egresos, 2)

    total_facturado_ingresos = round(sum(float(c.total or 0.0) for c in ingresos_cfdis), 2)
    total_comprobado_egresos = round(sum(float(c.total or 0.0) for c in egresos_cfdis), 2)

    # 4. Detección de facturas PPD sin complemento de pago
    ppd_invoices_sin_rep = [
        c for c in cfdis_mes
        if c.tipo == "INGRESO" and getattr(c, "metodo_pago", "") == "PPD" and not getattr(c, "complemento_pago_uuid", None)
    ]
    count_ppd_sin_rep = len(ppd_invoices_sin_rep)

    # 5. Detección de posibles duplicados en banco
    dups_map: Dict[str, List[BankTransaction]] = {}
    for t in query_txs:
        key = f"{str(t.fecha)[:10]}_{round(float(t.monto), 2)}_{t.tipo}"
        dups_map.setdefault(key, []).append(t)
    posibles_duplicados = [txs for txs in dups_map.values() if len(txs) > 1]
    count_duplicados = sum(len(txs) for txs in posibles_duplicados)

    # 6. Cálculo de Score y Nivel de Salud Fiscal
    is_mes_completo = (count_sin_cfdi == 0 and len(query_txs) > 0)
    score = 100
    if not is_mes_completo:
        score -= min(50, count_sin_cfdi * 10)
    if count_duplicados > 0:
        score -= min(15, count_duplicados * 5)
    if count_ppd_sin_rep > 0:
        score -= min(15, count_ppd_sin_rep * 5)
    score = max(20, min(100, score))

    if is_mes_completo:
        health_level = "MES_COMPLETO"
    elif score >= 75:
        health_level = "POR_REVISAR"
    else:
        health_level = "ALERTA_FISCAL"

    # 7. Recomendaciones accionables estructuradas
    recommendations: List[str] = []
    if count_sin_cfdi > 0:
        recommendations.append(
            f"Faltan {count_sin_cfdi} cargo(s) por comprobar o justificar (${monto_sin_cfdi:,.2f} MXN). Justifícalos como gastos personales o traspasos para activar el Check de Mes Completo al 100%."
        )
    if count_ppd_sin_rep > 0:
        recommendations.append(
            f"Hay {count_ppd_sin_rep} factura(s) emitida(s) en método PPD que no tienen Complemento de Pago timbrado vinculado."
        )
    if count_duplicados > 0:
        recommendations.append(
            f"Se identificaron {count_duplicados} movimientos con montos idénticos en la misma fecha en BBVA; revisa si alguno es cobro doble o devolución de cargo."
        )
    if balance_iva > 0:
        recommendations.append(
            f"Balance estimado de IVA a pagar al SAT: ${balance_iva:,.2f} MXN. Comprobar facturas pendientes de egresos te ayudará a acreditar más IVA y reducir este saldo."
        )
    elif balance_iva < 0:
        recommendations.append(
            f"Tienes un saldo a favor proyectado de IVA de ${abs(balance_iva):,.2f} MXN, ya que tus gastos comprobados superaron los ingresos facturados del periodo."
        )
    if not recommendations:
        recommendations.append("El mes se encuentra completamente conciliado y sin discrepancias fiscales detectadas.")

    # 8. Síntesis Ejecutiva con IA (Gemini) o Fallback
    agent_summary = _generate_fiscal_ai_briefing(
        entity_name=entity_name,
        month=month,
        is_mes_completo=is_mes_completo,
        pct_egresos=pct_egresos_comprobados,
        count_sin_cfdi=count_sin_cfdi,
        monto_sin_cfdi=monto_sin_cfdi,
        total_ingresos_banco=total_ingresos_banco,
        total_egresos_banco=total_egresos_banco,
        iva_trasladado=iva_trasladado_ingresos,
        iva_acreditable=iva_acreditable_egresos,
        balance_iva=balance_iva,
        top_pendientes=top_pendientes_data,
        count_ppd_sin_rep=count_ppd_sin_rep,
        recommendations=recommendations,
        use_ai=use_ai
    )

    return {
        "entity": {
            "rfc": effective_rfc,
            "name": entity_name
        },
        "month": month,
        "is_mes_completo": is_mes_completo,
        "score": score,
        "health_level": health_level,
        "completion_pct": pct_egresos_comprobados,
        "kpis": {
            "total_ingresos_banco": round(total_ingresos_banco, 2),
            "total_egresos_banco": round(total_egresos_banco, 2),
            "monto_sin_cfdi": round(monto_sin_cfdi, 2),
            "count_sin_cfdi": count_sin_cfdi,
            "total_facturado_ingresos": total_facturado_ingresos,
            "total_comprobado_egresos": total_comprobado_egresos,
            "iva_trasladado": iva_trasladado_ingresos,
            "iva_acreditable": iva_acreditable_egresos,
            "balance_iva_estimado": balance_iva,
            "count_ppd_sin_rep": count_ppd_sin_rep,
            "count_posibles_duplicados": count_duplicados
        },
        "top_pendientes": top_pendientes_data,
        "recommendations": recommendations,
        "agent_summary": agent_summary,
        "audited_at": datetime.utcnow().isoformat()
    }


def _generate_fiscal_ai_briefing(
    entity_name: str,
    month: str,
    is_mes_completo: bool,
    pct_egresos: float,
    count_sin_cfdi: int,
    monto_sin_cfdi: float,
    total_ingresos_banco: float,
    total_egresos_banco: float,
    iva_trasladado: float,
    iva_acreditable: float,
    balance_iva: float,
    top_pendientes: List[Dict[str, Any]],
    count_ppd_sin_rep: int,
    recommendations: List[str],
    use_ai: bool = True
) -> str:
    """
    Genera el reporte ejecutivo en lenguaje natural estructurado para el Agente Auditor Fiscal.
    Utiliza Google Gemini con fallback heurístico garantizado.
    """
    if use_ai:
        gemini_key = getattr(settings, "GEMINI_API_KEY", None) or __import__("os").environ.get("GEMINI_API_KEY")
        if gemini_key and len(gemini_key) > 10:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-2.5-flash")

                top_desc = ", ".join([f"{p['concepto']} (${p['monto']:,.2f})" for p in top_pendientes[:3]])
                prompt = (
                    f"Eres el Agente Auditor Fiscal y Contable de la agencia de marketing digital HiphaMX. "
                    f"Estás auditando el mes {month} para la entidad fiscal {entity_name}.\n"
                    f"Datos contables:\n"
                    f"- Estatus: {'MES COMPLETO AL 100%' if is_mes_completo else f'{pct_egresos}% comprobado'}\n"
                    f"- Ingresos en banco: ${total_ingresos_banco:,.2f} MXN\n"
                    f"- Egresos en banco: ${total_egresos_banco:,.2f} MXN\n"
                    f"- Cargos pendientes sin factura: {count_sin_cfdi} movimientos que suman ${monto_sin_cfdi:,.2f} MXN (ejemplos: {top_desc or 'Ninguno'})\n"
                    f"- IVA Trasladado (cobrado): ${iva_trasladado:,.2f} MXN | IVA Acreditable (gastos): ${iva_acreditable:,.2f} MXN\n"
                    f"- Balance proyectado de IVA: {'A pagar: $' + f'{balance_iva:,.2f}' if balance_iva > 0 else ('A favor: $' + f'{abs(balance_iva):,.2f}' if balance_iva < 0 else '$0.00')}\n"
                    f"- Facturas PPD pendientes de Complemento REP: {count_ppd_sin_rep}\n\n"
                    f"Redacta un diagnóstico ejecutivo breve (3 a 4 oraciones) en tono profesional, claro y cercano para Chizko (dueño de la agencia).\n"
                    f"Estructura el texto en 2 partes:\n"
                    f"1. **Diagnóstico del Mes**: Explica cómo está el cierre del mes y el balance proyectado de IVA ante el SAT.\n"
                    f"2. **Acción Recomendada**: Señala la acción más inteligente para optimizar el mes (justificar comisiones/traspasos o pedir facturas)."
                )
                resp = model.generate_content(prompt)
                if resp and resp.text:
                    return resp.text.strip()
            except Exception as e:
                logger.debug(f"Fiscal Auditor Agent Gemini fallback: {e}")

    # Fallback Heurístico Determinista de Alta Calidad
    if is_mes_completo:
        iva_text = f"con un saldo proyectado de IVA a pagar de **${balance_iva:,.2f} MXN**" if balance_iva > 0 else (f"con saldo a favor de IVA estimado de **${abs(balance_iva):,.2f} MXN**" if balance_iva < 0 else "con balance de IVA equilibrado")
        return (
            f"🎉 **Cierre Fiscal Impecable**: El periodo {month} para **{entity_name}** se encuentra conciliado al **100%**, "
            f"{iva_text}. Todas las transacciones bancarias cuentan con CFDI o justificación válida, "
            f"listo para presentar declaración provisional ante el SAT sin discrepancias."
        )

    iva_info = f"saldo a pagar de **${balance_iva:,.2f} MXN**" if balance_iva > 0 else (f"saldo a favor de **${abs(balance_iva):,.2f} MXN**" if balance_iva < 0 else "**$0.00 MXN**")
    top_items_sample = f" (como {top_pendientes[0]['concepto'][:35]})" if top_pendientes else ""

    return (
        f"⚖️ **Diagnóstico Fiscal ({month})**: La cuenta de **{entity_name}** presenta un avance de comprobación del **{pct_egresos}%** con un balance de IVA estimado con {iva_info}.\n\n"
        f"🔍 **Acción Recomendada**: Tienes **{count_sin_cfdi} cargo(s) pendientes** (${monto_sin_cfdi:,.2f} MXN){top_items_sample}. "
        f"Justifica los traspasos internos o comisiones bancarias exentas para desbloquear el **Check de Mes Completo al 100%**."
    )
