import io
import csv
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import openpyxl


SPANISH_MONTHS = {
    'ENERO': '01', 'ENE': '01',
    'FEBRERO': '02', 'FEB': '02',
    'MARZO': '03', 'MAR': '03',
    'ABRIL': '04', 'ABR': '04',
    'MAYO': '05', 'MAY': '05',
    'JUNIO': '06', 'JUN': '06',
    'JULIO': '07', 'JUL': '07',
    'AGOSTO': '08', 'AGO': '08',
    'SEPTIEMBRE': '09', 'SETIEMBRE': '09', 'SEP': '09', 'SET': '09',
    'OCTUBRE': '10', 'OCT': '10',
    'NOVIEMBRE': '11', 'NOV': '11',
    'DICIEMBRE': '12', 'DIC': '12'
}


def _clean_header(h: Any) -> str:
    s = str(h or "").strip().lower()
    s = s.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    return s


def _parse_num(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s.upper() in ["NAN", "NONE", "NULL", "-", "--", "N/A"]:
        return None

    is_negative = False
    s_upper = s.upper()

    # Contabilidad: montos negativos entre paréntesis (150.00)
    if "(" in s and ")" in s:
        is_negative = True
        s = s.replace("(", "").replace(")", "")

    # Sufijos bancarios DB (Débito) / CR (Crédito)
    if "DB" in s_upper or "DR" in s_upper:
        is_negative = True
        s = re.sub(r'\b(DB|DR)\b', '', s, flags=re.IGNORECASE)
    if "CR" in s_upper:
        s = re.sub(r'\bCR\b', '', s, flags=re.IGNORECASE)

    s = s.replace("$", "").replace("MXN", "").replace("USD", "").replace(" ", "").strip()
    if not s:
        return None

    if s.startswith("-"):
        is_negative = True
        s = s[1:].strip()
    elif s.endswith("-"):
        is_negative = True
        s = s[:-1].strip()

    # Formatos decimales: europeo/mexicano (1.250,50 vs 1,250.50 vs 1250,50)
    if "." in s and "," in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) in (1, 2):
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")

    try:
        num = float(s)
        return -num if is_negative else num
    except (ValueError, TypeError):
        return None


def parse_flexible_date(val: Any) -> Optional[datetime]:
    """
    Parsea fechas provenientes de extractos bancarios en formatos numéricos
    (DD/MM/YYYY, YYYY-MM-DD, DD-MM-YY) o con nombres de meses en español (01/AGO/2026, 15-AGO-26).
    """
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    if hasattr(val, "date") and callable(getattr(val, "date")):
        d = val.date()
        return datetime(d.year, d.month, d.day)

    s = str(val).strip()
    if not s:
        return None

    # Intentar formatos ISO y numéricos directos
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"]:
        try:
            return datetime.strptime(s[:19] if " " in s else s[:10], fmt)
        except ValueError:
            continue

    # Normalizar meses en español (ej. AGO, AGOSTO, ENE, DIC)
    s_upper = s.upper()
    for m_name, m_num in SPANISH_MONTHS.items():
        if m_name in s_upper:
            s_upper = re.sub(r'[\b\-_/]' + m_name + r'[\b\-_/]', f'/{m_num}/', s_upper)
            s_upper = s_upper.replace(m_name, m_num)
            break

    clean_s = s_upper.replace('.', '').replace('-', '/').strip()
    parts = clean_s.split()[0].split('/')
    if len(parts) == 3:
        p0, p1, p2 = parts[0], parts[1], parts[2]
        if len(p0) == 4:  # YYYY/MM/DD
            clean_s = f"{p0}-{p1.zfill(2)}-{p2.zfill(2)}"
        else:  # DD/MM/YYYY o DD/MM/YY
            year = ("20" + p2) if len(p2) == 2 else p2
            clean_s = f"{year}-{p1.zfill(2)}-{p0.zfill(2)}"
        try:
            return datetime.strptime(clean_s, "%Y-%m-%d")
        except Exception:
            pass

    return None


