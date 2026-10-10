import io
from typing import List, Dict, Any
from datetime import datetime
from fpdf import FPDF


class ReporteFaltantesPDF(FPDF):
    def __init__(self, mes_label: str = ""):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.mes_label = mes_label

    def header(self):
        # Fondo decorativo del encabezado
        self.set_fill_color(15, 23, 42)  # Slate 900
        self.rect(0, 0, 210, 28, 'F')

        # Logotipo / Nombre
        self.set_xy(10, 6)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, 'HIPHA - CONTROL CONTABLE & FISCAL', ln=True)

        self.set_xy(10, 13)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(148, 163, 184)  # Slate 400
        self.cell(0, 5, f'REPORTE EJECUTIVO DE DISCREPANCIAS Y FALTANTES | PERÍODO: {self.mes_label or "ACTUAL"}', ln=True)

        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Página {self.page_no()} de {{nb}} | Generado automáticamente por Agente Antigravity', align='C')


def generate_discrepancies_pdf(transacciones: List[Dict[str, Any]], mes_label: str = "") -> bytes:
    """
    Genera un informe ejecutivo en PDF con los movimientos bancarios que no cuentan con CFDI
    o que se encuentran pendientes de revisión.
    """
    pdf = ReporteFaltantesPDF(mes_label=mes_label)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Filtrar movimientos sin CFDI y por revisar
    faltantes = [t for t in transacciones if t.get("status_conciliacion") == "SIN_CFDI"]
    por_revisar = [t for t in transacciones if t.get("status_conciliacion") == "POR_REVISAR"]

    # Ordenar faltantes por monto descendente para atender primero los montos más altos
    faltantes.sort(key=lambda x: float(x.get("monto") or 0.0), reverse=True)

    total_faltantes_egresos = sum(float(t.get("monto") or 0.0) for t in faltantes if t.get("tipo") == "EGRESO")
    total_faltantes_ingresos = sum(float(t.get("monto") or 0.0) for t in faltantes if t.get("tipo") == "INGRESO")

    # 1. Resumen Ejecutivo (Cards)
    pdf.set_fill_color(248, 250, 252)  # Slate 50
    pdf.set_draw_color(226, 232, 240)  # Slate 200
    pdf.rect(10, 32, 190, 32, 'DF')

    pdf.set_xy(14, 35)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 5, 'RESUMEN EJECUTIVO DE RIESGO FISCAL & DISCREPANCIAS', ln=True)

    pdf.set_xy(14, 43)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(60, 5, f'- Movimientos sin CFDI: {len(faltantes)} transacciones', ln=False)
    pdf.cell(65, 5, f'- Gastos sin deducir: ${total_faltantes_egresos:,.2f} MXN', ln=False)
    pdf.cell(65, 5, f'- Ingresos no facturados: ${total_faltantes_ingresos:,.2f} MXN', ln=True)

    pdf.set_xy(14, 51)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, f'Movimientos pendientes de confirmación (Por Revisar): {len(por_revisar)} transacciones.', ln=True)

    pdf.ln(12)

    # 2. Tabla de Movimientos sin Factura (Egresos no deducibles)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(185, 28, 28)  # Red 700
    pdf.cell(0, 7, '1. EGRESOS BANCARIOS SIN COMPROBANTE FISCAL DIGITAL (PRIORIDAD ALTA)', ln=True)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, 'Requiere solicitar la factura al proveedor antes del cierre mensual para evitar pérdida de deducibilidad.', ln=True)
    pdf.ln(2)

    # Encabezados de tabla
    pdf.set_fill_color(239, 68, 68)  # Red 500
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 8)

    pdf.cell(24, 7, 'Fecha', 1, 0, 'C', fill=True)
    pdf.cell(90, 7, 'Concepto Bancario (BBVA)', 1, 0, 'L', fill=True)
    pdf.cell(22, 7, 'Tipo', 1, 0, 'C', fill=True)
    pdf.cell(28, 7, 'Monto', 1, 0, 'R', fill=True)
    pdf.cell(26, 7, 'Estatus', 1, 1, 'C', fill=True)

    # Filas
    pdf.set_text_color(15, 23, 42)
    pdf.set_font('Helvetica', '', 7)
    pdf.set_fill_color(254, 242, 242)  # Red 50 alternado

    fill_row = False
    count_egresos = 0

    for tx in faltantes:
        if tx.get("tipo") != "EGRESO":
            continue
        count_egresos += 1

        fecha_val = tx.get("fecha")
        fecha_str = fecha_val.strftime("%Y-%m-%d") if isinstance(fecha_val, datetime) else str(fecha_val)[:10]

        concepto = str(tx.get("concepto") or "").strip()
        concepto_trunc = concepto[:52] + "..." if len(concepto) > 52 else concepto

        monto_num = float(tx.get("monto") or 0.0)

        pdf.cell(24, 6, fecha_str, 1, 0, 'C', fill=fill_row)
        pdf.cell(90, 6, concepto_trunc, 1, 0, 'L', fill=fill_row)
        pdf.cell(22, 6, 'CARGO', 1, 0, 'C', fill=fill_row)
        pdf.cell(28, 6, f"${monto_num:,.2f}", 1, 0, 'R', fill=fill_row)
        pdf.cell(26, 6, 'SIN CFDI', 1, 1, 'C', fill=fill_row)

        fill_row = not fill_row

    if count_egresos == 0:
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(22, 101, 52)
        pdf.cell(190, 8, 'Excelente: No hay egresos pendientes de factura para este período.', 1, 1, 'C')

    pdf.ln(6)

    # 3. Recomendaciones del Agente
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, 'RECOMENDACIONES AUTOMATIZADAS DEL AGENTE', ln=True)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(71, 85, 105)

    recs = [
        "1. Para transferencias a personas físicas o morales no recurrentes, enviar un correo solicitando el CFDI adjuntando el comprobante SPEI.",
        "2. Las comisiones bancarias de BBVA se amparan en el estado de cuenta fiscal global expedido por el banco a mes vencido.",
        "3. Verifique en el dashboard la bandeja de 'POR REVISAR' para aprobar con 1 clic coincidencias de montos con conceptos ambiguos."
    ]
    for r in recs:
        pdf.multi_cell(190, 5, r)

    return bytes(pdf.output())
