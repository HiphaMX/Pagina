import io
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from fpdf import FPDF
from pypdf import PdfReader, PdfWriter


TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "assets", "templates", "cotizacion_template.pdf"
)

# Datos bancarios oficiales de la agencia para SPEI
DEFAULT_BANK_DETAILS = {
    "bank": "BBVA México",
    "beneficiary": "Francisco Javier Delgado González (Hipha Media)",
    "clabe": "012 375 0153835678 9",
    "notes": "Favor de enviar comprobante de transferencia a contacto@hipha.mx",
}


class DynamicQuotationPDF(FPDF):
    """Generador dinámico de páginas para superposición vectorial."""

    def __init__(self):
        # Tamaño carta en milímetros: 215.9 x 279.4 mm
        super().__init__(orientation="P", unit="mm", format="letter")
        self.set_auto_page_break(auto=False, margin=0)


def format_currency(amount: float) -> str:
    return f"${amount:,.2f} MXN"


def format_spanish_date(dt: Optional[datetime]) -> str:
    if not dt:
        dt = datetime.now()
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    return f"{dt.day} de {months[dt.month - 1]} de {dt.year}"


def sanitize_text(text: str) -> str:
    """Sanitiza texto para fuentes estándar (Latin-1) de FPDF evitando fallos con caracteres unicode como bullets o comillas tipográficas."""
    if not text:
        return ""
    replacements = {
        "\u2022": "|",
        "\u2013": "-",
        "\u2014": "--",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_quotation_pdf(
    quotation_data: Dict[str, Any],
    bank_details: Optional[Dict[str, str]] = None,
) -> bytes:
    """
    Genera el PDF oficial de cotización combinando la plantilla membretada
    (portada oscura y detalle blanco con condiciones comerciales) con los
    datos dinámicos del cliente y conceptos.
    """
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Plantilla base no encontrada en: {TEMPLATE_PATH}")

    bank_info = bank_details or DEFAULT_BANK_DETAILS

    folio = sanitize_text(quotation_data.get("folio", "HIP-2026-0001"))
    client_name = sanitize_text(quotation_data.get("client_name", "Cliente").strip())
    client_contact = sanitize_text(quotation_data.get("client_contact", "").strip())
    client_email = sanitize_text(quotation_data.get("client_email", "").strip())
    client_phone = sanitize_text(quotation_data.get("client_phone", "").strip())
    notes = sanitize_text(quotation_data.get("notes", "").strip())
    validity_days = quotation_data.get("validity_days", 30)

    raw_date = quotation_data.get("date")
    if isinstance(raw_date, str):
        try:
            date_obj = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
        except Exception:
            date_obj = datetime.now()
    elif isinstance(raw_date, datetime):
        date_obj = raw_date
    else:
        date_obj = datetime.now()

    date_str = format_spanish_date(date_obj)

    # Procesar items y recalcular
    raw_items: List[Dict[str, Any]] = quotation_data.get("items", [])
    items: List[Dict[str, Any]] = []
    subtotal = 0.0

    for idx, it in enumerate(raw_items, 1):
        name = sanitize_text(it.get("name", f"Concepto {idx}"))
        desc = sanitize_text(it.get("description", ""))
        qty = float(it.get("quantity", 1.0))
        unit_price = float(it.get("unit_price", 0.0))
        item_sub = qty * unit_price
        subtotal += item_sub
        items.append({
            "idx": idx,
            "name": name,
            "description": desc,
            "quantity": qty,
            "unit_price": unit_price,
            "subtotal": item_sub,
        })

    apply_tax = bool(quotation_data.get("apply_tax", True))
    tax_rate = float(quotation_data.get("tax_rate", 0.16)) if apply_tax else 0.0
    tax_amount = subtotal * tax_rate if apply_tax else 0.0
    total = subtotal + tax_amount

    down_payment_rate = float(quotation_data.get("down_payment_rate", 0.50))
    down_payment_amount = total * down_payment_rate

    # 1. Crear documento dinámico FPDF
    pdf = DynamicQuotationPDF()

    # -------------------------------------------------------------
    # PÁGINA 1: PORTADA
    # -------------------------------------------------------------
    pdf.add_page()

    # Título superior / Categoría
    pdf.set_xy(16, 175)
    pdf.set_text_color(216, 180, 254)  # Púrpura suave elegante
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(184, 6, "PROPUESTA COMERCIAL & COTIZACION", align="C")

    # Nombre del Cliente / Proyecto (grande, blanco)
    pdf.set_xy(16, 184)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    # Truncar o ajustar si es muy largo
    display_client = client_name[:48].upper()
    pdf.cell(184, 10, display_client, align="C")

    # Persona de contacto o subtítulo
    pdf.set_xy(16, 196)
    pdf.set_text_color(203, 213, 225)  # Slate 300
    pdf.set_font("Helvetica", "", 11)
    if client_contact:
        pdf.cell(184, 6, f"Atencion: {client_contact}", align="C")
    else:
        pdf.cell(184, 6, "Estrategia Digital | Diseno | Desarrollo Web & IA", align="C")

    # Badge con Folio, Fecha y Vigencia
    pdf.set_xy(16, 214)
    pdf.set_text_color(148, 163, 184)  # Slate 400
    pdf.set_font("Helvetica", "", 9)
    metadata_line = f"FOLIO: {folio}   |   FECHA: {date_str.upper()}   |   VIGENCIA: {validity_days} DIAS"
    pdf.cell(184, 6, metadata_line, align="C")

    # Footer discreto de portada
    pdf.set_xy(16, 264)
    pdf.set_text_color(100, 116, 139)  # Slate 500
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(184, 5, "HIPHA MEDIA & TECH   |   MORELIA, MICHOACAN   |   HIPHA.MX", align="C")

    # -------------------------------------------------------------
    # PÁGINA 2+: PROPUESTA Y DESGLOSE
    # -------------------------------------------------------------
    pdf.add_page()

    def render_page2_header():
        # Título en esquina superior izquierda
        pdf.set_xy(16, 18)
        pdf.set_text_color(15, 23, 42)  # Slate 900
        pdf.set_font("Helvetica", "B", 15)
        pdf.cell(110, 6, "PROPUESTA DE SERVICIOS", align="L")

        # Metadatos del folio y fecha
        pdf.set_xy(16, 25)
        pdf.set_text_color(100, 116, 139)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(110, 4, f"Folio: {folio}   |   Fecha: {date_str}   |   Vigencia: {validity_days} días", align="L")

        # Información del cliente
        pdf.set_xy(16, 31)
        pdf.set_text_color(30, 41, 59)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.cell(110, 5, f"Cliente: {client_name}", align="L")

        contact_parts = []
        if client_contact:
            contact_parts.append(f"At'n: {client_contact}")
        if client_email:
            contact_parts.append(client_email)
        if client_phone:
            contact_parts.append(client_phone)

        if contact_parts:
            pdf.set_xy(16, 36)
            pdf.set_text_color(71, 85, 105)
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(110, 4, "  |  ".join(contact_parts), align="L")

    def render_table_header(y_pos: float):
        pdf.set_xy(16, y_pos)
        pdf.set_fill_color(15, 23, 42)  # Fondo oscuro cabecera
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)
        
        pdf.cell(10, 7, "#", border=0, align="C", fill=True)
        pdf.cell(94, 7, "CONCEPTO Y ALCANCE", border=0, align="L", fill=True)
        pdf.cell(18, 7, "CANT", border=0, align="C", fill=True)
        pdf.cell(31, 7, "P. UNITARIO", border=0, align="R", fill=True)
        pdf.cell(31, 7, "IMPORTE", border=0, align="R", fill=True)
        return y_pos + 7

    render_page2_header()
    current_y = render_table_header(45)

    # Anchos de columnas
    w_idx = 10
    w_concept = 94
    w_qty = 18
    w_unit = 31
    w_total = 31

    max_content_y = 205.0  # Límite vertical antes de saltar de página para dejar espacio a totales

    for it in items:
        # Calcular altura requerida para el concepto y descripción
        has_desc = bool(it["description"].strip())
        desc_lines = pdf.multi_cell(w_concept, 3.8, it["description"], dry_run=True, output="LINES") if has_desc else []
        desc_h = len(desc_lines) * 3.8 if has_desc else 0.0
        row_h = max(7.0, 5.0 + desc_h + 3.0)

        # Si excede el espacio en página, crear nueva página
        if current_y + row_h > max_content_y:
            pdf.add_page()
            render_page2_header()
            current_y = render_table_header(45)

        # Fondo cebra suave
        if it["idx"] % 2 == 0:
            pdf.set_fill_color(248, 250, 252)
            pdf.rect(16, current_y, 184, row_h, "F")

        # Línea separadora inferior sutil
        pdf.set_draw_color(226, 232, 240)
        pdf.line(16, current_y + row_h, 200, current_y + row_h)

        # Columna #
        pdf.set_xy(16, current_y + 1.5)
        pdf.set_text_color(100, 116, 139)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(w_idx, 5, str(it["idx"]), align="C")

        # Columna CONCEPTO Y ALCANCE
        pdf.set_xy(16 + w_idx + 1, current_y + 1.2)
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(w_concept - 2, 4.5, it["name"][:55], align="L")

        if has_desc:
            pdf.set_xy(16 + w_idx + 1, current_y + 5.5)
            pdf.set_text_color(71, 85, 105)
            pdf.set_font("Helvetica", "", 7.5)
            pdf.multi_cell(w_concept - 2, 3.6, it["description"], align="L")

        # Columna CANT
        pdf.set_xy(16 + w_idx + w_concept, current_y + 1.5)
        pdf.set_text_color(30, 41, 59)
        pdf.set_font("Helvetica", "", 8.5)
        qty_str = f"{it['quantity']:g}"
        pdf.cell(w_qty, 5, qty_str, align="C")

        # Columna P. UNITARIO
        pdf.set_xy(16 + w_idx + w_concept + w_qty, current_y + 1.5)
        pdf.cell(w_unit, 5, format_currency(it["unit_price"]), align="R")

        # Columna IMPORTE
        pdf.set_xy(16 + w_idx + w_concept + w_qty + w_unit, current_y + 1.5)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(w_total, 5, format_currency(it["subtotal"]), align="R")

        current_y += row_h

    # -------------------------------------------------------------
    # SECCIÓN TOTALES Y DATOS BANCARIOS
    # -------------------------------------------------------------
    bottom_start_y = max(current_y + 4, 180.0)

    # Si por alguna razón queda muy pegado al pie con condiciones (Y=242), saltar de página
    if bottom_start_y > 200.0:
        pdf.add_page()
        render_page2_header()
        bottom_start_y = 50.0

    # 1. Caja de Datos Bancarios (Izquierda: X=16 a X=118, ancho 102 mm)
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(16, bottom_start_y, 102, 36, "FD")

    pdf.set_xy(19, bottom_start_y + 2.5)
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(96, 4, "DATOS PARA PAGO POR TRANSFERENCIA (SPEI):", align="L")

    pdf.set_xy(19, bottom_start_y + 7.5)
    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.cell(96, 3.8, f"Banco: {bank_info['bank']}", align="L")

    pdf.set_xy(19, bottom_start_y + 11.5)
    pdf.cell(96, 3.8, f"Beneficiario: {bank_info['beneficiary']}", align="L")

    pdf.set_xy(19, bottom_start_y + 15.5)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(96, 3.8, f"CLABE Interbancaria: {bank_info['clabe']}", align="L")

    pdf.set_xy(19, bottom_start_y + 19.5)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(96, 3.8, f"Concepto de Pago: {folio}", align="L")

    # Notas adicionales si aplican
    pdf.set_xy(19, bottom_start_y + 24.5)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100, 116, 139)
    custom_note = notes if notes else bank_info.get("notes", "")
    pdf.multi_cell(96, 3.2, custom_note[:140], align="L")

    # 2. Caja de Totales (Derecha: X=124 a X=200, ancho 76 mm)
    box_w = 76
    box_x = 124

    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(box_x, bottom_start_y, box_w, 36, "FD")

    # Subtotal
    pdf.set_xy(box_x + 3, bottom_start_y + 2.5)
    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(38, 4.5, "Subtotal:", align="L")
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(32, 4.5, format_currency(subtotal), align="R")

    # IVA
    pdf.set_xy(box_x + 3, bottom_start_y + 7.5)
    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Helvetica", "", 8)
    iva_label = f"I.V.A. ({int(tax_rate * 100)}%):" if apply_tax else "I.V.A.:"
    pdf.cell(38, 4.5, iva_label, align="L")
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 8)
    iva_val_str = format_currency(tax_amount) if apply_tax else "No aplica"
    pdf.cell(32, 4.5, iva_val_str, align="R")

    # Línea divisoria en caja de totales
    pdf.set_draw_color(203, 213, 225)
    pdf.line(box_x + 3, bottom_start_y + 13, box_x + box_w - 3, bottom_start_y + 13)

    # TOTAL NETO
    pdf.set_xy(box_x + 3, bottom_start_y + 14.5)
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(34, 5.5, "TOTAL:", align="L")
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.cell(36, 5.5, format_currency(total), align="R")

    # Anticipo Requerido (50%)
    pdf.set_xy(box_x + 3, bottom_start_y + 22.5)
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(box_x + 2, bottom_start_y + 21.5, box_w - 4, 11, "F")

    pdf.set_text_color(217, 70, 239)  # Magenta/fucsia de marca
    pdf.set_font("Helvetica", "B", 7.5)
    ant_pct_label = f"ANTICIPO REQUERIDO ({int(down_payment_rate * 100)}%):"
    pdf.cell(box_w - 8, 4, ant_pct_label, align="L")

    pdf.set_xy(box_x + 3, bottom_start_y + 26.5)
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(box_w - 8, 4.5, format_currency(down_payment_amount), align="R")

    # -------------------------------------------------------------
    # 2. OVERLAY VECTORIAL CON PYPDF SOBRE LA PLANTILLA BASE
    # -------------------------------------------------------------
    dynamic_pdf_bytes = bytes(pdf.output())
    dynamic_reader = PdfReader(io.BytesIO(dynamic_pdf_bytes))
    template_reader = PdfReader(TEMPLATE_PATH)

    template_page1 = template_reader.pages[0]
    template_page2 = template_reader.pages[1]

    writer = PdfWriter()

    # Página 1 (Portada): template_page1 + dynamic_reader.pages[0]
    cover_page = template_page1
    cover_page.merge_page(dynamic_reader.pages[0])
    writer.add_page(cover_page)

    # Página 2 y siguientes (Detalle):
    # La página 2 del template tiene el logo arriba a la derecha y las condiciones comerciales al pie.
    for i in range(1, len(dynamic_reader.pages)):
        # Clonar la página 2 de la plantilla para cada página de desglose
        detail_template = template_reader.pages[1]
        # Creamos una copia fresca para evitar mutaciones si hay múltiples páginas
        fresh_detail = PdfReader(TEMPLATE_PATH).pages[1]
        fresh_detail.merge_page(dynamic_reader.pages[i])
        writer.add_page(fresh_detail)

    output_stream = io.BytesIO()
    writer.write(output_stream)
    return output_stream.getvalue()
