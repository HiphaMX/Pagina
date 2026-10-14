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
    "beneficiary": "FRANCISCO DE JESUS DELGADILLO GARCIA",
    "rfc_regime": "RFC: DEGF851127TK1 | Régimen Simplificado de Confianza",
    "bank_account_clabe": "BBVA Bancomer | Cuenta: 0476919804 | Clabe: 0123 2000 4769 1980 40",
    "contact": "Teléfono: 333 6762545 | Email: factura@hipha.mx",
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
    beneficiary_name = sanitize_text(str(bank_info.get("beneficiary") or "FRANCISCO DE JESUS DELGADILLO GARCIA"))
    rfc_regime = sanitize_text(str(bank_info.get("rfc_regime") or "RFC: DEGF851127TK1 | Régimen Simplificado de Confianza"))
    bank_account = sanitize_text(str(bank_info.get("bank_account_clabe") or "BBVA Bancomer | Cuenta: 0476919804 | Clabe: 0123 2000 4769 1980 40"))
    contact_bank = sanitize_text(str(bank_info.get("contact") or "Teléfono: 333 6762545 | Email: factura@hipha.mx"))

    folio = sanitize_text(str(quotation_data.get("folio") or "HIP-2026-0001"))
    client_name = sanitize_text(str(quotation_data.get("client_name") or "Cliente").strip())
    client_contact = sanitize_text(str(quotation_data.get("client_contact") or "").strip())
    client_email = sanitize_text(str(quotation_data.get("client_email") or "").strip())
    client_phone = sanitize_text(str(quotation_data.get("client_phone") or "").strip())
    notes = sanitize_text(str(quotation_data.get("notes") or "").strip())
    validity_days = quotation_data.get("validity_days") or 30

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
        name = sanitize_text(str(it.get("name") or f"Concepto {idx}"))
        desc = sanitize_text(str(it.get("description") or ""))
        qty = float(it.get("quantity") or 1.0)
        unit_price = float(it.get("unit_price") or 0.0)
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

    # Solamente la URL institucional al pie de la portada oficial
    pdf.set_xy(16, 258)
    pdf.set_text_color(0, 229, 255)  # Cyan #00e5ff de Hipha sobre fondo azul oscuro
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(184, 6, "WWW.HIPHA.MX", align="C")

    # -------------------------------------------------------------
    # PÁGINA 2+: PROPUESTA Y DESGLOSE
    # -------------------------------------------------------------
    pdf.add_page()

    def render_page2_header():
        # Título en esquina superior izquierda: Nombre del cliente (ej. AIO Constructora)
        pdf.set_xy(16, 17)
        pdf.set_text_color(15, 23, 42)  # Slate 900
        pdf.set_font("Helvetica", "B", 15)
        pdf.cell(115, 6, client_name, align="L")

        # Metadatos del folio, fecha y vigencia
        pdf.set_xy(16, 24.5)
        pdf.set_text_color(100, 116, 139)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(115, 4, f"Folio: {folio}   |   Fecha: {date_str}   |   Vigencia: {validity_days} días", align="L")

        # Contacto: At'n con tamaño de letra 9.5 (el tamaño que antes tenía Cliente: ...)
        contact_parts = []
        if client_contact:
            contact_parts.append(f"At'n: {client_contact}")
        if client_email:
            contact_parts.append(client_email)
        if client_phone:
            contact_parts.append(client_phone)

        if contact_parts:
            pdf.set_xy(16, 31)
            pdf.set_text_color(30, 41, 59)
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.cell(130, 5, " | ".join(contact_parts), align="L")

        # Footer institucional balanceado a 2 columnas (Datos Bancarios + Condiciones Comerciales)
        render_page2_footer()

    def render_page2_footer():
        footer_y = 239.0

        # Cubrir fondo inferior de la plantilla (reemplaza las condiciones viejas de gran tamaño)
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(14, 235, 188, 38, style="F")

        # Columna Izquierda: Datos Bancarios y Fiscales (X=16 a X=104, ancho 88 mm)
        pdf.set_xy(16, footer_y)
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Helvetica", "B", 7.0)
        pdf.cell(88, 3.5, "DATOS BANCARIOS Y FISCALES:", align="L")

        pdf.set_xy(16, footer_y + 4.2)
        pdf.set_font("Helvetica", "B", 6.8)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(88, 3.2, beneficiary_name, align="L")

        pdf.set_xy(16, footer_y + 7.8)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(88, 3.2, rfc_regime, align="L")

        pdf.set_xy(16, footer_y + 11.4)
        pdf.cell(88, 3.2, bank_account, align="L")

        pdf.set_xy(16, footer_y + 15.0)
        pdf.cell(88, 3.2, contact_bank, align="L")

        # Columna Derecha: Condiciones Comerciales (X=112 a X=200, ancho 88 mm)
        pdf.set_xy(112, footer_y)
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Helvetica", "B", 7.0)
        pdf.cell(88, 3.5, "CONDICIONES COMERCIALES:", align="L")

        pdf.set_text_color(71, 85, 105)
        pdf.set_font("Helvetica", "", 6.5)

        pdf.set_xy(112, footer_y + 4.2)
        pdf.cell(88, 3.2, f"- Se requiere del {int(down_payment_rate * 100)}% como anticipo para iniciar el proyecto.", align="L")

        pdf.set_xy(112, footer_y + 7.8)
        pdf.cell(88, 3.2, "- Cualquier concepto no incluido se cotiza por separado.", align="L")

        pdf.set_xy(112, footer_y + 11.4)
        iva_cond = "- Los precios mostrados no incluyen IVA." if not apply_tax else "- Precios en moneda nacional (MXN) con desglose de impuestos."
        pdf.cell(88, 3.2, iva_cond, align="L")

        pdf.set_xy(112, footer_y + 15.0)
        pdf.cell(88, 3.2, f"- Cotización válida por {validity_days} días naturales.", align="L")

    def render_table_header(y_pos: float):
        # Fondo redondeado azul marino para el encabezado
        pdf.set_fill_color(15, 23, 42)
        pdf.rect(16, y_pos, 184, 7.5, style="F", round_corners=True, corner_radius=2.2)

        pdf.set_xy(16, y_pos)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)
        
        pdf.cell(10, 7.5, "#", border=0, align="C", fill=False)
        pdf.cell(94, 7.5, "CONCEPTO Y ALCANCE", border=0, align="L", fill=False)
        pdf.cell(18, 7.5, "CANT", border=0, align="C", fill=False)
        # Recorridos a la izquierda / centrados en su columna
        pdf.cell(31, 7.5, "P. UNITARIO", border=0, align="C", fill=False)
        pdf.cell(31, 7.5, "IMPORTE", border=0, align="C", fill=False)
        return y_pos + 7.5

    render_page2_header()
    # Espacio en blanco generoso hacia abajo antes de los encabezados (Y=51)
    current_y = render_table_header(51)

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
            current_y = render_table_header(51)

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
        pdf.cell(w_unit - 3, 5, format_currency(it["unit_price"]), align="R")

        # Columna IMPORTE
        pdf.set_xy(16 + w_idx + w_concept + w_qty + w_unit, current_y + 1.5)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(w_total - 3, 5, format_currency(it["subtotal"]), align="R")

        current_y += row_h

    # -------------------------------------------------------------
    # SECCIÓN TOTALES Y OBSERVACIONES
    # -------------------------------------------------------------
    totals_start_y = max(current_y + 6, 145.0)

    # Si por alguna razón queda muy pegado al pie (Y=235), saltar de página
    if totals_start_y > 195.0:
        pdf.add_page()
        render_page2_header()
        totals_start_y = 55.0

    # Notas u observaciones opcionales en el lado izquierdo
    if notes:
        pdf.set_xy(16, totals_start_y)
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.cell(90, 4.0, "NOTAS / OBSERVACIONES:", align="L")

        pdf.set_xy(16, totals_start_y + 4.8)
        pdf.set_font("Helvetica", "I", 7.0)
        pdf.set_text_color(100, 116, 139)
        pdf.multi_cell(90, 3.3, notes[:220], align="L")

    # Desglose de Totales (Derecha: X=124 a X=200, ancho 76 mm)
    box_w = 76
    box_x = 124

    # Subtotal
    pdf.set_xy(box_x, totals_start_y)
    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.cell(38, 4.5, "Subtotal:", align="L")
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.cell(38, 4.5, format_currency(subtotal), align="R")

    # IVA
    pdf.set_xy(box_x, totals_start_y + 5.5)
    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Helvetica", "", 8.5)
    iva_label = f"I.V.A. ({int(tax_rate * 100)}%):" if apply_tax else "I.V.A.:"
    pdf.cell(38, 4.5, iva_label, align="L")
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 8.5)
    iva_val_str = format_currency(tax_amount) if apply_tax else "No aplica"
    pdf.cell(38, 4.5, iva_val_str, align="R")

    # TOTAL
    pdf.set_xy(box_x, totals_start_y + 12.0)
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 10.0)
    pdf.cell(34, 5.5, "TOTAL:", align="L")
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.cell(42, 5.5, format_currency(total), align="R")

    # Anticipo Requerido (50%) en Cyan Hipha
    pdf.set_xy(box_x, totals_start_y + 19.0)
    pdf.set_text_color(0, 180, 216)  # Cyan oficial de marca Hipha
    pdf.set_font("Helvetica", "B", 8.0)
    ant_pct_label = f"ANTICIPO REQUERIDO ({int(down_payment_rate * 100)}%):"
    pdf.cell(38, 4.5, ant_pct_label, align="L")
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(38, 4.5, format_currency(down_payment_amount), align="R")

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
