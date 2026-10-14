import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from fpdf import FPDF
from fpdf.enums import XPos, YPos


def _format_forma_pago(fp: str, mp: str = "") -> str:
    fp = (fp or "").strip()
    mp = (mp or "").strip().upper()
    mapping = {
        "01": "01 Efectivo",
        "02": "02 Cheque",
        "03": "03 SPEI",
        "04": "04 TC",
        "05": "05 Monedero",
        "06": "06 Dinero elect.",
        "08": "08 Vales",
        "28": "28 T. Débito",
        "29": "29 T. Servicios",
        "99": "99 Por definir",
    }
    label = mapping.get(fp, fp or "N/E")
    if mp:
        return f"{mp} ({label})"
    return label


class ReporteFaltantesPDF(FPDF):
    def __init__(self, mes_label: str = ""):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.mes_label = mes_label

    def header(self):
        self.set_fill_color(15, 23, 42)  # Slate 900
        self.rect(0, 0, 210, 28, 'F')

        self.set_xy(10, 6)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, 'HIPHA - CONTROL CONTABLE & FISCAL', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_xy(10, 13)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(148, 163, 184)  # Slate 400
        self.cell(0, 5, f'REPORTE EJECUTIVO DE DISCREPANCIAS Y FALTANTES | {self.mes_label or "PERÍODO ACTUAL"}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Página {self.page_no()} de {{nb}} | Control Fiscal Inteligente HiphaMX', align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)


