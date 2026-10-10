import io
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pypdf import PdfReader

from app.services.reconciliation.bbva_parser import (
    parse_flexible_date,
    _parse_num,
    _clean_header
)


KNOWN_PROJECT_TAGS = [
    "DAM", "HEALTHYICE", "VALENCIA", "BOTICA", "SOUL SHINE",
    "PUMPAPA", "IEER", "NI2", "LETRERAMA", "GARI", "JESSICA",
    "UROLOGIA", "ONCOLOGIA", "WHITE CLEAN", "CHILE CHILLON"
]


def _detect_area_project(concepto: str, default_area: Optional[str] = None) -> Optional[str]:
    concepto_up = (concepto or "").upper()
    for tag in KNOWN_PROJECT_TAGS:
        if re.search(r"\b" + re.escape(tag) + r"\b", concepto_up):
            return tag
    return default_area


def _parse_single_comprobante(
    full_text: str,
    filename: str,
    account_rfc: str
) -> List[Dict[str, Any]]:
    """
    Parsea comprobantes individuales de traspaso / transferencia (ej. BBVA Net Cash / Móvil).
    Extrae fecha, importe, concepto de pago, beneficiario, banco destino y clave de rastreo.
    """
    text_clean = full_text.replace("\r", "\n")
    lines = [l.strip() for l in text_clean.split("\n") if l.strip()]

    # 1. Extraer Importe
    monto: Optional[float] = None
    m_importe = re.search(r"(?:Importe|Monto|Cantidad|Total):\s*[$]?\s*([\d,]+\.\d{2})", full_text, re.IGNORECASE)
    if m_importe:
        monto = _parse_num(m_importe.group(1))

    if monto is None:
        for line in lines:
            if any(k in line.lower() for k in ["importe", "monto", "total"]):
                num = _parse_num(line)
                if num and num > 0:
                    monto = num
                    break

    if not monto or monto <= 0:
        return []

    # 2. Extraer Fecha
    fecha_obj: Optional[datetime] = None
    m_fecha_cap = re.search(r"(?:Fecha\s*y\s*Hora\s*de\s*Captura|Fecha\s*de\s*operaci[oó]n|Fecha):\s*(\d{2}[/-]\d{2}[/-]\d{4})", full_text, re.IGNORECASE)
    if m_fecha_cap:
        fecha_obj = parse_flexible_date(m_fecha_cap.group(1))

    if not fecha_obj:
        for line in lines[:15]:
            m_d = re.search(r"\b(\d{2}[/-]\d{2}[/-]\d{2,4})\b", line)
            if m_d:
                cand = parse_flexible_date(m_d.group(1))
                if cand:
                    fecha_obj = cand
                    break

    if not fecha_obj:
        fecha_obj = datetime.now()

    # 3. Extraer Concepto de pago
    concepto_pago = ""
    m_concepto = re.search(r"(?:Concepto\s*de\s*pago|Concepto|Motivo|Descripci[oó]n):\s*([^\n]+)", full_text, re.IGNORECASE)
    if m_concepto:
        concepto_pago = m_concepto.group(1).strip()

    # 4. Extraer Beneficiario
    beneficiario = ""
    m_ben = re.search(r"Datos\s*del\s*beneficiario[^\n]*\n+\s*(?:Nombre:)?\s*([^\n]+)", full_text, re.IGNORECASE)
    if m_ben:
        beneficiario = m_ben.group(1).replace("Nombre:", "").strip()
    if not beneficiario:
        m_ben2 = re.search(r"(?:Beneficiario|Destinatario|A\s*nombre\s*de):\s*([^\n]+)", full_text, re.IGNORECASE)
        if m_ben2:
            beneficiario = m_ben2.group(1).strip()

    # 5. Extraer Banco destino
    banco_destino = ""
    m_banco = re.search(r"(?:Banco\s*destino|Banco\s*receptor|Instituci[oó]n):\s*([^\n]+)", full_text, re.IGNORECASE)
    if m_banco:
        banco_destino = m_banco.group(1).strip()

    # 6. Extraer Clave de rastreo o Folio
    clave_rastreo = ""
    m_rastreo = re.search(r"(?:Clave\s*de\s*rastreo|Rastreo|Folio\s*de\s*internet):\s*([A-Za-z0-9]+)", full_text, re.IGNORECASE)
    if m_rastreo:
        clave_rastreo = m_rastreo.group(1).strip()

    effective_rfc = account_rfc
    if "MEDINA HERNANDEZ ADRIANA" in full_text.upper():
        if account_rfc == "MEHA850118Q96":
            effective_rfc = "MEHA850118Q96"

    parts = []
    if beneficiario:
        parts.append(beneficiario)
    if concepto_pago:
        parts.append(concepto_pago)
    if banco_destino:
        parts.append(banco_destino)
    if clave_rastreo:
        parts.append(f"Rastreo: {clave_rastreo}")

    concepto_final = " - ".join(parts) if parts else f"Traspaso bancario {fecha_obj.strftime('%d/%m/%Y')}"

    tipo = "EGRESO"
    if any(k in full_text.upper() for k in ["DEPOSITO RECIBIDO", "ABONO RECIBIDO", "TRANSFERENCIA RECIBIDA"]):
        tipo = "INGRESO"

    area_proyecto = _detect_area_project(concepto_final)
    periodo_mes = fecha_obj.strftime("%Y-%m")

    date_str = fecha_obj.strftime("%Y-%m-%d")
    hash_seed = f"{effective_rfc}|PDF_COMP|{date_str}|{concepto_final.upper()}|{monto:.2f}|{tipo}|{clave_rastreo}"
    id_transaccion = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()

    return [{
        "account_rfc": effective_rfc,
        "id_transaccion": id_transaccion,
        "banco": "BBVA",
        "fecha": fecha_obj,
        "concepto": concepto_final[:500],
        "monto": round(monto, 2),
        "tipo": tipo,
        "saldo": None,
        "periodo_mes": periodo_mes,
        "area_proyecto": area_proyecto,
        "referencia_rastreo": clave_rastreo or None
    }]


