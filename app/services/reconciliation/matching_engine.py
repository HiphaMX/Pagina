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
        # Extraer fecha bancaria
        tx_fecha = tx["fecha"]
        if isinstance(tx_fecha, str):
            tx_fecha = datetime.strptime(tx_fecha[:10], "%Y-%m-%d")
        elif isinstance(tx_fecha, datetime):
            tx_fecha = tx_fecha

        tx_monto = round(float(tx["monto"]), 2)
        tx_tipo = tx["tipo"]  # INGRESO o EGRESO
        concepto_upper = str(tx.get("concepto", "")).upper()

        match_seleccionado: Any = None
        match_tier: int = 3
        nota_revision: str = ""
        confianza_score: float = 0.0

        # Lista de candidatos que coinciden en tipo y monto
        candidatos: List[Tuple[Dict[str, Any], int, str, float]] = []

        for f in facturas_pool:
            f_tipo = f["tipo"]
            f_total = round(float(f["total"]), 2)

            # 1. Filtro estricto: Mismo tipo de flujo (egreso-cargo o ingreso-abono) y monto exacto
            if f_tipo == tx_tipo and abs(f_total - tx_monto) <= 0.05:
                f_fecha = f["fecha_emision"]
                if isinstance(f_fecha, str):
                    f_fecha = datetime.strptime(f_fecha[:10], "%Y-%m-%d")

                # 2. Ventana temporal: el movimiento en banco ocurre entre -2 y +7 días de la emisión
                delta_dias = (tx_fecha - f_fecha).days
                if -2 <= delta_dias <= 7:
                    # Evaluar coincidencia de texto (RFC o Razón Social)
                    rfc_contraparte = (f.get("rfc_emisor") if f_tipo == "EGRESO" else f.get("rfc_receptor") or "").upper().strip()
                    nombre_contraparte = (f.get("nombre_emisor") if f_tipo == "EGRESO" else f.get("nombre_receptor") or "").upper().strip()

                    tokens_nombre = _clean_text_tokens(nombre_contraparte)

                    tiene_coincidencia_texto = False
                    if rfc_contraparte and len(rfc_contraparte) >= 4 and rfc_contraparte in concepto_upper:
                        tiene_coincidencia_texto = True
                    else:
                        for token in tokens_nombre:
                            if token in concepto_upper:
                                tiene_coincidencia_texto = True
                                break

                    if tiene_coincidencia_texto:
                        # Nivel 1: Match 100%
                        candidatos.append((f, 1, f"Match exacto por importe (${tx_monto:,.2f}), fecha ({delta_dias}d) y coincidencia con {nombre_contraparte[:30]}.", 1.0))
                    else:
                        # Nivel 2: Match 70% (Monto y fecha coinciden, concepto genérico o ambiguo)
                        candidatos.append((f, 2, f"Monto (${tx_monto:,.2f}) y fecha coinciden con CFDI de {nombre_contraparte[:30]}, pero el concepto bancario no contiene el RFC/Nombre visible.", 0.7))

        if candidatos:
            # Priorizar candidatos Nivel 1 sobre Nivel 2
            candidatos.sort(key=lambda x: (x[1], abs((tx_fecha - (datetime.strptime(x[0]["fecha_emision"][:10], "%Y-%m-%d") if isinstance(x[0]["fecha_emision"], str) else x[0]["fecha_emision"])).days)))
            ganador, match_tier, nota_revision, confianza_score = candidatos[0]

            uuid_asignado = ganador["uuid"]
            status_asignado = "CONCILIADO" if match_tier == 1 else "POR_REVISAR"

            # Remover la factura ganadora del pool para evitar emparejamientos dobles
            facturas_pool.remove(ganador)
        else:
            # Nivel 3: Sin CFDI (0%)
            uuid_asignado = None
            status_asignado = "SIN_CFDI"
            confianza_score = 0.0

            # Identificar si es comisión bancaria o movimiento no deducible recurrente
            if any(term in concepto_upper for term in ["COMISION", "IVA COMISION", "MEMBRESIA", "MANEJO DE CUENTA", "CHEQUE"]):
                nota_revision = "Cargo bancario / comisión BBVA. Generalmente amparado en el estado de cuenta fiscal mensual del banco."
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

        resultados.append(resultado_tx)

    return resultados