def generate_discrepancies_pdf(
    transacciones: List[Dict[str, Any]],
    mes_label: str = "",
    facturas_sueltas: Optional[List[Dict[str, Any]]] = None
) -> bytes:
    """
    Genera un informe ejecutivo en PDF con:
    1. Movimientos bancarios que no cuentan con CFDI o que están por revisar.
    2. Facturas CFDI (XMLs) sueltas del mes que no cuentan con movimiento bancario ni comprobación.
    """
    if facturas_sueltas is None:
        facturas_sueltas = []

    pdf = ReporteFaltantesPDF(mes_label=mes_label)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # 1. Movimientos bancarios sin CFDI y por revisar
    faltantes = [t for t in transacciones if t.get("status_conciliacion") == "SIN_CFDI"]
    por_revisar = [t for t in transacciones if t.get("status_conciliacion") == "POR_REVISAR"]

    faltantes.sort(key=lambda x: float(x.get("monto") or 0.0), reverse=True)

    total_faltantes_egresos = sum(float(t.get("monto") or 0.0) for t in faltantes if t.get("tipo") == "EGRESO")
    total_faltantes_ingresos = sum(float(t.get("monto") or 0.0) for t in faltantes if t.get("tipo") == "INGRESO")

    # 2. Facturas sueltas (XMLs) sin banco
    xml_egresos = [f for f in facturas_sueltas if f.get("tipo") == "EGRESO"]
    xml_ingresos = [f for f in facturas_sueltas if f.get("tipo") == "INGRESO"]

    total_xml_egresos = sum(float(f.get("total") or 0.0) for f in xml_egresos)
    total_xml_ingresos = sum(float(f.get("total") or 0.0) for f in xml_ingresos)
    total_xml_sueltos = total_xml_egresos + total_xml_ingresos

    # Resumen Ejecutivo (Cards)
    pdf.set_fill_color(248, 250, 252)  # Slate 50
    pdf.set_draw_color(226, 232, 240)  # Slate 200
    pdf.rect(10, 32, 190, 42, 'DF')

    pdf.set_xy(14, 35)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 5, 'RESUMEN EJECUTIVO DE RIESGO FISCAL & DISCREPANCIAS', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(14, 43)
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(95, 5, f'- Cargos en banco sin CFDI: {len(faltantes)} movimientos (${total_faltantes_egresos:,.2f} MXN)', new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(95, 5, f'- Abonos en banco sin factura: ${total_faltantes_ingresos:,.2f} MXN', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(14, 50)
    pdf.cell(95, 5, f'- XMLs sueltos sin cargo/abono: {len(facturas_sueltas)} facturas (${total_xml_sueltos:,.2f} MXN)', new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(95, 5, f'  (Egresos: {len(xml_egresos)} (${total_xml_egresos:,.2f}) · Ingresos: {len(xml_ingresos)} (${total_xml_ingresos:,.2f}))', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(14, 57)
    pdf.cell(95, 5, f'- Movimientos bancarios por revisar: {len(por_revisar)} transacciones.', new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font('Helvetica', 'I', 7.5)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(95, 5, '[i] Haz clic en el UUID de cualquier factura para abrirla en el Dashboard', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(12)

    # ---------------------------------------------------------
    # SECCIÓN 1: EGRESOS BANCARIOS SIN FACTURA CFDI
    # ---------------------------------------------------------
    pdf.set_font('Helvetica', 'B', 10.5)
    pdf.set_text_color(185, 28, 28)  # Red 700
    pdf.cell(0, 6, '1. EGRESOS BANCARIOS SIN FACTURA CFDI (CARGOS NO DEDUCIBLES)', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, 'Cargos en la cuenta de BBVA que requieren solicitar la factura al proveedor para evitar pérdida de deducibilidad.', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    # Encabezados de tabla de bancos
    def render_bank_table_headers():
        pdf.set_fill_color(239, 68, 68)  # Red 500
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(24, 7, 'Fecha', 1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(90, 7, 'Concepto Bancario (BBVA)', 1, align='L', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(22, 7, 'Tipo', 1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(28, 7, 'Monto', 1, align='R', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(26, 7, 'Estatus', 1, align='C', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    render_bank_table_headers()

    pdf.set_text_color(15, 23, 42)
    pdf.set_font('Helvetica', '', 7)

    fill_row = False
    count_egresos = 0

    for tx in faltantes:
        if tx.get("tipo") != "EGRESO":
            continue
        count_egresos += 1

        if pdf.get_y() > 265:
            pdf.add_page()
            render_bank_table_headers()
            pdf.set_text_color(15, 23, 42)
            pdf.set_font('Helvetica', '', 7)

        pdf.set_fill_color(254, 242, 242) if fill_row else pdf.set_fill_color(255, 255, 255)

        fecha_val = tx.get("fecha")
        fecha_str = fecha_val.strftime("%Y-%m-%d") if isinstance(fecha_val, datetime) else str(fecha_val)[:10]
        concepto = str(tx.get("concepto") or "").strip()
        concepto_trunc = concepto[:52] + "..." if len(concepto) > 52 else concepto
        monto_num = float(tx.get("monto") or 0.0)

        pdf.cell(24, 6, fecha_str, 1, align='C', fill=fill_row, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(90, 6, concepto_trunc, 1, align='L', fill=fill_row, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(22, 6, 'CARGO', 1, align='C', fill=fill_row, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(28, 6, f"${monto_num:,.2f}", 1, align='R', fill=fill_row, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(26, 6, 'SIN CFDI', 1, align='C', fill=fill_row, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        fill_row = not fill_row

    if count_egresos == 0:
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(22, 101, 52)
        pdf.cell(190, 8, 'Excelente: No hay egresos bancarios pendientes de factura para este período.', 1, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(6)

    # ---------------------------------------------------------
    # SECCIÓN 2: FACTURAS CFDI (XMLs) SUELTAS DEL MES
    # ---------------------------------------------------------
    if pdf.get_y() > 230:
        pdf.add_page()

    pdf.set_font('Helvetica', 'B', 10.5)
    pdf.set_text_color(2, 132, 199)  # Sky 600
    pdf.cell(0, 6, '2. FACTURAS CFDI (XMLs) SUELTAS DEL MES (SIN MOVIMIENTO BANCARIO NI COMPROBACIÓN)', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, 'Facturas timbradas en el SAT que no cuentan con cargo/abono bancario en BBVA ni han sido comprobadas fuera de banco.', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    def render_xml_table_headers():
        pdf.set_fill_color(2, 132, 199)  # Sky 600
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(20, 7, 'Fecha', 1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(18, 7, 'Tipo', 1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(54, 7, 'Emisor / Proveedor', 1, align='L', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(46, 7, 'Concepto Resumen', 1, align='L', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(26, 7, 'Método / SAT', 1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(26, 7, 'Total Factura', 1, align='R', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    render_xml_table_headers()

    if not facturas_sueltas:
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(22, 101, 52)
        pdf.cell(190, 8, 'Excelente: No hay facturas CFDI sueltas sin conciliar ni comprobar para este período.', 1, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        fill_xml = False
        for f in facturas_sueltas:
            # Cada factura ocupa 2 renglones (fila de datos + fila de UUID/link) = ~10.5 mm
            if pdf.get_y() > 255:
                pdf.add_page()
                render_xml_table_headers()

            fecha_val = f.get("fecha")
            fecha_str = fecha_val.strftime("%Y-%m-%d") if isinstance(fecha_val, datetime) else str(fecha_val)[:10]
            tipo_str = str(f.get("tipo") or "EGRESO").upper()
            emisor_str = str(f.get("nombre_emisor") or f.get("rfc_emisor") or "Sin emisor")
            emisor_trunc = emisor_str[:26] + f" ({f.get('rfc_emisor', '')[:12]})" if len(emisor_str) > 26 else f"{emisor_str} ({f.get('rfc_emisor', '')})"
            concepto_str = str(f.get("concepto") or "Sin concepto").strip()
            concepto_trunc = concepto_str[:28] + "..." if len(concepto_str) > 28 else concepto_str
            total_num = float(f.get("total") or 0.0)
            pago_str = _format_forma_pago(str(f.get("forma_pago") or ""), str(f.get("metodo_pago") or ""))
            uuid_str = str(f.get("uuid") or "").strip()

            url_link = f"https://www.hipha.mx/projects/HiphaMX/dashboard/?search={uuid_str}"

            pdf.set_fill_color(240, 249, 255) if fill_xml else pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(15, 23, 42)
            pdf.set_font('Helvetica', '', 7)

            # Renglón 1: Datos principales
            pdf.cell(20, 6, fecha_str, 'TLR', align='C', fill=fill_xml, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(18, 6, tipo_str, 'TLR', align='C', fill=fill_xml, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(54, 6, emisor_trunc[:36], 'TLR', align='L', fill=fill_xml, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(46, 6, concepto_trunc[:30], 'TLR', align='L', fill=fill_xml, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(26, 6, pago_str[:17], 'TLR', align='C', fill=fill_xml, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(26, 6, f"${total_num:,.2f}", 'TLR', align='R', fill=fill_xml, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # Renglón 2: UUID con hipervínculo clickeable al dashboard
            pdf.set_font('Helvetica', '', 6)
            pdf.set_text_color(37, 99, 235)  # Azul hipervínculo
            uuid_label = f"   Folio Fiscal UUID: {uuid_str}  [Clic para abrir e inspeccionar en Dashboard]"
            pdf.cell(190, 4.5, uuid_label, 'BLR', align='L', fill=fill_xml, link=url_link, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            fill_xml = not fill_xml

    pdf.ln(6)

    # ---------------------------------------------------------
    # SECCIÓN 3: RECOMENDACIONES DEL AGENTE
    # ---------------------------------------------------------
    if pdf.get_y() > 245:
        pdf.add_page()

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, 'RECOMENDACIONES AUTOMATIZADAS DEL AGENTE', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(71, 85, 105)

    recs = [
        "1. Cargos bancarios sin CFDI: Solicitar la factura digital al proveedor adjuntando el comprobante SPEI/CEP del banco.",
        "2. Facturas de egreso sueltas: Si fueron pagadas en efectivo, caja chica o tarjeta de crédito personal, ampararlas en el dashboard con 1 clic seleccionando 'Comprobar fuera de banco (Efectivo / Otra TC)' para acreditarlas fiscalmente.",
        "3. Facturas de ingreso sueltas: Si corresponden a ventas cobradas en el banco, conciliar con el depósito recibido; si son crédito comercial (PPD), permanecerán pendientes hasta la emisión del Complemento de Pago (REP)."
    ]
    for r in recs:
        pdf.multi_cell(190, 5, r)

    return bytes(pdf.output())