def _parse_tabular_statement(
    pages_text: List[str],
    filename: str,
    account_rfc: str
) -> List[Dict[str, Any]]:
    """
    Parsea estados de cuenta mensuales estructurados en tablas de movimientos continuos.
    """
    transacciones: List[Dict[str, Any]] = []

    for page_idx, page_str in enumerate(pages_text):
        lines = page_str.split("\n")
        for line_idx, line in enumerate(lines):
            line_str = line.strip()
            if not line_str or any(line_str.upper().startswith(k) for k in ["TOTAL", "SALDO INICIAL", "SALDO FINAL", "RESUMEN", "CORTE"]):
                continue

            m_date = re.match(r"^(\d{2}[/-](?:\d{2}|[A-Za-z]{3})(?:[/-]\d{2,4})?)\b", line_str)
            if not m_date:
                continue

            raw_date = m_date.group(1)
            fecha_obj = parse_flexible_date(raw_date)
            if not fecha_obj:
                continue

            rest_of_line = line_str[len(raw_date):].strip()
            num_tokens = re.findall(r"[-$]?\s*[\d,]+\.\d{2}", rest_of_line)
            if not num_tokens:
                continue

            last_num_match = re.search(r"([-$]?\s*[\d,]+\.\d{2}.*)$", rest_of_line)
            concepto = rest_of_line[:last_num_match.start()].strip() if last_num_match else rest_of_line

            if not concepto or len(concepto) < 3:
                continue

            monto_val = _parse_num(num_tokens[0])
            if monto_val is None or monto_val == 0:
                continue

            tipo = "EGRESO"
            if monto_val > 0 and any(k in concepto.upper() for k in ["ABONO", "DEPOSITO", "TRASPASO REC", "TRANSFERENCIA REC"]):
                tipo = "INGRESO"
            elif monto_val < 0:
                tipo = "EGRESO"
                monto_val = abs(monto_val)

            saldo_val = None
            if len(num_tokens) >= 2:
                saldo_val = _parse_num(num_tokens[-1])

            periodo_mes = fecha_obj.strftime("%Y-%m")
            area_proyecto = _detect_area_project(concepto)

            date_str = fecha_obj.strftime("%Y-%m-%d")
            hash_seed = f"{account_rfc}|PDF_STMT|{date_str}|{concepto.upper()}|{monto_val:.2f}|{tipo}|{page_idx}-{line_idx}"
            id_transaccion = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()

            transacciones.append({
                "account_rfc": account_rfc,
                "id_transaccion": id_transaccion,
                "banco": "BBVA",
                "fecha": fecha_obj,
                "concepto": concepto[:500],
                "monto": round(monto_val, 2),
                "tipo": tipo,
                "saldo": saldo_val,
                "periodo_mes": periodo_mes,
                "area_proyecto": area_proyecto,
                "referencia_rastreo": None
            })

    return transacciones


def parse_bank_pdf_statement(
    file_content: bytes,
    filename: str,
    account_rfc: str = "DEGF851127TK1"
) -> List[Dict[str, Any]]:
    """
    Punto de entrada principal para extraer transacciones bancarias desde documentos PDF.
    """
    if not file_content:
        raise ValueError("El archivo PDF bancario está vacío.")

    try:
        reader = PdfReader(io.BytesIO(file_content))
    except Exception as e:
        raise ValueError(f"No se pudo interpretar el archivo PDF: {e}")

    if not reader.pages:
        raise ValueError("El documento PDF no contiene páginas.")

    pages_text: List[str] = []
    full_text_parts: List[str] = []

    for page in reader.pages:
        txt = page.extract_text() or ""
        pages_text.append(txt)
        full_text_parts.append(txt)

    full_text = "\n".join(full_text_parts)
    full_text_up = full_text.upper()

    is_comprobante = any(k in full_text_up for k in [
        "RESULTADO DEL TRASPASO", "COMPROBANTE", "DETALLE DE LA TRANSFERENCIA",
        "DATOS DEL BENEFICIARIO", "CUENTA DE RETIRO", "FORMA DE DEPÓSITO",
        "FORMA DE DEPOSITO", "CLAVE DE RASTREO"
    ])

    if is_comprobante:
        txs = _parse_single_comprobante(full_text, filename, account_rfc)
        if txs:
            return txs

    txs_tab = _parse_tabular_statement(pages_text, filename, account_rfc)
    if txs_tab:
        return txs_tab

    txs_fallback = _parse_single_comprobante(full_text, filename, account_rfc)
    if txs_fallback:
        return txs_fallback

    raise ValueError(
        "No se encontraron transacciones bancarias legibles en el PDF. "
        "Asegúrese de que sea un estado de cuenta o comprobante oficial de BBVA u otro banco."
    )
