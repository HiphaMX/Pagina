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

    if hasattr(quotation_data, "model_dump"):
        quotation_data = quotation_data.model_dump()

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

    raw_require_down_payment = quotation_data.get("require_down_payment")
    down_payment_rate = float(quotation_data.get("down_payment_rate", 0.50))
    if raw_require_down_payment is not None:
        require_down_payment = bool(raw_require_down_payment) and (down_payment_rate > 0.0)
    else:
        require_down_payment = (down_payment_rate > 0.0)

    if not require_down_payment:
        down_payment_rate = 0.0
        down_payment_amount = 0.0
    else:
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

        # Cubrir preventivamente el pie original de la plantilla
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(14, 202, 188, 73, style="F")

    def render_page2_footer(footer_y: float = 205.0):
        # Cubrir fondo inferior de la plantilla original para ocultar textos estáticos previos
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(14, footer_y - 3, 188, 75, style="F")

        width_limit = 184

        # 1. En primer lugar: CONDICIONES COMERCIALES (cargadas a la izquierda, tipografía mejorada)
        pdf.set_xy(16, footer_y)
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Helvetica", "B", 8.2)
        pdf.cell(width_limit, 4.0, "CONDICIONES COMERCIALES:", align="L")

        pdf.set_text_color(71, 85, 105)
        pdf.set_font("Helvetica", "", 7.5)

        conditions_lines = []

        # 1. Anticipo o confirmación de tiempo de entrega
        if require_down_payment and down_payment_rate > 0:
            pct_int = int(round(down_payment_rate * 100))
            conditions_lines.append(f"- Se requiere del {pct_int}% como anticipo para iniciar, el tiempo de entrega se confirma al contratar.")
        else:
            conditions_lines.append("- Se requiere OC para iniciar con el trabajo y confirmar el tiempo de entrega.")

        # 2. Conceptos no incluidos
        conditions_lines.append("- Cualquier concepto no incluido en la presente cotización deberá cotizarse por separado.")

        # 3. IVA: Si NO está habilitada la opción de IVA, se mantiene la leyenda:
        # "- Los precios mostrados no incluyen IVA."
        # Si sí está habilitada y reflejada en la cotización, se elimina ese texto de las condiciones comerciales.
        if not apply_tax:
            conditions_lines.append("- Los precios mostrados no incluyen IVA.")

        # 4. Vigencia
        conditions_lines.append(f"- Cotización válida por {validity_days} días naturales.")

        cond_y = footer_y + 4.8
        for line in conditions_lines:
            pdf.set_xy(16, cond_y)
            pdf.cell(width_limit, 3.8, line, align="L")
            cond_y += 4.0

        # 2. Debajo: DATOS BANCARIOS Y FISCALES (cargados a la izquierda)
        bank_y = max(cond_y + 3.5, footer_y + 24.5)
        pdf.set_xy(16, bank_y)
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Helvetica", "B", 8.2)
        pdf.cell(width_limit, 4.0, "DATOS BANCARIOS Y FISCALES:", align="L")

        pdf.set_xy(16, bank_y + 4.8)
        pdf.set_font("Helvetica", "B", 7.8)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(width_limit, 3.8, beneficiary_name, align="L")

        pdf.set_xy(16, bank_y + 8.8)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(width_limit, 3.8, rfc_regime, align="L")

        pdf.set_xy(16, bank_y + 12.8)
        pdf.cell(width_limit, 3.8, bank_account, align="L")

        pdf.set_xy(16, bank_y + 16.8)
        pdf.cell(width_limit, 3.8, contact_bank, align="L")

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
    # Colocado por regla debajo (dejando un espacio en blanco) del último item cotizado
    # -------------------------------------------------------------
    totals_start_y = current_y + 8.0

    # Si por acumulación de filas queda sin espacio en la página, saltar a nueva página
    if totals_start_y > 172.0:
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
    curr_total_y = totals_start_y

    # Subtotal
    pdf.set_xy(box_x, curr_total_y)
    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.cell(38, 4.5, "Subtotal:", align="L")
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.cell(38, 4.5, format_currency(subtotal), align="R")
    curr_total_y += 5.5

    # IVA (solo si apply_tax es True; si está deshabilitado no aparece en la cotización)
    if apply_tax:
        pdf.set_xy(box_x, curr_total_y)
        pdf.set_text_color(71, 85, 105)
        pdf.set_font("Helvetica", "", 8.5)
        iva_label = f"I.V.A. ({int(tax_rate * 100)}%):"
        pdf.cell(38, 4.5, iva_label, align="L")
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(38, 4.5, format_currency(tax_amount), align="R")
        curr_total_y += 6.5

    # TOTAL
    pdf.set_xy(box_x, curr_total_y)
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 10.0)
    pdf.cell(34, 5.5, "TOTAL:", align="L")
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.cell(42, 5.5, format_currency(total), align="R")
    curr_total_y += 7.0

    # Anticipo Requerido en Cyan Hipha (solo si require_down_payment es True y down_payment_rate > 0)
    if require_down_payment and down_payment_rate > 0:
        pdf.set_xy(box_x, curr_total_y)
        pdf.set_text_color(0, 180, 216)  # Cyan oficial de marca Hipha
        pdf.set_font("Helvetica", "B", 8.0)
        pct_int = int(round(down_payment_rate * 100))
        ant_pct_label = f"ANTICIPO REQUERIDO ({pct_int}%):"
        pdf.cell(38, 4.5, ant_pct_label, align="L")
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.cell(38, 4.5, format_currency(down_payment_amount), align="R")
        curr_total_y += 6.5

    # Footer institucional: Condiciones Comerciales en 1er lugar y Datos Bancarios debajo
    footer_pos_y = max(curr_total_y + 10.0, 205.0)
    render_page2_footer(footer_pos_y)

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
