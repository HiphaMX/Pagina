import io
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pypdf import PdfReader

from app.services.reconciliation.bbva_parser import (
    parse_flexible_date,
    _parse_num,
    _clean_header,
    SPANISH_MONTHS
)


PROJECT_KEYWORD_MAP = {
    "DAM": "DAM",
    "PISOS": "DAM",
    "AZULEJERO": "DAM",
    "HEALTHYICE": "HEALTHYICE",
    "AXIS": "HEALTHYICE",
    "VALENCIA": "VALENCIA",
    "BOTICA": "BOTICA",
    "SOUL SHINE": "SOUL SHINE",
    "PUMPAPA": "PUMPAPA",
    "IEER": "IEER",
    "NI2": "NI2",
    "LETRERAMA": "LETRERAMA",
    "GARI": "GARI",
    "JESSICA": "JESSICA",
    "UROLOGIA": "UROLOGIA",
    "ONCOLOGIA": "ONCOLOGIA",
    "WHITE CLEAN": "WHITE CLEAN",
    "CHILE CHILLON": "CHILE CHILLON"
}


def _detect_area_project(concepto: str, default_area: Optional[str] = None) -> Optional[str]:
    concepto_up = (concepto or "").upper()
    for kw, project_name in PROJECT_KEYWORD_MAP.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", concepto_up):
            return project_name
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