# Retrocompatibilidad
_parse_date = parse_flexible_date


def _detect_delimiter(text: str) -> str:
    """
    Determina de manera robusta el delimitador CSV (, ; \t |),
    incluso si hay líneas de metadatos o preámbulos en el archivo.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ','

    candidates = [',', ';', '\t', '|']
    scores = {c: 0 for c in candidates}

    # Evaluar las primeras 40 líneas
    for line in lines[:40]:
        for c in candidates:
            cnt = line.count(c)
            if cnt >= 2:
                scores[c] += cnt

    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best

    try:
        sample = text[:4096]
        return csv.Sniffer().sniff(sample, delimiters=',;\t|').delimiter
    except Exception:
        return ','


def parse_bbva_statement(file_content: bytes, filename: str, account_rfc: str = "DEGF851127TK1") -> List[Dict[str, Any]]:
    """
    Lee y normaliza un archivo de estado de cuenta o movimientos descargado de BBVA México
    (formato .csv, .xlsx o .xls).
    
    Genera un hash determinista único (SHA-256) por cada transacción para prevenir duplicados.
    Maneja preámbulos de metadatos, múltiples delimitadores, fechas en español y montos contables.
    """
    if not file_content:
        raise ValueError("El archivo de estado de cuenta está vacío.")

    filename_lower = filename.lower()
    rows: List[List[Any]] = []

    if filename_lower.endswith(".csv"):
        decoded_text: Optional[str] = None
        for encoding in ["utf-8-sig", "utf-8", "latin-1", "cp1252", "iso-8859-1"]:
            try:
                decoded_text = file_content.decode(encoding)
                break
            except Exception:
                continue

        if not decoded_text:
            raise ValueError("No se pudo leer el archivo CSV de BBVA con ninguna codificación estándar.")

        delim = _detect_delimiter(decoded_text)
        reader = csv.reader(io.StringIO(decoded_text), delimiter=delim)
        rows = [list(r) for r in reader if any(str(field).strip() for field in r)]

        if not rows:
            raise ValueError("El archivo CSV de BBVA está vacío.")
    elif filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls"):
        try:
            wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True)
            sheet = wb.active
            rows = [list(r) for r in sheet.iter_rows(values_only=True) if any(c is not None for c in r)]
        except Exception as e:
            raise ValueError(f"Error leyendo archivo Excel de BBVA: {e}")
    else:
        raise ValueError("Formato de archivo no soportado. Debe ser .csv, .xlsx o .xls.")

    if not rows:
        raise ValueError("El archivo de estado de cuenta no contiene renglones válidos.")

    # Buscar el renglón de encabezados dentro de los primeros 40 renglones
    header_row_idx = None
    headers: List[str] = []

    for idx, r in enumerate(rows[:40]):
        cleaned_r = [_clean_header(c) for c in r]
        has_date = any(any(k in c for k in ["fecha", "f. oper", "f oper", "f. valor", "f valor", "operacion", "dia"]) for c in cleaned_r)
        has_other = any(any(k in c for k in [
            "concepto", "descripci", "detalle", "motivo", "movimiento", "referencia",
            "cargo", "retiro", "debito", "egreso", "salida",
            "abono", "deposito", "credito", "ingreso", "entrada",
            "importe", "monto", "saldo", "balance"
        ]) for c in cleaned_r)

        if has_date and has_other and len(cleaned_r) >= 2:
            header_row_idx = idx
            headers = cleaned_r
            break

    if header_row_idx is None:
        header_row_idx = 0
        headers = [_clean_header(c) for c in rows[0]]

    # Mapeo flexible de columnas comunes en exportaciones BBVA
    col_fecha_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["fecha", "f. oper", "f oper", "f. valor", "f valor", "operacion", "dia"])), None)
    col_concepto_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["concepto", "descripci", "detalle", "motivo", "movimiento", "referencia", "glosa", "leyenda"])), None)
    col_cargo_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["cargo", "retiro", "debito", "salida", "egreso", "disposicion"])), None)
    col_abono_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["abono", "deposito", "credito", "entrada", "ingreso"])), None)
    col_saldo_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["saldo", "balance"])), None)

    col_monto_unico_idx = None
    if col_cargo_idx is None and col_abono_idx is None:
        col_monto_unico_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["importe", "monto", "cantidad", "valor"])), None)

    if col_fecha_idx is None or col_concepto_idx is None or (col_cargo_idx is None and col_abono_idx is None and col_monto_unico_idx is None):
        raise ValueError(
            f"Estructura no reconocida de BBVA. Columnas detectadas: {headers}. "
            "Se requiere al menos Fecha, Concepto y Cargo/Abono (o Importe)."
        )

    transacciones: List[Dict[str, Any]] = []

    for idx, row in enumerate(rows[header_row_idx + 1:], start=header_row_idx + 1):
        if col_fecha_idx >= len(row) or col_concepto_idx >= len(row):
            continue

        raw_fecha_val = row[col_fecha_idx]
        fecha_obj = parse_flexible_date(raw_fecha_val)
        if not fecha_obj:
            continue

        concepto = str(row[col_concepto_idx] or "").strip()
        if not concepto:
            for c_idx, cell in enumerate(row):
                if c_idx not in [col_fecha_idx, col_cargo_idx, col_abono_idx, col_saldo_idx, col_monto_unico_idx]:
                    cand = str(cell or "").strip()
                    if len(cand) >= 3 and _parse_num(cand) is None:
                        concepto = cand
                        break

        concepto_up = concepto.upper()
        if not concepto or any(concepto_up.startswith(k) for k in ["TOTAL", "SALDO INICIAL", "SALDO FINAL", "RESUMEN", "CORTE"]):
            continue

        cargo = 0.0
        abono = 0.0

        if col_monto_unico_idx is not None and col_monto_unico_idx < len(row):
            val_num = _parse_num(row[col_monto_unico_idx])
            if val_num is None or val_num == 0:
                continue
            if val_num < 0:
                cargo = abs(float(val_num))
            else:
                abono = float(val_num)
        else:
            if col_cargo_idx is not None and col_cargo_idx < len(row):
                c_num = _parse_num(row[col_cargo_idx])
                if c_num is not None:
                    cargo = abs(float(c_num))

            if col_abono_idx is not None and col_abono_idx < len(row):
                a_num = _parse_num(row[col_abono_idx])
                if a_num is not None:
                    abono = abs(float(a_num))

        saldo = None
        if col_saldo_idx is not None and col_saldo_idx < len(row):
            s_num = _parse_num(row[col_saldo_idx])
            if s_num is not None:
                saldo = round(float(s_num), 2)

        if cargo > 0:
            monto = round(cargo, 2)
            tipo = "EGRESO"
        elif abono > 0:
            monto = round(abono, 2)
            tipo = "INGRESO"
        else:
            continue

        saldo_token = f"{saldo:.2f}" if saldo is not None else f"row-{idx}"
        hash_seed = f"{account_rfc}|BBVA|{fecha_obj.strftime('%Y-%m-%d')}|{concepto.upper()}|{monto:.2f}|{tipo}|{saldo_token}"
        id_transaccion = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()

        periodo_mes = fecha_obj.strftime("%Y-%m")

        transacciones.append({
            "account_rfc": account_rfc,
            "id_transaccion": id_transaccion,
            "banco": "BBVA",
            "fecha": fecha_obj,
            "concepto": concepto,
            "monto": monto,
            "tipo": tipo,
            "saldo": saldo,
            "periodo_mes": periodo_mes,
        })

    return transacciones
