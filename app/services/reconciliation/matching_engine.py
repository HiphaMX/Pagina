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

# Mapeo de nombres comerciales y terminales TPV hacia razones sociales y RFCs de emisores CFDI
TRADE_NAME_ALIASES = {
    "FERREMATE": ["CASTELLANOS", "CACX880324IAA"],
    "IKEA": ["IKANO", "IRM170428Q82", "HER170522M19"],
    "HOME DEPOT": ["THE HOME DEPOT", "HDM001017AS1"],
    "PLURAL": ["PLURAL ARQUITECTURA", "PAR150311N33", "PAR050922GK3"],
    "ZARA": ["INDITEX", "ZARA MEXICO", "IMX0202206G1"],
    "H&M": ["HENNES", "MAURITZ", "HM"],
    "UBER": ["DANIEL ALFREDO CHAVEZ", "CHMD850428", "FACTURIFY", "FAC1710188Q2", "UBER"],
    "DLO*UBER": ["DANIEL ALFREDO CHAVEZ", "CHMD850428", "FACTURIFY", "FAC1710188Q2", "UBER"],
    "ULTRAKLIN": ["BIOZONE CHEMICAL", "BIOZONE"],
    "OFFICE Y SCHOOL": ["SILVA DE LA TORRE", "SITM7801129B4"],
    "TUKIPA": ["ABEL ALEJANDRO MEDINA", "MEHA870222DY4"],
}


