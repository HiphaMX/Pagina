import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from fpdf import FPDF
from fpdf.enums import XPos, YPos


def _clean(val: Any) -> str:
    if val is None:
        return ""
    text = str(val)
    text = text.replace("·", "-").replace("—", "-").replace("–", "-").replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace("…", "...")
    return text.encode("latin-1", "replace").decode("latin-1")


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
    def __init__(self, mes_label: str = "", entity_name: str = "HIPHA"):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.mes_label = mes_label
        # Si mes_label contiene "ENTIDAD (RFC)", inferir entity_name si no se proveyó uno específico
        if not entity_name or entity_name == "HIPHA":
            if mes_label and "(" in mes_label:
                self.entity_name = mes_label.split("(")[0].strip() or "HIPHA"
            else:
                self.entity_name = entity_name or "HIPHA"
        else:
            self.entity_name = entity_name

    def header(self):
        self.set_fill_color(15, 23, 42)  # Slate 900
        self.rect(0, 0, 210, 28, 'F')

        self.set_xy(10, 6)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, _clean(f'{self.entity_name} - CONTROL CONTABLE & FISCAL'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_xy(10, 13)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(148, 163, 184)  # Slate 400
        self.cell(0, 5, _clean(f'REPORTE MOVIMIENTOS BANCARIOS Y CFDI FALTANTES | {self.mes_label or "PERÍODO ACTUAL"}'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, _clean(f'Página {self.page_no()} de {{nb}} | Control Fiscal Inteligente HiphaMX'), align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)


def generate_discrepancies_pdf(
    transacciones: List[Dict[str, Any]],
    mes_label: str = "",
    facturas_sueltas: Optional[List[Dict[str, Any]]] = None,
    entity_name: Optional[str] = None
) -> bytes:
    """
    Genera un informe ejecutivo en PDF con:
    1. Movimientos bancarios debidamente conciliados con CFDI (100% amparados).
    2. Movimientos bancarios que no cuentan con CFDI (cargos no deducibles).
    3. Facturas CFDI (XMLs) sueltas del mes que no cuentan con movimiento bancario ni comprobación.
    4. Recomendaciones automatizadas del agente.
    """
    if facturas_sueltas is None:
        facturas_sueltas = []

    pdf = ReporteFaltantesPDF(mes_label=mes_label, entity_name=entity_name or "HIPHA")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # 1. Movimientos bancarios conciliados con CFDI
    conciliados = [
        t for t in transacciones
        if (t.get("status_conciliacion") in ("CONCILIADO", "CONCILIADO_DIRECTO", "CONCILIADO_POR_REGLA") or t.get("uuid_cfdi"))
        and t.get("status_conciliacion") not in ("NO_APLICA", "EXENTO")
    ]

    def _sort_key(item):
        f = item.get("fecha")
        f_str = f.strftime("%Y-%m-%d") if isinstance(f, datetime) else str(f or "")[:10]
        m = float(item.get("monto") or 0.0)
        return (f_str, m)

    conciliados.sort(key=_sort_key, reverse=True)

    conciliados_egresos = [t for t in conciliados if t.get("tipo") == "EGRESO"]
    conciliados_ingresos = [t for t in conciliados if t.get("tipo") == "INGRESO"]
    total_conciliados_egresos = sum(float(t.get("monto") or 0.0) for t in conciliados_egresos)
    total_conciliados_ingresos = sum(float(t.get("monto") or 0.0) for t in conciliados_ingresos)
    total_conciliados_monto = total_conciliados_egresos + total_conciliados_ingresos

    # 2. Movimientos bancarios sin CFDI y por revisar
    faltantes = [t for t in transacciones if t.get("status_conciliacion") == "SIN_CFDI"]
    por_revisar = [t for t in transacciones if t.get("status_conciliacion") == "POR_REVISAR"]

    faltantes.sort(key=lambda x: float(x.get("monto") or 0.0), reverse=True)

    faltantes_egresos = [t for t in faltantes if t.get("tipo") == "EGRESO"]
    faltantes_ingresos = [t for t in faltantes if t.get("tipo") == "INGRESO"]
    total_faltantes_egresos = sum(float(t.get("monto") or 0.0) for t in faltantes_egresos)
    total_faltantes_ingresos = sum(float(t.get("monto") or 0.0) for t in faltantes_ingresos)

    # 3. Facturas sueltas (XMLs) sin banco
    xml_egresos = [f for f in facturas_sueltas if f.get("tipo") == "EGRESO"]
    xml_ingresos = [f for f in facturas_sueltas if f.get("tipo") == "INGRESO"]

    total_xml_egresos = sum(float(f.get("total") or 0.0) for f in xml_egresos)
    total_xml_ingresos = sum(float(f.get("total") or 0.0) for f in xml_ingresos)
    total_xml_sueltos = total_xml_egresos + total_xml_ingresos

    # Resumen Ejecutivo (Cards)
    pdf.set_fill_color(248, 250, 252)  # Slate 50
    pdf.set_draw_color(203, 213, 225)  # Slate 300
    pdf.rect(10, 32, 190, 44, 'DF')

    pdf.set_xy(14, 35)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, _clean(f'RESUMEN EJECUTIVO DE CONCILIACIÓN, CONTROL FISCAL & RIESGO | {entity_name or "HIPHA"}'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(14, 43)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(5, 150, 105)  # Emerald 600
    pdf.cell(95, 5, _clean(f'- Movimientos conciliados con CFDI: {len(conciliados)} (${total_conciliados_monto:,.2f} MXN)'), new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(95, 5, _clean(f'  (Egresos: {len(conciliados_egresos)} (${total_conciliados_egresos:,.2f}) | Ingresos: {len(conciliados_ingresos)} (${total_conciliados_ingresos:,.2f}))'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(14, 50)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(185, 28, 28)  # Red 700
    pdf.cell(95, 5, _clean(f'- Cargos en banco sin CFDI: {len(faltantes_egresos)} (${total_faltantes_egresos:,.2f} MXN)'), new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(95, 5, _clean(f'- Abonos en banco sin factura: ${total_faltantes_ingresos:,.2f} MXN'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(14, 57)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(2, 132, 199)  # Sky 600
    pdf.cell(95, 5, _clean(f'- XMLs sueltos sin cargo/abono: {len(facturas_sueltas)} (${total_xml_sueltos:,.2f} MXN)'), new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(95, 5, _clean(f'  (Egresos: {len(xml_egresos)} (${total_xml_egresos:,.2f}) | Ingresos: {len(xml_ingresos)} (${total_xml_ingresos:,.2f}))'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(14, 64)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(95, 5, _clean(f'- Movimientos bancarios por revisar: {len(por_revisar)} transacciones.'), new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font('Helvetica', 'I', 7.5)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(95, 5, _clean('[i] Haz clic en el UUID de cualquier factura para abrirla en el Dashboard'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(80)

    # ---------------------------------------------------------
    # SECCIÓN 1: MOVIMIENTOS BANCARIOS CONCILIADOS CON FACTURA CFDI
    # ---------------------------------------------------------
    pdf.set_font('Helvetica', 'B', 10.5)
    pdf.set_text_color(5, 150, 105)  # Emerald 600
    pdf.cell(0, 6, '1. MOVIMIENTOS BANCARIOS CONCILIADOS CON FACTURA CFDI (100% AMPARADOS)', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, 'Transacciones bancarias debidamente vinculadas a su comprobante fiscal (CFDI). Cumplimiento y deducibilidad verificada.', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    def render_reconciled_table_headers():
        pdf.set_fill_color(5, 150, 105)  # Emerald 600
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(20, 7, 'Fecha', 1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(50, 7, 'Concepto Bancario', 1, align='L', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(16, 7, 'Tipo', 1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(24, 7, 'Monto Banco', 1, align='R', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(54, 7, 'Emisor / Receptor CFDI', 1, align='L', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(26, 7, 'Total Factura', 1, align='R', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    render_reconciled_table_headers()

    if not conciliados:
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(190, 8, _clean('No se registraron movimientos conciliados con CFDI para este período.'), 1, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        fill_recon = False
        for tx in conciliados:
            if pdf.get_y() > 255:
                pdf.add_page()
                render_reconciled_table_headers()

            fecha_val = tx.get("fecha")
            fecha_str = fecha_val.strftime("%Y-%m-%d") if isinstance(fecha_val, datetime) else str(fecha_val)[:10]
            concepto = str(tx.get("concepto") or "").strip()
            concepto_trunc = concepto[:28] + "..." if len(concepto) > 28 else concepto
            tipo_str = "ABONO" if tx.get("tipo") == "INGRESO" else "CARGO"
            monto_num = float(tx.get("monto") or 0.0)

            # CFDI Contraparte
            if tx.get("tipo") == "INGRESO":
                cp_name = str(tx.get("nombre_receptor") or tx.get("rfc_receptor") or tx.get("nombre_emisor") or "Cliente").strip()
                cp_rfc = str(tx.get("rfc_receptor") or tx.get("rfc_emisor") or "").strip()
            else:
                cp_name = str(tx.get("nombre_emisor") or tx.get("rfc_emisor") or tx.get("nombre_receptor") or "Proveedor").strip()
                cp_rfc = str(tx.get("rfc_emisor") or tx.get("rfc_receptor") or "").strip()

            if cp_rfc and len(cp_name) > 22:
                cp_display = f"{cp_name[:22]} ({cp_rfc[:12]})"
            elif cp_rfc:
                cp_display = f"{cp_name} ({cp_rfc})"
            else:
                cp_display = cp_name[:34]

            cfdi_total = float(tx.get("cfdi_total") or monto_num)
            uuid_str = str(tx.get("uuid_cfdi") or "").strip()
            url_link = f"https://www.hipha.mx/projects/HiphaMX/dashboard/?search={uuid_str}" if uuid_str else None

            pago_str = _format_forma_pago(str(tx.get("cfdi_forma") or ""), str(tx.get("cfdi_metodo") or ""))
            cfdi_concepto = str(tx.get("cfdi_concepto") or "").strip()
            if cfdi_concepto:
                cfdi_concepto_trunc = cfdi_concepto[:40] + "..." if len(cfdi_concepto) > 40 else cfdi_concepto
            else:
                cfdi_concepto_trunc = "Factura CFDI amparada"

            pdf.set_fill_color(240, 253, 244) if fill_recon else pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(15, 23, 42)
            pdf.set_font('Helvetica', '', 7)

            # Renglón 1: Datos principales
            pdf.cell(20, 6, _clean(fecha_str), 'TLR', align='C', fill=fill_recon, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(50, 6, _clean(concepto_trunc), 'TLR', align='L', fill=fill_recon, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(16, 6, _clean(tipo_str), 'TLR', align='C', fill=fill_recon, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(24, 6, f"${monto_num:,.2f}", 'TLR', align='R', fill=fill_recon, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(54, 6, _clean(cp_display), 'TLR', align='L', fill=fill_recon, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(26, 6, f"${cfdi_total:,.2f}", 'TLR', align='R', fill=fill_recon, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # Renglón 2: UUID con enlace interactivo y detalles de método de pago
            pdf.set_font('Helvetica', '', 6)
            pdf.set_text_color(5, 150, 105)
            if uuid_str:
                subrow_label = f"   UUID: {uuid_str}  |  Pago: {pago_str}  |  Concepto: {cfdi_concepto_trunc}  [Abrir]"
                pdf.cell(190, 4.5, _clean(subrow_label), 'BLR', align='L', fill=fill_recon, link=url_link, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                subrow_label = f"   Conciliado por regla / comprobación  |  {tx.get('nota_revision') or 'Amparado fiscalmente'}"
                pdf.cell(190, 4.5, _clean(subrow_label), 'BLR', align='L', fill=fill_recon, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            fill_recon = not fill_recon

    pdf.ln(6)

    # ---------------------------------------------------------
    # SECCIÓN 2: EGRESOS BANCARIOS SIN FACTURA CFDI
    # ---------------------------------------------------------
    if pdf.get_y() > 230:
        pdf.add_page()

    pdf.set_font('Helvetica', 'B', 10.5)
    pdf.set_text_color(185, 28, 28)  # Red 700
    pdf.cell(0, 6, '2. EGRESOS BANCARIOS SIN FACTURA CFDI (CARGOS NO DEDUCIBLES)', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, 'Cargos en la cuenta bancaria que requieren solicitar la factura al proveedor para evitar pérdida de deducibilidad.', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    # Encabezados de tabla de bancos
    def render_bank_table_headers():
        pdf.set_fill_color(239, 68, 68)  # Red 500
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(24, 7, 'Fecha', 1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(90, 7, 'Concepto Bancario', 1, align='L', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
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

        pdf.cell(24, 6, _clean(fecha_str), 1, align='C', fill=fill_row, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(90, 6, _clean(concepto_trunc), 1, align='L', fill=fill_row, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(22, 6, 'CARGO', 1, align='C', fill=fill_row, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(28, 6, f"${monto_num:,.2f}", 1, align='R', fill=fill_row, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(26, 6, 'SIN CFDI', 1, align='C', fill=fill_row, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        fill_row = not fill_row

    if count_egresos == 0:
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(22, 101, 52)
        pdf.cell(190, 8, _clean('Excelente: No hay egresos bancarios pendientes de factura para este período.'), 1, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(6)

    # ---------------------------------------------------------
    # SECCIÓN 3: FACTURAS CFDI (XMLs) SUELTAS DEL MES
    # ---------------------------------------------------------
    if pdf.get_y() > 230:
        pdf.add_page()

    pdf.set_font('Helvetica', 'B', 10.5)
    pdf.set_text_color(2, 132, 199)  # Sky 600
    pdf.cell(0, 6, '3. FACTURAS CFDI (XMLs) SUELTAS DEL MES (SIN MOVIMIENTO BANCARIO NI COMPROBACIÓN)', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, 'Facturas timbradas en el SAT que no cuentan con cargo/abono bancario ni han sido comprobadas fuera de banco.', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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
        pdf.cell(190, 8, _clean('Excelente: No hay facturas CFDI sueltas sin conciliar ni comprobar para este período.'), 1, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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
            pdf.cell(20, 6, _clean(fecha_str), 'TLR', align='C', fill=fill_xml, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(18, 6, _clean(tipo_str), 'TLR', align='C', fill=fill_xml, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(54, 6, _clean(emisor_trunc[:36]), 'TLR', align='L', fill=fill_xml, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(46, 6, _clean(concepto_trunc[:30]), 'TLR', align='L', fill=fill_xml, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(26, 6, _clean(pago_str[:17]), 'TLR', align='C', fill=fill_xml, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(26, 6, f"${total_num:,.2f}", 'TLR', align='R', fill=fill_xml, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # Renglón 2: UUID con hipervínculo clickeable al dashboard
            pdf.set_font('Helvetica', '', 6)
            pdf.set_text_color(37, 99, 235)  # Azul hipervínculo
            uuid_label = f"   Folio Fiscal UUID: {uuid_str}  [Clic para abrir e inspeccionar en Dashboard]"
            pdf.cell(190, 4.5, _clean(uuid_label), 'BLR', align='L', fill=fill_xml, link=url_link, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            fill_xml = not fill_xml

    pdf.ln(6)

    # ---------------------------------------------------------
    # SECCIÓN 4: RECOMENDACIONES DEL AGENTE
    # ---------------------------------------------------------
    if pdf.get_y() > 240:
        pdf.add_page()

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, '4. RECOMENDACIONES AUTOMATIZADAS DEL AGENTE', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(71, 85, 105)

    recs = [
        "1. Movimientos conciliados: Las operaciones amparadas cuentan con su comprobante fiscal correspondiente y cumplen los requisitos de deducibilidad y acumulación fiscal.",
        "2. Cargos bancarios sin CFDI: Solicitar la factura digital al proveedor adjuntando el comprobante SPEI/CEP del banco.",
        "3. Facturas de egreso sueltas: Si fueron pagadas en efectivo, caja chica o tarjeta de crédito personal, ampararlas en el dashboard con 1 clic seleccionando 'Comprobar fuera de banco (Efectivo / Otra TC)' para acreditarlas fiscalmente.",
        "4. Facturas de ingreso sueltas: Si corresponden a ventas cobradas en el banco, conciliar con el depósito recibido; si son crédito comercial (PPD), permanecerán pendientes hasta la emisión del Complemento de Pago (REP)."
    ]
    for r in recs:
        pdf.multi_cell(190, 5, _clean(r))

    return bytes(pdf.output())
