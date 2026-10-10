import io
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd


def parse_bbva_statement(file_content: bytes, filename: str, account_rfc: str = "DEGF851127TK1") -> List[Dict[str, Any]]:
    """
    Lee y normaliza un archivo de estado de cuenta o movimientos descargado de BBVA México
    (formato .csv, .xlsx o .xls).
    
    Genera un hash determinista único (SHA-256) por cada transacción para prevenir duplicados.
    """
    if not file_content:
        raise ValueError("El archivo de estado de cuenta está vacío.")

    filename_lower = filename.lower()
    df = None

    if filename_lower.endswith(".csv"):
        # Manejo de codificaciones comunes en exportaciones bancarias mexicanas
        for encoding in ["utf-8-sig", "utf-8", "latin-1", "cp1252"]:
            try:
                df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
                if not df.empty:
                    break
            except Exception:
                continue

        if df is None or df.empty:
            raise ValueError("No se pudo leer el archivo CSV de BBVA con ninguna codificación estándar.")
    elif filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls"):
        try:
            df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"Error leyendo archivo Excel de BBVA: {e}")
    else:
        raise ValueError("Formato de archivo no soportado. Debe ser .csv, .xlsx o .xls.")

    # Normalizar encabezados (quitar espacios en blanco, minúsculas, tildes)
    def clean_header(h: str) -> str:
        s = str(h).strip().lower()
        s = s.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        return s

    df.columns = [clean_header(c) for c in df.columns]

    # Mapeo flexible de columnas comunes en exportaciones BBVA
    col_fecha = next((c for c in df.columns if any(k in c for k in ["fecha", "f. oper", "f. valor", "operacion"])), None)
    col_concepto = next((c for c in df.columns if any(k in c for k in ["concepto", "descripci", "detalle", "motivo", "movimiento"])), None)
    col_cargo = next((c for c in df.columns if any(k in c for k in ["cargo", "retiro", "debito"])), None)
    col_abono = next((c for c in df.columns if any(k in c for k in ["abono", "deposito", "credito"])), None)
    col_saldo = next((c for c in df.columns if any(k in c for k in ["saldo", "balance"])), None)

    # Si hay una sola columna 'importe' o 'monto' con signo positivo/negativo
    col_monto_unico = None
    if not col_cargo and not col_abono:
        col_monto_unico = next((c for c in df.columns if any(k in c for k in ["importe", "monto"])), None)

    if not col_fecha or not col_concepto or (not col_cargo and not col_abono and not col_monto_unico):
        raise ValueError(
            f"Estructura no reconocida de BBVA. Columnas detectadas: {list(df.columns)}. "
            "Se requiere al menos Fecha, Concepto y Cargo/Abono (o Importe)."
        )

    transacciones: List[Dict[str, Any]] = []

    for idx, row in df.iterrows():
        # Descartar filas vacías o de encabezados secundarios
        if pd.isna(row[col_fecha]) or pd.isna(row[col_concepto]):
            continue

        raw_fecha = str(row[col_fecha]).strip()
        fecha_obj: Optional[datetime] = None

        # Probar formatos comunes de fecha en BBVA
        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"]:
            try:
                fecha_obj = datetime.strptime(raw_fecha[:10], fmt)
                break
            except ValueError:
                continue

        if not fecha_obj:
            # Si no es fecha válida, suele ser una fila de subtotales o pie de página
            continue

        concepto = str(row[col_concepto]).strip()
        if not concepto or concepto.upper().startswith("TOTAL"):
            continue

        cargo = 0.0
        abono = 0.0

        if col_monto_unico:
            val_str = str(row[col_monto_unico]).replace(",", "").replace("$", "").strip()
            val_num = pd.to_numeric(val_str, errors="coerce")
            if pd.isna(val_num) or val_num == 0:
                continue
            if val_num < 0:
                cargo = abs(float(val_num))
            else:
                abono = float(val_num)
        else:
            if col_cargo and not pd.isna(row[col_cargo]):
                c_str = str(row[col_cargo]).replace(",", "").replace("$", "").strip()
                c_num = pd.to_numeric(c_str, errors="coerce")
                if not pd.isna(c_num):
                    cargo = float(c_num)

            if col_abono and not pd.isna(row[col_abono]):
                a_str = str(row[col_abono]).replace(",", "").replace("$", "").strip()
                a_num = pd.to_numeric(a_str, errors="coerce")
                if not pd.isna(a_num):
                    abono = float(a_num)

        saldo = None
        if col_saldo and not pd.isna(row[col_saldo]):
            s_str = str(row[col_saldo]).replace(",", "").replace("$", "").strip()
            s_num = pd.to_numeric(s_str, errors="coerce")
            if not pd.isna(s_num):
                saldo = round(float(s_num), 2)

        # Determinar si es Cargo (EGRESO) o Abono (INGRESO)
        if cargo > 0:
            monto = round(cargo, 2)
            tipo = "EGRESO"
        elif abono > 0:
            monto = round(abono, 2)
            tipo = "INGRESO"
        else:
            continue  # Movimiento con monto cero

        # Generar hash SHA-256 determinista
        # Usamos RFC de cuenta, fecha, concepto, monto, tipo y saldo (o el índice de fila si no hay saldo)
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