def _extract_cfdi_identifiers(f: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrae serie, folio, uuid y combinaciones serie-folio de la factura o complemento de pago.
    """
    uuid_raw = str(f.get("uuid") or "").strip().upper()
    uuid_short = uuid_raw[:8] if len(uuid_raw) >= 8 else ""

    serie = str(f.get("serie") or "").strip().upper()
    folio = str(f.get("folio") or "").strip().upper()

    # Si no vienen explícitos, buscar en conceptos_resumen (ej. [F-176] o [176])
    conceptos = str(f.get("conceptos_resumen") or "")
    m_bracket = re.search(r'\[([A-Za-z0-9_-]+)\]', conceptos)
    if m_bracket:
        bracket_val = m_bracket.group(1).upper()
        if "-" in bracket_val:
            parts = bracket_val.split("-", 1)
            if not serie and parts[0]:
                serie = parts[0]
            if not folio and parts[1]:
                folio = parts[1]
        elif not folio:
            folio = bracket_val

    # Si aún no hay folio/serie, buscar en xml_raw si existe
    xml_raw = str(f.get("xml_raw") or "")
    if xml_raw:
        if not folio:
            m_fol = re.search(r'(?:Folio|folio)="([^"]+)"', xml_raw)
            if m_fol:
                folio = m_fol.group(1).strip().upper()
        if not serie:
            m_ser = re.search(r'(?:Serie|serie)="([^"]+)"', xml_raw)
            if m_ser:
                serie = m_ser.group(1).strip().upper()

    serie_folio_combos = []
    if serie and folio:
        serie_folio_combos.extend([
            f"{serie}-{folio}",
            f"{serie}{folio}",
            f"{serie} {folio}"
        ])
    elif folio:
        serie_folio_combos.append(folio)

    return {
        "uuid": uuid_raw,
        "uuid_short": uuid_short,
        "serie": serie,
        "folio": folio,
        "serie_folio_combos": serie_folio_combos
    }


def _matches_direct_reference(concepto_upper: str, cfdi_ids: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Nivel 1: Verifica si el concepto bancario contiene explícitamente:
    1. UUID completo o segmento UUID de 8 caracteres (uuid_short)
    2. Serie-folio completo (ej. 'F-176', 'F176', 'F 176')
    3. Folio numérico o alfanumérico coincidente con etiqueta bancaria (REF, FOLIO, FACTURA, BNET, RASTREO o entre corchetes)
    """
    uuid = cfdi_ids["uuid"]
    uuid_short = cfdi_ids["uuid_short"]
    folio = cfdi_ids["folio"]
    combos = cfdi_ids["serie_folio_combos"]

    # 1. Match por UUID completo
    if uuid and len(uuid) == 36 and uuid in concepto_upper:
        return True, f"UUID:{uuid[:8]}"

    # 2. Match por UUID corto (8 caracteres hexadecimales)
    if uuid_short and len(uuid_short) >= 8 and re.search(rf'\b{re.escape(uuid_short)}\b', concepto_upper):
        return True, f"UUID:{uuid_short}"

    # 3. Match por serie-folio compuesto (ej. 'F-176', 'F176')
    for combo in combos:
        if combo and len(combo) >= 3:
            if re.search(rf'(?:\b|[_\s/-]){re.escape(combo)}(?:\b|[_\s/-])', concepto_upper):
                return True, f"Folio:{combo}"

    # 4. Match por Folio individual (ej. 176 o 49201)
    if folio and len(folio) >= 2:
        folio_unpadded = folio.lstrip('0') or '0'
        explicit_patterns = [
            rf'(?:REF|REFERENCIA|FOLIO|FAC|FACTURA|DOCTO|DOC)[:\s#]+0*{re.escape(folio_unpadded)}\b',
            rf'\[0*{re.escape(folio_unpadded)}\]',
            rf'RASTREO[:\s]+[0-9A-Z]*{re.escape(folio_unpadded)}'
        ]
        for pat in explicit_patterns:
            if re.search(pat, concepto_upper):
                return True, f"Folio:{folio}"

        # Si el folio tiene 4 o más caracteres, admitir match como palabra completa
        if len(folio) >= 4 and re.search(rf'\b0*{re.escape(folio_unpadded)}\b', concepto_upper):
            return True, f"Folio:{folio}"

    return False, ""


def conciliar_movimientos(transacciones_banco: List[Dict[str, Any]], facturas_disponibles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Motor de Emparejamiento por Niveles (Cascada de Scoring):
    
    - Nivel 1: Match Exacto (Determinista)
      Mismo monto exacto (±$0.05) + clave de rastreo / referencia bancaria coincide con folio o UUID + fecha ventana (±3 días).
      Auto-conciliar sin intervención. Estatus: CONCILIADO_DIRECTO (confianza 1.0).
      
    - Nivel 2: Match Fuzzy (1 a 1)
      Mismo monto exacto (±$0.05) + razón social / alias comercial coincide con concepto bancario validado contra RFC conocido, sin referencia explícita.
      Estatus: CONCILIADO_POR_REGLA (confianza 0.95).
      
    - Nivel 3: Match Complejo (N a 1 o 1 a N)
      - N a 1: Un depósito/pago cubre múltiples facturas PPD/PUE. Si la combinación es unívoca -> CONCILIADO; si hay ambigüedad -> POR_REVISAR.
      - 1 a N: Factura pagada en 2 exhibiciones bancarias (split payments) -> Ambas transacciones CONCILIADO (confianza 1.0).
      
    - Nivel 4: Discrepancias y Huérfanos
      Movimientos bancarios sin factura: auto-clasificación de fiscales/traspasos (NO_APLICA) y comisiones/gastos pendientes (SIN_CFDI).
    """
    facturas_pool = list(facturas_disponibles)
    resultados = []

    for tx in transacciones_banco:
        # Pre-descarte: Traspasos propios o justificados
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

        # Fechas y montos
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
        # FASE 1: Búsqueda 1:1 (Nivel 1 Determinista & Nivel 2 Fuzzy)
        # -------------------------------------------------------------
        candidatos: List[Tuple[Dict[str, Any], int, str, float, str, List[str]]] = []

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

                # Coincidencia de texto (Razón social, RFC o Alias comercial)
                tiene_coincidencia_texto = False
                if rfc_contraparte and len(rfc_contraparte) >= 4 and rfc_contraparte in concepto_upper:
                    tiene_coincidencia_texto = True
                else:
                    for token in tokens_nombre:
                        if token in concepto_upper:
                            tiene_coincidencia_texto = True
                            break

                if not tiene_coincidencia_texto:
                    for alias_key, alias_targets in TRADE_NAME_ALIASES.items():
                        if alias_key in concepto_upper:
                            if any(target in nombre_contraparte or target == rfc_contraparte for target in alias_targets):
                                tiene_coincidencia_texto = True
                                break

                # Coincidencia explícita de identificadores (Folio, Serie, Rastreo, UUID)
                cfdi_ids = _extract_cfdi_identifiers(f)
                is_direct_ref, matched_ref_tag = _matches_direct_reference(concepto_upper, cfdi_ids)

                # Relacionados si es Complemento de Pago (REP)
                f_related = [d["uuid"] for d in f.get("doctos_relacionados", []) if d.get("uuid")]
                rep_tag = " [Complemento de Pago]" if f.get("metodo_pago") == "PAGO" else ""

                # --- Evaluación en Cascada ---
                # Nivel 1: Match Exacto (Determinista)
                # Mismo monto exacto + clave de rastreo / referencia / folio o UUID + ventana ±3 días
                if is_direct_ref and abs(delta_dias) <= 3:
                    cand_status = "CONCILIADO_DIRECTO"
                    cand_score = 1.0
                    cand_nota = f"Match exacto determinista{rep_tag} por referencia/folio ({matched_ref_tag}) e importe (${tx_monto:,.2f}) a {delta_dias}d."
                    candidatos.append((f, 1, cand_nota, cand_score, cand_status, f_related))

                # Nivel 2: Match Fuzzy (1 a 1)
                # Mismo monto exacto + razón social/alias comercial validado contra RFC, sin referencia explícita
                elif tiene_coincidencia_texto and -60 <= delta_dias <= 90:
                    cand_status = "CONCILIADO_POR_REGLA"
                    cand_score = 0.95
                    ant_tag = " [Anticipo]" if delta_dias < 0 else ""
                    cand_nota = f"Match 1:1 por regla comercial{rep_tag}{ant_tag} con {nombre_contraparte[:30]} (RFC: {rfc_contraparte}) por importe (${tx_monto:,.2f}) a {delta_dias}d."
                    candidatos.append((f, 2, cand_nota, cand_score, cand_status, f_related))

                # Casos grises / desfasados -> POR_REVISAR
                elif tiene_coincidencia_texto and (91 <= delta_dias <= 150 or -90 <= delta_dias < -60):
                    candidatos.append((f, 3, f"Monto (${tx_monto:,.2f}) y contraparte ({nombre_contraparte[:30]}) coinciden, pero con desfase de {delta_dias} días.", 0.80, "POR_REVISAR", f_related))
                elif not tiene_coincidencia_texto and -3 <= delta_dias <= 7:
                    candidatos.append((f, 4, f"Monto (${tx_monto:,.2f}) y fecha coinciden con CFDI de {nombre_contraparte[:30]}, pero concepto bancario no contiene contraparte ni folio visible.", 0.70, "POR_REVISAR", f_related))

        if candidatos:
            # Ordenar primero por Tier de coincidencia (1 = Directo, 2 = Regla, etc.) y luego por menor delta en días
            candidatos.sort(key=lambda x: (x[1], abs((tx_fecha - (datetime.strptime(x[0]["fecha_emision"][:10], "%Y-%m-%d") if isinstance(x[0]["fecha_emision"], str) else x[0]["fecha_emision"])).days)))
            ganador, match_tier, nota_revision, confianza_score, status_asignado, related_cfdi_uuids = candidatos[0]

            uuid_asignado = ganador["uuid"]
            facturas_pool.remove(ganador)

            # Si el ganador es un REP, enriquecer nota
            if ganador.get("metodo_pago") == "PAGO":
                num_docs = len(related_cfdi_uuids)
                if ganador.get("tipo") == "INGRESO":
                    nota_revision = f"Pago recibido que ampara {num_docs} factura(s) PPD (Ingreso) - REP: {uuid_asignado[:8]} | {nota_revision}"
                else:
                    nota_revision = f"Pago emitido que ampara {num_docs} factura(s) PPD (Egreso) - REP: {uuid_asignado[:8]} | {nota_revision}"

            # Si ampara facturas hijas (REP), removerlas también del pool
            if related_cfdi_uuids:
                facturas_pool = [inv for inv in facturas_pool if inv["uuid"] not in related_cfdi_uuids]

        # -------------------------------------------------------------
        # FASE 2: Nivel 3 - Pagos Consolidados (N Facturas a 1 Banco)
        # -------------------------------------------------------------
        elif tx_tipo in ("INGRESO", "EGRESO") and tx_monto > 0:
            candidatos_combo = [
                inv for inv in facturas_pool
                if inv["tipo"] == tx_tipo and 0 < round(float(inv["total"]), 2) < tx_monto
            ]

            def _inv_has_text_match(inv_cand):
                nom = (inv_cand.get("nombre_receptor" if tx_tipo == "INGRESO" else "nombre_emisor") or "").upper().strip()
                rfc_c = (inv_cand.get("rfc_receptor" if tx_tipo == "INGRESO" else "rfc_emisor") or "").upper().strip()
                if rfc_c and len(rfc_c) >= 4 and rfc_c in concepto_upper:
                    return True
                for tok in _clean_text_tokens(nom):
                    if tok in concepto_upper:
                        return True
                for alias_key, alias_targets in TRADE_NAME_ALIASES.items():
                    if alias_key in concepto_upper:
                        if any(target in nom or target == rfc_c for target in alias_targets):
                            return True
                return False

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

            # En pagos consolidados N:1, las facturas DEBEN coincidir con la contraparte del movimiento bancario
            # para evitar asociar facturas de un tercero no relacionado a un pago arbitrario
            valid_cands = [c for c in valid_cands if _inv_has_text_match(c)]

            # Buscar todas las combinaciones posibles que sumen el total pagado
            matching_combos = []

            # Combinaciones de 2 facturas
            for i in range(len(valid_cands)):
                for j in range(i + 1, len(valid_cands)):
                    same_counterparty = (
                        (valid_cands[i].get("rfc_emisor") == valid_cands[j].get("rfc_emisor")) or
                        (valid_cands[i].get("rfc_receptor") == valid_cands[j].get("rfc_receptor"))
                    )
                    if not same_counterparty:
                        continue

                    s2 = round(float(valid_cands[i]["total"]) + float(valid_cands[j]["total"]), 2)
                    if abs(s2 - tx_monto) <= 0.05:
                        matching_combos.append([valid_cands[i], valid_cands[j]])

            # Combinaciones de 3 facturas si no hay o si se evalúa exhaustivamente
            if not matching_combos:
                for i in range(len(valid_cands)):
                    for j in range(i + 1, len(valid_cands)):
                        for k in range(j + 1, len(valid_cands)):
                            same_counterparty = (
                                (valid_cands[i].get("rfc_emisor") == valid_cands[j].get("rfc_emisor") == valid_cands[k].get("rfc_emisor")) or
                                (valid_cands[i].get("rfc_receptor") == valid_cands[j].get("rfc_receptor") == valid_cands[k].get("rfc_receptor")) or
                                (_inv_has_text_match(valid_cands[i]) and _inv_has_text_match(valid_cands[j]) and _inv_has_text_match(valid_cands[k]))
                            )
                            if not same_counterparty:
                                continue

                            s3 = round(float(valid_cands[i]["total"]) + float(valid_cands[j]["total"]) + float(valid_cands[k]["total"]), 2)
                            if abs(s3 - tx_monto) <= 0.05:
                                matching_combos.append([valid_cands[i], valid_cands[j], valid_cands[k]])

            # Criterio Agentic de Ambigüedad:
            # Si hay exactamente 1 combinación -> UNÍVOCO: CONCILIADO (confianza 1.0)
            # Si hay múltiples combinaciones posibles de igual suma -> AMBIGUO: POR_REVISAR (confianza 0.7)
            if len(matching_combos) == 1:
                matched_combo = matching_combos[0]
                uuid_asignado = matched_combo[0]["uuid"]
                status_asignado = "CONCILIADO"
                confianza_score = 1.0
                related_cfdi_uuids = [inv["uuid"] for inv in matched_combo]
                desc_combo = " + ".join([f"{inv['uuid'][:8]} (${float(inv['total']):,.2f})" for inv in matched_combo])
                c_nom = matched_combo[0].get("nombre_receptor" if tx_tipo == "INGRESO" else "nombre_emisor", "")
                nota_revision = f"Pago consolidado unívoco de {len(matched_combo)} facturas ({c_nom[:25]}): {desc_combo}"

                for inv_rem in matched_combo:
                    if inv_rem in facturas_pool:
                        facturas_pool.remove(inv_rem)

            elif len(matching_combos) > 1:
                uuid_asignado = matching_combos[0][0]["uuid"]
                status_asignado = "POR_REVISAR"
                confianza_score = 0.70
                nota_revision = f"Posible pago consolidado ambiguo: se detectaron {len(matching_combos)} combinaciones de facturas que suman ${tx_monto:,.2f}."

        # -------------------------------------------------------------
        # FASE 3: Nivel 4 - Clasificación de Discrepancias y Huérfanos
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

        resultado_tx = dict(tx)
        resultado_tx["uuid_cfdi"] = uuid_asignado
        resultado_tx["status_conciliacion"] = status_asignado
        resultado_tx["confianza_score"] = confianza_score
        resultado_tx["nota_revision"] = nota_revision
        resultado_tx["related_cfdi_uuids"] = related_cfdi_uuids
        if uuid_asignado is None and delgadillo_area:
            resultado_tx["area_proyecto"] = delgadillo_area

        resultados.append(resultado_tx)

    # -------------------------------------------------------------
    # FASE 4: Nivel 3 (1 a N) - Split Payments (1 CFDI pagado en múltiples bancos)
    # -------------------------------------------------------------
    unmatched_indices = [
        idx for idx, r in enumerate(resultados)
        if not r.get("uuid_cfdi") and r.get("status_conciliacion") == "SIN_CFDI"
    ]

    if facturas_pool and len(unmatched_indices) >= 2:
        for f in list(facturas_pool):
            f_tipo = f["tipo"]
            f_total = round(float(f["total"]), 2)
            if f_total <= 0:
                continue

            f_fecha = f.get("fecha_pago") or f["fecha_emision"]
            if isinstance(f_fecha, str):
                f_fecha = datetime.strptime(f_fecha[:10], "%Y-%m-%d")
            f_d = f_fecha.date() if hasattr(f_fecha, "date") else f_fecha

            contraparte_name = str((f.get("nombre_receptor") if f_tipo == "INGRESO" else f.get("nombre_emisor")) or "").upper().strip()

            def _cand_matches_vendor(cand_idx: int) -> bool:
                r_conc = str(resultados[cand_idx].get("concepto", "")).upper()
                c_rfc = str((f.get("rfc_emisor") if f_tipo == "EGRESO" else f.get("rfc_receptor")) or "").upper().strip()
                if c_rfc and len(c_rfc) >= 4 and c_rfc in r_conc:
                    return True
                for tok in _clean_text_tokens(contraparte_name):
                    if tok in r_conc:
                        return True
                for alias_key, alias_targets in TRADE_NAME_ALIASES.items():
                    if alias_key in r_conc:
                        if any(target in contraparte_name or target == c_rfc for target in alias_targets):
                            return True
                return False

            cands_idx = []
            for u_idx in unmatched_indices:
                r = resultados[u_idx]
                if r.get("uuid_cfdi") or r.get("tipo") != f_tipo:
                    continue
                r_monto = round(float(r["monto"]), 2)
                if r_monto >= f_total or r_monto <= 0:
                    continue
                r_fecha = r["fecha"]
                if isinstance(r_fecha, str):
                    r_fecha = datetime.strptime(r_fecha[:10], "%Y-%m-%d")
                r_d = r_fecha.date() if hasattr(r_fecha, "date") else r_fecha

                delta = abs((r_d - f_d).days)
                if delta <= 90:
                    cands_idx.append(u_idx)

            found_combo = None
            for i_pos in range(len(cands_idx)):
                for j_pos in range(i_pos + 1, len(cands_idx)):
                    idx_a = cands_idx[i_pos]
                    idx_b = cands_idx[j_pos]
                    matches_vendor = _cand_matches_vendor(idx_a) or _cand_matches_vendor(idx_b)
                    if not matches_vendor:
                        c_a = str(resultados[idx_a].get("concepto", "")).upper()
                        c_b = str(resultados[idx_b].get("concepto", "")).upper()
                        stopwords = {"TARJETA", "TITULAR", "DIGITAL", "CIUDAD", "MEX", "PAGO", "CUENTA", "TERCERO", "SPEI", "ENVIADO", "RECIBIDO", "BNET", "TRANSFERENCIA", "ZAPOPAN", "JAL"}
                        common_tokens = (set(_clean_text_tokens(c_a)) & set(_clean_text_tokens(c_b))) - stopwords
                        if not common_tokens:
                            continue

                    sum_monto = round(float(resultados[idx_a]["monto"]) + float(resultados[idx_b]["monto"]), 2)
                    if abs(sum_monto - f_total) <= 0.05:
                        found_combo = [idx_a, idx_b]
                        break
                if found_combo:
                    break

            if found_combo:
                f_related = [d["uuid"] for d in f.get("doctos_relacionados", []) if d.get("uuid")]
                rep_tag = " [Complemento de Pago]" if f.get("metodo_pago") == "PAGO" else ""
                for pos, c_idx in enumerate(found_combo):
                    tx_c = resultados[c_idx]
                    tx_c["uuid_cfdi"] = f["uuid"]
                    tx_c["status_conciliacion"] = "CONCILIADO"
                    tx_c["confianza_score"] = 1.0
                    tx_c["related_cfdi_uuids"] = f_related
                    tx_c["contraparte"] = contraparte_name
                    tx_c["nota_revision"] = f"Pago parcial ({pos+1} de {len(found_combo)}) para CFDI/REP{rep_tag}: {f['uuid'][:8]} (${f_total:,.2f}) - {contraparte_name[:30]}"

                if f in facturas_pool:
                    facturas_pool.remove(f)
                if f_related:
                    facturas_pool = [inv for inv in facturas_pool if inv["uuid"] not in f_related]

                unmatched_indices = [idx for idx in unmatched_indices if idx not in found_combo]

    return resultados
