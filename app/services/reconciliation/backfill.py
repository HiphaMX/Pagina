import io
import csv
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
import openpyxl
from sqlalchemy.orm import Session

from app.models.reconciliation import CFDIInvoice, BankTransaction


def _clean_header(h: Any) -> str:
    s = str(h or "").strip().upper()
    s = s.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
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
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y", "%d/%m/%y", "%d/%m/%Y %H:%M:%S"]:
        try:
            return datetime.strptime(s[:19] if " " in s else s[:10], fmt)
        except ValueError:
            continue
    return None


def import_historical_excel(
    file_content: bytes,
    filename: str,
    db: Session,
    mi_rfc: Optional[str] = None,
    account_rfc: str = "DEGF851127TK1"
) -> Dict[str, Any]:
    """
    Importa hojas de cálculo históricas (Excel o CSV) donde el usuario ya tiene transacciones
    y folios fiscales previamente capturados, soportando la sábana de 14 columnas:
    FECHA, ÁREA/PROYECTO, FOLIO FISCAL, CLIENTE/PROVEEDOR, CONCEPTO, MÉTODO DE PAGO,
    INGRESOS, EGRESOS, CFDI, TIPO, SUBTOTAL, IVA INGRESOS, RETENCIÓN ISR, IVA EGRESOS.
    Utiliza exclusivamente librerías estándar y openpyxl (cero dependencias de pandas).
    """
    effective_rfc = mi_rfc or account_rfc
    filename_lower = filename.lower()
    rows: List[List[Any]] = []

    if filename_lower.endswith(".csv"):
        decoded_text: Optional[str] = None
        for enc in ["utf-8-sig", "utf-8", "latin-1", "cp1252"]:
            try:
                decoded_text = file_content.decode(enc)
                break
            except Exception:
                continue

        if not decoded_text:
            raise ValueError("No se pudo leer el archivo CSV con ninguna codificación estándar.")

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
            raise ValueError("El archivo CSV está vacío.")
    elif filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls"):
        try:
            wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True)
            sheet = wb.active
            rows = [list(r) for r in sheet.iter_rows(values_only=True) if any(c is not None for c in r)]
        except Exception as e:
            raise ValueError(f"Error leyendo archivo Excel: {e}")
    else:
        raise ValueError("Formato de archivo no soportado. Debe ser .csv, .xlsx o .xls.")

    if not rows:
        raise ValueError("El archivo de histórico está vacío o no pudo ser interpretado.")

    # Buscar encabezado en los primeros 15 renglones
    header_row_idx = None
    headers: List[str] = []
    for idx, r in enumerate(rows[:15]):
        cleaned_r = [_clean_header(c) for c in r]
        if any(any(k in c for k in ["FECHA", "DATE"]) for c in cleaned_r):
            header_row_idx = idx
            headers = cleaned_r
            break

    if header_row_idx is None:
        header_row_idx = 0
        headers = [_clean_header(c) for c in rows[0]]

    def find_col(keywords: List[str]) -> Optional[int]:
        for i, h in enumerate(headers):
            if any(k in h for k in keywords):
                return i
        return None

    col_fecha = find_col(["FECHA", "DATE"])
    col_area = find_col(["AREA", "PROYECTO"])
    col_uuid = find_col(["FOLIO", "UUID", "FISCAL"])
    col_contraparte = find_col(["CLIENTE", "PROVEEDOR", "NOMBRE", "RAZON"])
    col_concepto = find_col(["CONCEPTO", "DESCRIP", "DETALLE"])
    col_metodo = find_col(["METODO", "FORMA"])
    col_ingreso = find_col(["INGRESOS", "INGRESO", "ABONO", "DEPOSITO"])
    col_egreso = find_col(["EGRESOS", "EGRESO", "CARGO", "GASTO", "RETIRO"])
    col_monto = find_col(["MONTO", "TOTAL", "IMPORTE"])
    col_tipo = next((i for i, h in enumerate(headers) if h in ["TIPO", "CATEGORIA", "TIPO DE GASTO"]), None)
    col_subtotal = next((i for i, h in enumerate(headers) if "SUBTOTAL" in h), None)
    col_iva_ing = next((i for i, h in enumerate(headers) if "IVA ING" in h or "IVA TRAS" in h), None)
    col_ret_isr = next((i for i, h in enumerate(headers) if any(k in h for k in ["RETENCION ISR", "RETENCION_ISR", "ISR"])), None)
    col_iva_egr = next((i for i, h in enumerate(headers) if "IVA EGR" in h or "IVA ACRED" in h), None)
    col_iva = next((i for i, h in enumerate(headers) if "IVA" in h and i not in [col_iva_ing, col_iva_egr]), None)
    col_rfc = next((i for i, h in enumerate(headers) if "RFC" in h), None)

    if col_fecha is None:
        raise ValueError(f"No se encontró la columna de FECHA en el archivo histórico. Columnas: {headers}")

    tx_count = 0
    cfdi_count = 0
    errors: List[str] = []

    for idx, row in enumerate(rows[header_row_idx + 1:], start=header_row_idx + 1):
        try:
            if col_fecha >= len(row):
                continue

            raw_fecha_val = row[col_fecha]
            fecha_obj = _parse_date(raw_fecha_val)
            if not fecha_obj:
                continue

            concepto = str(row[col_concepto] or "").strip() if (col_concepto is not None and col_concepto < len(row)) else f"Movimiento {idx}"

            # Extraer montos
            monto = 0.0
            tipo = "EGRESO"

            val_ingreso = _parse_num(row[col_ingreso]) if (col_ingreso is not None and col_ingreso < len(row)) else 0.0
            val_egreso = _parse_num(row[col_egreso]) if (col_egreso is not None and col_egreso < len(row)) else 0.0

            val_ingreso = 0.0 if val_ingreso is None else float(val_ingreso)
            val_egreso = 0.0 if val_egreso is None else float(val_egreso)

            if val_ingreso > 0:
                monto = round(val_ingreso, 2)
                tipo = "INGRESO"
            elif val_egreso > 0:
                monto = round(val_egreso, 2)
                tipo = "EGRESO"
            elif col_monto is not None and col_monto < len(row):
                val_m = _parse_num(row[col_monto])
                if val_m and val_m != 0:
                    monto = round(abs(val_m), 2)
                    tipo = "INGRESO" if val_m > 0 else "EGRESO"

            if monto <= 0:
                continue

            # Evaluar UUID
            uuid = None
            if col_uuid is not None and col_uuid < len(row):
                uuid_candidate = str(row[col_uuid] or "").strip().upper()
                if len(uuid_candidate) >= 30 and "PENDIENTE" not in uuid_candidate and uuid_candidate not in ["NAN", "NONE", "NULL", "-"]:
                    uuid = uuid_candidate

            # Extraer datos de contraparte, área, método, tipo e impuestos
            contraparte = str(row[col_contraparte] or "").strip() if (col_contraparte is not None and col_contraparte < len(row)) else ""
            rfc_val = str(row[col_rfc] or "").strip().upper() if (col_rfc is not None and col_rfc < len(row)) else ""
            area_val = str(row[col_area] or "").strip() if (col_area is not None and col_area < len(row) and row[col_area]) else None
            metodo_val = str(row[col_metodo] or "PUE").strip().upper() if (col_metodo is not None and col_metodo < len(row) and row[col_metodo]) else "PUE"
            tipo_cat_val = str(row[col_tipo] or "").strip() if (col_tipo is not None and col_tipo < len(row) and row[col_tipo]) else ("INGRESO" if tipo == "INGRESO" else "GASTO")

            subtotal_num = _parse_num(row[col_subtotal]) if (col_subtotal is not None and col_subtotal < len(row)) else None
            subtotal_val = monto if subtotal_num is None else float(subtotal_num)

            # IVA e ISR
            iva_val = 0.0
            if col_iva_ing is not None and tipo == "INGRESO" and col_iva_ing < len(row):
                i_num = _parse_num(row[col_iva_ing])
                iva_val = 0.0 if i_num is None else float(i_num)
            elif col_iva_egr is not None and tipo == "EGRESO" and col_iva_egr < len(row):
                i_num = _parse_num(row[col_iva_egr])
                iva_val = 0.0 if i_num is None else float(i_num)
            elif col_iva is not None and col_iva < len(row):
                i_num = _parse_num(row[col_iva])
                iva_val = 0.0 if i_num is None else float(i_num)

            ret_isr_val = 0.0
            if col_ret_isr is not None and col_ret_isr < len(row):
                r_num = _parse_num(row[col_ret_isr])
                ret_isr_val = 0.0 if r_num is None else float(r_num)

            # 1. Registrar CFDI si tenía UUID
            if uuid:
                existing_cfdi = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid).first()
                if not existing_cfdi:
                    new_cfdi = CFDIInvoice(
                        uuid=uuid,
                        account_rfc=effective_rfc,
                        area_proyecto=area_val,
                        tipo=tipo,
                        rfc_emisor=effective_rfc if tipo == "INGRESO" else (rfc_val or "PROV_HISTORICO"),
                        nombre_emisor="HiphaMX" if tipo == "INGRESO" else (contraparte or "Proveedor"),
                        rfc_receptor=(rfc_val or "CLIENTE_HISTORICO") if tipo == "INGRESO" else effective_rfc,
                        nombre_receptor=contraparte if tipo == "INGRESO" else "HiphaMX",
                        fecha_emision=fecha_obj,
                        subtotal=round(subtotal_val, 2),
                        iva_trasladado=round(iva_val, 2),
                        retencion_isr=round(ret_isr_val, 2),
                        retencion_iva=0.0,
                        retenciones=round(ret_isr_val, 2),
                        total=round(monto, 2),
                        metodo_pago=metodo_val[:10] if metodo_val else "PUE",
                        forma_pago="03",
                        conceptos_resumen=concepto[:250],
                        conciliado=True,
                        fuente="HISTORICO"
                    )
                    db.add(new_cfdi)
                    cfdi_count += 1
                else:
                    existing_cfdi.conciliado = True

            # 2. Registrar Transacción Bancaria de forma determinista y sin duplicados
            area_str = (area_val or '').strip().upper()
            hash_seed = f"{effective_rfc}|HIST|{fecha_obj.strftime('%Y-%m-%d')}|{concepto.upper()}|{monto:.2f}|{tipo}|{area_str}"
            id_transaccion = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()

            # Evitar duplicados: verificar por id_transaccion O por datos de negocio
            existing_tx = db.query(BankTransaction).filter(
                BankTransaction.account_rfc == effective_rfc,
                (
                    (BankTransaction.id_transaccion == id_transaccion) |
                    (
                        (BankTransaction.fecha == fecha_obj) &
                        (BankTransaction.monto == monto) &
                        (BankTransaction.tipo == tipo) &
                        (BankTransaction.concepto == concepto)
                    )
                )
            ).first()

            if not existing_tx:
                new_tx = BankTransaction(
                    account_rfc=effective_rfc,
                    area_proyecto=area_val,
                    tipo_categoria=tipo_cat_val,
                    id_transaccion=id_transaccion,
                    banco="BBVA",
                    fecha=fecha_obj,
                    concepto=concepto,
                    monto=monto,
                    tipo=tipo,
                    uuid_cfdi=uuid,
                    status_conciliacion="CONCILIADO" if uuid else "SIN_CFDI",
                    confianza_score=1.0 if uuid else 0.0,
                    nota_revision="Migrado desde sábana histórica." if uuid else "Histórico sin folio fiscal.",
                    periodo_mes=fecha_obj.strftime("%Y-%m")
                )
                db.add(new_tx)
                tx_count += 1
            else:
                if uuid and not existing_tx.uuid_cfdi:
                    existing_tx.uuid_cfdi = uuid
                    existing_tx.status_conciliacion = "CONCILIADO"
                    existing_tx.confianza_score = 1.0
                    existing_tx.nota_revision = "Conciliado con folio fiscal histórico."
                if area_val and not existing_tx.area_proyecto:
                    existing_tx.area_proyecto = area_val

        except Exception as e_row:
            errors.append(f"Fila {idx}: {str(e_row)}")

    db.commit()

    return {
        "success": True,
        "imported_transactions": tx_count,
        "imported_invoices": cfdi_count,
        "errors": errors[:10]
    }
