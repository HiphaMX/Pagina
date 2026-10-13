from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import re

def _clean_text_tokens(text: str) -> List[str]:
    """Extrae palabras clave significativas de más de 3 letras ignorando stopwords comunes."""
    if not text:
        return []
    stopwords = {"DE", "DEL", "LA", "EL", "LOS", "LAS", "SA", "CV", "SAPI", "SCL", "SRL", "SC", "RFC", "SPEI", "BCO", "BANCO", "PAGO", "TRANSFERENCIA", "TRASPASO"}
    cleaned = re.sub(r'[^A-Z0-9\s]', ' ', text.upper())
    tokens = [t for t in cleaned.split() if len(t) >= 4 and t not in stopwords]
    return tokens

def conciliar_movimientos(transacciones_banco: List[Dict[str, Any]], facturas_disponibles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ejecuta el motor de conciliación determinista de 3 niveles entre movimientos bancarios y CFDIs disponibles.
    
    Tolerancia: ±$0.05 MXN por redondeo bancario.
    Ventana temporal: Entre -2 días y +7 días naturales respecto a la fecha del CFDI.
    
    Retorna la lista de transacciones con sus campos de conciliación asignados.
    """
    # Copia de trabajo de facturas para descartar en memoria las ya emparejadas
    facturas_pool = list(facturas_disponibles)
    resultados = []

    for tx in transacciones_banco:
        # Si la transacción ya está excluida/justificada (NO_APLICA, EXENTO) o es un traspaso entre cuentas propias
        from app.services.reconciliation.pdf_parser import is_own_account_transfer

        if tx.get("status_conciliacion") in ("NO_APLICA", "EXENTO") or is_own_account_transfer(tx.get("concepto", ""), account_rfc=tx.get("account_rfc", "")) or (tx.get("nota_revision") and "Traspaso entre Cuentas Propias" in tx.get("nota_revision", "")):
            resultado_tx = dict(tx)
            resultado_tx["uuid_cfdi"] = None
            resultado_tx["status_conciliacion"] = "NO_APLICA"
            resultado_tx["confianza_score"] = 1.0
            resultado_tx["nota_revision"] = tx.get("nota_revision") or "Traspaso entre Cuentas Propias"
            resultado_tx["area_proyecto"] = tx.get("area_proyecto") or "DELGADILLO MEDINA"
            resultados.append(resultado_tx)
            continue

        # Extraer fecha bancaria
        tx_fecha = tx["fecha"]
        if isinstance(tx_fecha, str):
            tx_fecha = datetime.strptime(tx_fecha[:10], "%Y-%m-%d")
        elif isinstance(tx_fecha, datetime):
            tx_fecha = tx_fecha

        tx_monto = round(float(tx["monto"]), 2)
        tx_tipo = tx["tipo"]  # INGRESO o EGRESO
        concepto_upper = str(tx.get("concepto", "")).upper()

        uuid_asignado = None
        status_asignado = "SIN_CFDI"
        confianza_score = 0.0
        nota_revision = ""
        related_cfdi_uuids = []
        delgadillo_area = None

        # -------------------------------------------------------------
        # FASE 1: Búsqueda 1:1 (Exacta o con Complemento de Pago)
        # -------------------------------------------------------------
        candidatos: List[Tuple[Dict[str, Any], int, str, float, List[str]]] = []

        for f in facturas_pool:
            f_tipo = f["tipo"]
            f_total = round(float(f["total"]), 2)

            if f_tipo == tx_tipo and abs(f_total - tx_monto) <= 0.05:
                f_fecha = f.get("fecha_pago") or f["fecha_emision"]
                if isinstance(f_fecha, str):
                    f_fecha = datetime.strptime(f_fecha[:10], "%Y-%m-%d")

                tx_d = tx_fecha.date() if hasattr(tx_fecha, "date") else tx_fecha
                f_d = f_fecha.date() if hasattr(f_fecha, "date") else f_fecha
                delta_dias = (tx_d - f_d).days

                rfc_contraparte = str((f.get("rfc_emisor") if f_tipo == "EGRESO" else f.get("rfc_receptor")) or "").upper().strip()
                nombre_contraparte = str((f.get("nombre_emisor") if f_tipo == "EGRESO" else f.get("nombre_receptor")) or "").upper().strip()
                tokens_nombre = _clean_text_tokens(nombre_contraparte)

                tiene_coincidencia_texto = False
                if rfc_contraparte and len(rfc_contraparte) >= 4 and rfc_contraparte in concepto_upper:
                    tiene_coincidencia_texto = True
                else:
                    for token in tokens_nombre:
                        if token in concepto_upper:
                            tiene_coincidencia_texto = True
                            break

                # Relacionados si es Complemento de Pago
                f_related = [d["uuid"] for d in f.get("doctos_relacionados", []) if d.get("uuid")]

                # Ventana comercial flexible:
                # - Con coincidencia de nombre/RFC: de -60 días (anticipos de clientes) a +90 días (crédito comercial y PPD)
                # - Sin coincidencia visible en concepto: ventana estricta de -3 a +7 días
                if tiene_coincidencia_texto:
                    if -60 <= delta_dias <= 90:
                        rep_tag = " [Complemento de Pago]" if f.get("metodo_pago") == "PAGO" else ""
                        ant_tag = " [Anticipo]" if delta_dias < 0 else ""
                        candidatos.append((f, 1, f"Match exacto{rep_tag}{ant_tag} por importe (${tx_monto:,.2f}), fecha ({delta_dias}d) y coincidencia con {nombre_contraparte[:30]}.", 1.0, f_related))
                    elif 91 <= delta_dias <= 150 or -90 <= delta_dias < -60:
                        candidatos.append((f, 2, f"Monto (${tx_monto:,.2f}) y contraparte ({nombre_contraparte[:30]}) coinciden, pero con desfase de {delta_dias} días.", 0.8, f_related))
                else:
                    if -3 <= delta_dias <= 7:
                        candidatos.append((f, 2, f"Monto (${tx_monto:,.2f}) y fecha coinciden con CFDI de {nombre_contraparte[:30]}, pero el concepto bancario no contiene el RFC/Nombre visible.", 0.7, f_related))

        if candidatos:
            candidatos.sort(key=lambda x: (x[1], abs((tx_fecha - (datetime.strptime(x[0]["fecha_emision"][:10], "%Y-%m-%d") if isinstance(x[0]["fecha_emision"], str) else x[0]["fecha_emision"])).days)))
            ganador, match_tier, nota_revision, confianza_score, related_cfdi_uuids = candidatos[0]

            uuid_asignado = ganador["uuid"]
            status_asignado = "CONCILIADO" if match_tier == 1 else "POR_REVISAR"
            facturas_pool.remove(ganador)

            # Si el ganador ampara facturas hijas (REP), remover también las facturas hijas del pool
            if related_cfdi_uuids:
                facturas_pool = [inv for inv in facturas_pool if inv["uuid"] not in related_cfdi_uuids]

        # -------------------------------------------------------------
        # FASE 2: Pagos Consolidados (Múltiples Facturas en 1 Solo Pago)
        # -------------------------------------------------------------
        elif tx_tipo == "INGRESO":
            candidatos_combo = [
                inv for inv in facturas_pool
                if inv["tipo"] == "INGRESO" and 0 < round(float(inv["total"]), 2) < tx_monto
            ]

            # Priorizar facturas cuya contraparte coincida con el concepto bancario
            def _has_text_match(inv_cand):
                nom = (inv_cand.get("nombre_receptor") or "").upper().strip()
                rfc_c = (inv_cand.get("rfc_receptor") or "").upper().strip()
                if rfc_c and len(rfc_c) >= 4 and rfc_c in concepto_upper:
                    return True
                for tok in _clean_text_tokens(nom):
                    if tok in concepto_upper:
                        return True
                return False

            matched_combo: List[Dict[str, Any]] = []

            # Filtrar por ventana temporal razonable (-15d a +90d respecto a la fecha del pago)
            valid_cands = []
            for c in candidatos_combo:
                c_fec = c["fecha_emision"]
                if isinstance(c_fec, str):
                    c_fec = datetime.strptime(c_fec[:10], "%Y-%m-%d")
                tx_d = tx_fecha.date() if hasattr(tx_fecha, "date") else tx_fecha
                c_d = c_fec.date() if hasattr(c_fec, "date") else c_fec
                d_days = (tx_d - c_d).days
                if -60 <= d_days <= 90:
                    valid_cands.append(c)

            # Ordenar primero los que coinciden en nombre/RFC
            valid_cands.sort(key=lambda x: (0 if _has_text_match(x) else 1))

            # 1. Probar combinaciones de 2 facturas
            for i in range(len(valid_cands)):
                for j in range(i + 1, len(valid_cands)):
                    s2 = round(float(valid_cands[i]["total"]) + float(valid_cands[j]["total"]), 2)
                    if abs(s2 - tx_monto) <= 0.05:
                        matched_combo = [valid_cands[i], valid_cands[j]]
                        break
                if matched_combo:
                    break

            # 2. Probar combinaciones de 3 facturas si no hubo par
            if not matched_combo:
                for i in range(len(valid_cands)):
                    for j in range(i + 1, len(valid_cands)):
                        for k in range(j + 1, len(valid_cands)):
                            s3 = round(float(valid_cands[i]["total"]) + float(valid_cands[j]["total"]) + float(valid_cands[k]["total"]), 2)
                            if abs(s3 - tx_monto) <= 0.05:
                                matched_combo = [valid_cands[i], valid_cands[j], valid_cands[k]]
                                break
                        if matched_combo:
                            break
                    if matched_combo:
                        break

            if matched_combo:
                uuid_asignado = matched_combo[0]["uuid"]
                status_asignado = "CONCILIADO"
                confianza_score = 1.0
                related_cfdi_uuids = [inv["uuid"] for inv in matched_combo]
                desc_combo = " + ".join([f"{inv['uuid'][:8]} (${float(inv['total']):,.2f})" for inv in matched_combo])
                receptor_name = matched_combo[0].get("nombre_receptor", "")
                nota_revision = f"Pago consolidado de {len(matched_combo)} facturas ({receptor_name[:25]}): {desc_combo}"

                # Remover todas las facturas consolidadas del pool
                for inv_rem in matched_combo:
                    if inv_rem in facturas_pool:
                        facturas_pool.remove(inv_rem)

        # -------------------------------------------------------------
        # FASE 3: Clasificación Inteligente de Egresos sin CFDI
        # -------------------------------------------------------------
        if status_asignado == "SIN_CFDI":
            banco_val = tx.get("banco", "")
            from app.services.reconciliation.pdf_parser import is_delgadillo_medina_tc_expense

            if any(term in concepto_upper for term in ["SAT ", "PAGO SIPARE", "IMSS/INF/AFORE", "IMPUESTOS", "TESORERIA"]):
                status_asignado = "NO_APLICA"
                confianza_score = 1.0
                nota_revision = "Pago fiscal / Seguridad Social (SAT / IMSS / SIPARE). Exento de comprobante CFDI comercial."
            elif any(term in concepto_upper for term in ["COMISION", "IVA COMISION", "SERV BANCA INTERNET", "IVA COM SERV", "MEMBRESIA", "MANEJO DE CUENTA", "CHEQUE"]):
                status_asignado = "SIN_CFDI"
                nota_revision = "Cargo bancario / comisión BBVA. Generalmente amparado en el estado de cuenta fiscal mensual del banco."
            elif any(term in concepto_upper for term in ["TC PROY", "PAGO TARJETA", "PAGO DE TARJETA", "PAGO TC"]):
                status_asignado = "NO_APLICA"
                confianza_score = 1.0
                nota_revision = "Pago a Tarjeta de Crédito / Cuenta Secundaria."
            elif any(term in concepto_upper for term in ["DEVOLUCION", "DEVOLUCIÓN", "SPEI DEVUELTO"]):
                status_asignado = "NO_APLICA"
                confianza_score = 1.0
                nota_revision = "Movimiento devuelto / cancelación bancaria."
            elif tx_tipo == "EGRESO" and is_delgadillo_medina_tc_expense(tx.get("concepto", ""), banco=banco_val):
                nota_revision = "Gasto con TC sin proveedor corporativo reconocido o terminal MP (DELGADILLO MEDINA - Pendiente de revisión)"
                delgadillo_area = "DELGADILLO MEDINA"
            elif any(term in concepto_upper for term in ["RETIRO", "DISPOSICION", "CAJERO"]):
                nota_revision = "Retiro en efectivo / ventanilla. Sin comprobante digital emitido."
            elif any(term in concepto_upper for term in ["PAGO DE INTERESES", "RENDIMIENTO"]):
                nota_revision = "Abono por intereses ganados de BBVA."
            else:
                nota_revision = "Transacción bancaria sin CFDI registrado en el período."

        # Construir registro resultado
        resultado_tx = dict(tx)
        resultado_tx["uuid_cfdi"] = uuid_asignado
        resultado_tx["status_conciliacion"] = status_asignado
        resultado_tx["confianza_score"] = confianza_score
        resultado_tx["nota_revision"] = nota_revision
        resultado_tx["related_cfdi_uuids"] = related_cfdi_uuids
        if uuid_asignado is None and delgadillo_area:
            resultado_tx["area_proyecto"] = delgadillo_area

        resultados.append(resultado_tx)

    return resultados
