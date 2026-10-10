import io
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
from sqlalchemy.orm import Session

from app.models.reconciliation import CFDIInvoice, BankTransaction


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
    """
    effective_rfc = mi_rfc or account_rfc
    filename_lower = filename.lower()
    df = None

    if filename_lower.endswith(".csv"):
        for enc in ["utf-8-sig", "utf-8", "latin-1"]:
            try:
                df = pd.read_csv(io.BytesIO(file_content), encoding=enc)
                if not df.empty:
                    break
            except Exception:
                continue
    else:
        df = pd.read_excel(io.BytesIO(file_content))

    if df is None or df.empty:
        raise ValueError("El archivo de histórico está vacío o no pudo ser interpretado.")

    # Normalizar columnas a mayúsculas sin espacios
    df.columns = [str(c).strip().upper() for c in df.columns]

    col_fecha = next((c for c in df.columns if any(k in c for k in ["FECHA", "DATE"])), None)
    col_area = next((c for c in df.columns if any(k in c for k in ["ÁREA", "AREA", "PROYECTO"])), None)
    col_uuid = next((c for c in df.columns if any(k in c for k in ["FOLIO", "UUID", "FISCAL"])), None)
    col_contraparte = next((c for c in df.columns if any(k in c for k in ["CLIENTE", "PROVEEDOR", "NOMBRE", "RAZON"])), None)
    col_concepto = next((c for c in df.columns if any(k in c for k in ["CONCEPTO", "DESCRIP", "DETALLE"])), None)
    col_metodo = next((c for c in df.columns if any(k in c for k in ["MÉTODO", "METODO", "FORMA"])), None)
    col_ingreso = next((c for c in df.columns if any(k in c for k in ["INGRESOS", "INGRESO", "ABONO", "DEPOSITO"])), None)
    col_egreso = next((c for c in df.columns if any(k in c for k in ["EGRESOS", "EGRESO", "CARGO", "GASTO", "RETIRO"])), None)
    col_monto = next((c for c in df.columns if any(k in c for k in ["MONTO", "TOTAL", "IMPORTE"])), None)
    col_tipo = next((c for c in df.columns if c in ["TIPO", "CATEGORIA", "TIPO DE GASTO"]), None)
    col_subtotal = next((c for c in df.columns if "SUBTOTAL" in c), None)
    col_iva_ing = next((c for c in df.columns if "IVA ING" in c), None)
    col_ret_isr = next((c for c in df.columns if any(k in c for k in ["RETENCIÓN ISR", "RETENCION ISR", "ISR"])), None)
    col_iva_egr = next((c for c in df.columns if "IVA EGR" in c), None)
    col_iva = next((c for c in df.columns if "IVA" in c and c not in [col_iva_ing, col_iva_egr]), None)
    col_rfc = next((c for c in df.columns if "RFC" in c), None)

    if not col_fecha:
        raise ValueError("No se encontró la columna de FECHA en el archivo histórico.")

    tx_count = 0
    cfdi_count = 0
    errors: List[str] = []

    for idx, row in df.iterrows():
        try:
            if pd.isna(row[col_fecha]):
                continue

            raw_fecha = str(row[col_fecha]).strip()
            fecha_obj: Optional[datetime] = None
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y"]:
                try:
                    fecha_obj = datetime.strptime(raw_fecha[:10], fmt)
                    break
                except ValueError:
                    continue

            if not fecha_obj:
                continue

            concepto = str(row.get(col_concepto, "")).strip() if col_concepto else f"Movimiento {idx}"

            # Extraer montos
            monto = 0.0
            tipo = "EGRESO"

            val_ingreso = pd.to_numeric(str(row.get(col_ingreso, 0)).replace(",", "").replace("$", ""), errors="coerce") if col_ingreso else 0.0
            val_egreso = pd.to_numeric(str(row.get(col_egreso, 0)).replace(",", "").replace("$", ""), errors="coerce") if col_egreso else 0.0

            val_ingreso = 0.0 if pd.isna(val_ingreso) else float(val_ingreso)
            val_egreso = 0.0 if pd.isna(val_egreso) else float(val_egreso)

            if val_ingreso > 0:
                monto = round(val_ingreso, 2)
                tipo = "INGRESO"
            elif val_egreso > 0:
                monto = round(val_egreso, 2)
                tipo = "EGRESO"
            elif col_monto:
                val_m = pd.to_numeric(str(row.get(col_monto, 0)).replace(",", "").replace("$", ""), errors="coerce")
                val_m = 0.0 if pd.isna(val_m) else float(val_m)
                if val_m != 0:
                    monto = abs(val_m)
                    tipo = "INGRESO" if val_m > 0 else "EGRESO"

            if monto <= 0:
                continue

            # Evaluar UUID
            uuid = None
            if col_uuid and not pd.isna(row[col_uuid]):
                uuid_candidate = str(row[col_uuid]).strip().upper()
                # Un UUID estándar del SAT tiene 36 caracteres con guiones
                if len(uuid_candidate) >= 30 and "PENDIENTE" not in uuid_candidate and uuid_candidate != "NAN":
                    uuid = uuid_candidate

            # Extraer datos de contraparte, área, método, tipo e impuestos
            contraparte = str(row.get(col_contraparte, "")).strip() if col_contraparte and not pd.isna(row[col_contraparte]) else ""
            rfc_val = str(row.get(col_rfc, "")).strip().upper() if col_rfc and not pd.isna(row[col_rfc]) else ""
            area_val = str(row.get(col_area, "")).strip() if col_area and not pd.isna(row[col_area]) else None
            metodo_val = str(row.get(col_metodo, "PUE")).strip().upper() if col_metodo and not pd.isna(row[col_metodo]) else "PUE"
            tipo_cat_val = str(row.get(col_tipo, "")).strip() if col_tipo and not pd.isna(row[col_tipo]) else ("INGRESO" if tipo == "INGRESO" else "GASTO")
            
            subtotal_num = pd.to_numeric(str(row.get(col_subtotal, monto)).replace(",", "").replace("$", ""), errors="coerce") if col_subtotal else monto
            subtotal_val = monto if pd.isna(subtotal_num) else float(subtotal_num)

            # IVA e ISR
            iva_val = 0.0
            if col_iva_ing and tipo == "INGRESO" and not pd.isna(row[col_iva_ing]):
                i_num = pd.to_numeric(str(row[col_iva_ing]).replace(",", "").replace("$", ""), errors="coerce")
                iva_val = 0.0 if pd.isna(i_num) else float(i_num)
            elif col_iva_egr and tipo == "EGRESO" and not pd.isna(row[col_iva_egr]):
                i_num = pd.to_numeric(str(row[col_iva_egr]).replace(",", "").replace("$", ""), errors="coerce")
                iva_val = 0.0 if pd.isna(i_num) else float(i_num)
            elif col_iva and not pd.isna(row[col_iva]):
                i_num = pd.to_numeric(str(row[col_iva]).replace(",", "").replace("$", ""), errors="coerce")
                iva_val = 0.0 if pd.isna(i_num) else float(i_num)

            ret_isr_val = 0.0
            if col_ret_isr and not pd.isna(row[col_ret_isr]):
                r_num = pd.to_numeric(str(row[col_ret_isr]).replace(",", "").replace("$", ""), errors="coerce")
                ret_isr_val = 0.0 if pd.isna(r_num) else float(r_num)

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

            # 2. Registrar Transacción Bancaria
            hash_seed = f"{effective_rfc}|HIST|{fecha_obj.strftime('%Y-%m-%d')}|{concepto.upper()}|{monto:.2f}|{tipo}|{idx}"
            id_transaccion = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()

            existing_tx = db.query(BankTransaction).filter(BankTransaction.id_transaccion == id_transaccion).first()
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

        except Exception as e_row:
            errors.append(f"Fila {idx}: {str(e_row)}")

    db.commit()

    return {
        "success": True,
        "imported_transactions": tx_count,
        "imported_invoices": cfdi_count,
        "errors": errors[:10]
    }
