import io
import csv
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import openpyxl


def _clean_header(h: Any) -> str:
    s = str(h or "").strip().lower()
    s = s.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    return s


def _parse_num(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).replace(",", "").replace("$", "").replace(" ", "").strip()
    if not s or s.upper() in ["NAN", "NONE", "NULL", "-", "--"]:
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _parse_date(val: Any) -> Optional[datetime]:
    if isinstance(val, datetime):
        return val
    if hasattr(val, "date") and callable(getattr(val, "date")):
        d = val.date()
        return datetime(d.year, d.month, d.day)
    s = str(val or "").strip()
    if not s:
        return None
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"]:
        try:
            return datetime.strptime(s[:19] if " " in s else s[:10], fmt)
        except ValueError:
            continue
    return None


def parse_bbva_statement(file_content: bytes, filename: str, account_rfc: str = "DEGF851127TK1") -> List[Dict[str, Any]]:
    """
    Lee y normaliza un archivo de estado de cuenta o movimientos descargado de BBVA México
    (formato .csv, .xlsx o .xls).
    
    Genera un hash determinista único (SHA-256) por cada transacción para prevenir duplicados.
    Utiliza exclusivamente librerías estándar y openpyxl (cero dependencias de pandas).
    """
    if not file_content:
        raise ValueError("El archivo de estado de cuenta está vacío.")

    filename_lower = filename.lower()
    rows: List[List[Any]] = []

    if filename_lower.endswith(".csv"):
        decoded_text: Optional[str] = None
        for encoding in ["utf-8-sig", "utf-8", "latin-1", "cp1252"]:
            try:
                decoded_text = file_content.decode(encoding)
                break
            except Exception:
                continue

        if not decoded_text:
            raise ValueError("No se pudo leer el archivo CSV de BBVA con ninguna codificación estándar.")

        sample = decoded_text[:2048]
        delim = ','
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            delim = dialect.delimiter
        except Exception:
            delim = ','

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

    # Buscar el renglón de encabezados dentro de los primeros 15 renglones
    header_row_idx = None
    headers: List[str] = []
    for idx, r in enumerate(rows[:15]):
        cleaned_r = [_clean_header(c) for c in r]
        if any(any(k in c for k in ["fecha", "f. oper", "f. valor", "operacion"]) for c in cleaned_r):
            header_row_idx = idx
            headers = cleaned_r
            break

    if header_row_idx is None:
        header_row_idx = 0
        headers = [_clean_header(c) for c in rows[0]]

    # Mapeo flexible de columnas comunes en exportaciones BBVA
    col_fecha_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["fecha", "f. oper", "f. valor", "operacion"])), None)
    col_concepto_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["concepto", "descripci", "detalle", "motivo", "movimiento"])), None)
    col_cargo_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["cargo", "retiro", "debito"])), None)
    col_abono_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["abono", "deposito", "credito"])), None)
    col_saldo_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["saldo", "balance"])), None)

    col_monto_unico_idx = None
    if col_cargo_idx is None and col_abono_idx is None:
        col_monto_unico_idx = next((i for i, h in enumerate(headers) if any(k in h for k in ["importe", "monto"])), None)

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
        fecha_obj = _parse_date(raw_fecha_val)
        if not fecha_obj:
            continue

        concepto = str(row[col_concepto_idx] or "").strip()
        if not concepto or concepto.upper().startswith("TOTAL"):
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
                    cargo = float(c_num)

            if col_abono_idx is not None and col_abono_idx < len(row):
                a_num = _parse_num(row[col_abono_idx])
                if a_num is not None:
                    abono = float(a_num)

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