def _parse_bbva_pyme_statement(
    full_text: str,
    filename: str,
    account_rfc: str
) -> List[Dict[str, Any]]:
    """
    Parsea estados de cuenta mensuales estructurados de BBVA (ej. Maestra PyME BBVA).
    Extrae periodo, RFC, titular, y todas las filas de la sección 'Detalle de Movimientos Realizados'.
    """
    # 1. Extraer año y periodo del encabezado
    m_periodo = re.search(r'Periodo\s+DEL\s+\d{2}/\d{2}/(\d{4})\s+AL\s+\d{2}/\d{2}/(\d{4})', full_text, re.IGNORECASE)
    year = int(m_periodo.group(2)) if m_periodo else datetime.now().year

    # 2. Extraer RFC si existe en el estado de cuenta
    m_rfc = re.search(r'R\.?F\.?C\.?\s+([A-Z0-9]{12,13})', full_text)
    doc_rfc = m_rfc.group(1).strip() if m_rfc else None
    effective_rfc = account_rfc or doc_rfc or "DEGF851127TK1"

    lines = full_text.split('\n')
    in_movs = False
    txs: List[Dict[str, Any]] = []
    current_tx: Optional[Dict[str, Any]] = None

    for idx, line in enumerate(lines):
        line_str = line.strip()
        if 'Detalle de Movimientos Realizados' in line_str:
            in_movs = True
            continue
        if in_movs and any(line_str.startswith(k) for k in [
            'Total de Movimientos', 'TOTAL MOVIMIENTOS', 'Comportamiento',
            'Cuadro resumen', 'Glosario de Abreviaturas'
        ]):
            in_movs = False
            if current_tx:
                txs.append(current_tx)
                current_tx = None
            continue

        if not in_movs:
            continue

        # Detectar inicio de movimiento: ej. 22/JUL 22/JUL o 22/07 22/07 o 22/JUL
        m_row = re.match(r'^(\d{2}/[A-Za-z]{3}|\d{2}/\d{2})(?:\s+(\d{2}/[A-Za-z]{3}|\d{2}/\d{2}))?\s+(.+)$', line_str)
        if m_row:
            if current_tx:
                txs.append(current_tx)
                current_tx = None

            oper_date_str = m_row.group(1)
            rest = m_row.group(3).strip()

            # Extraer números al final
            nums = re.findall(r'[\d,]+\.\d{2}', rest)
            concept_part = rest
            for n in nums:
                last_pos = concept_part.rfind(n)
                if last_pos != -1:
                    concept_part = concept_part[:last_pos].strip()

            monto = 0.0
            tipo = 'EGRESO'
            saldo = None
            if len(nums) >= 3:
                # 3 números: Abono, Saldo Operación, Saldo Liquidación
                monto = _parse_num(nums[0])
                saldo = _parse_num(nums[-1])
                tipo = 'INGRESO'
            elif len(nums) == 1:
                # 1 número: Cargo
                monto = _parse_num(nums[0])
                tipo = 'EGRESO'
            elif len(nums) == 2:
                # 2 números: Cargo y Saldo
                monto = _parse_num(nums[0])
                saldo = _parse_num(nums[1])
                tipo = 'EGRESO'

            if not monto or monto <= 0:
                continue

            # Parsear fecha
            parts_d = oper_date_str.split('/')
            day = int(parts_d[0])
            mon_token = parts_d[1].upper()
            mon_num = int(SPANISH_MONTHS.get(mon_token, mon_token))
            fecha_obj = datetime(year, mon_num, day)

            current_tx = {
                'fecha': fecha_obj,
                'concepto': concept_part,
                'monto': round(monto, 2),
                'tipo': tipo,
                'saldo': saldo,
                'periodo_mes': f'{year}-{mon_num:02d}'
            }
        elif current_tx and line_str and not line_str.startswith('OPER LIQ') and not line_str.startswith('FECHA') and not line_str.startswith('SALDO'):
            # Línea subordinada (referencia, guía, BNET, concepto adicional)
            current_tx['concepto'] += ' - ' + line_str

    if current_tx:
        txs.append(current_tx)

    result: List[Dict[str, Any]] = []
    for idx, t in enumerate(txs):
        concepto_final = t['concepto'][:500]
        area_proyecto = _detect_area_project(concepto_final)
        periodo_mes = t['periodo_mes']
        fecha_obj = t['fecha']
        date_str = fecha_obj.strftime("%Y-%m-%d")
        saldo_token = f"{t['saldo']:.2f}" if t['saldo'] is not None else f"row-{idx}"
        hash_seed = f"{effective_rfc}|BBVA_PYME|{date_str}|{concepto_final.upper()}|{t['monto']:.2f}|{t['tipo']}|{saldo_token}"
        id_transaccion = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()

        result.append({
            "account_rfc": effective_rfc,
            "id_transaccion": id_transaccion,
            "banco": "BBVA",
            "fecha": fecha_obj,
            "concepto": concepto_final,
            "monto": t['monto'],
            "tipo": t['tipo'],
            "saldo": t['saldo'],
            "periodo_mes": periodo_mes,
            "area_proyecto": area_proyecto,
            "referencia_rastreo": None
        })

    return result


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

    # 1. Detectar si es Estado de Cuenta BBVA (ej. PyME con Detalle de Movimientos)
    if "DETALLE DE MOVIMIENTOS" in full_text_up or "MAESTRA PYME" in full_text_up or "ESTADO DE CUENTA" in full_text_up:
        txs_pyme = _parse_bbva_pyme_statement(full_text, filename, account_rfc)
        if txs_pyme:
            return txs_pyme

    # 2. Detectar si es un comprobante de operación individual / transferencia / traspaso
    is_comprobante = any(k in full_text_up for k in [
        "RESULTADO DEL TRASPASO", "COMPROBANTE", "DETALLE DE LA TRANSFERENCIA",
        "DATOS DEL BENEFICIARIO", "CUENTA DE RETIRO", "FORMA DE DEPÓSITO",
        "FORMA DE DEPOSITO", "CLAVE DE RASTREO"
    ])

    if is_comprobante:
        txs = _parse_single_comprobante(full_text, filename, account_rfc)
        if txs:
            return txs

    # 3. Tabular statement genérico
    txs_tab = _parse_tabular_statement(pages_text, filename, account_rfc)
    if txs_tab:
        return txs_tab

    # 4. Fallback comprobante
    txs_fallback = _parse_single_comprobante(full_text, filename, account_rfc)
    if txs_fallback:
        return txs_fallback

    raise ValueError(
        "No se encontraron transacciones bancarias legibles en el PDF. "
        "Asegúrese de que sea un estado de cuenta o comprobante oficial de BBVA u otro banco."
    )
