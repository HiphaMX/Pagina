import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, Optional

def parse_cfdi_xml(xml_content: bytes, mi_rfc: Optional[str] = None) -> Dict[str, Any]:
    """
    Parsea el contenido binario de una factura CFDI (3.3 o 4.0) de forma determinista y extrae
    los metadatos fiscales clave.
    """
    if not xml_content:
        raise ValueError("El contenido del XML está vacío.")

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise ValueError(f"Error de sintaxis XML: {e}")

    # Namespaces estándar del SAT
    ns = {
        'cfdi': 'http://www.sat.gob.mx/cfd/4',
        'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
    }

    # Soporte retrocompatible para CFDI 3.3
    if 'cfd/3' in root.tag:
        ns['cfdi'] = 'http://www.sat.gob.mx/cfd/3'

    # Helper para buscar nodos con o sin namespace
    def find_node(parent, tag_name: str, ns_prefix: str = 'cfdi'):
        # 1. Búsqueda con namespace registrado
        node = parent.find(f'{ns_prefix}:{tag_name}', ns)
        if node is not None:
            return node
        # 2. Búsqueda universal por tag local (ignora el namespace URI)
        for child in parent:
            child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if child_tag == tag_name:
                return child
        return None

    def find_all_nodes(parent, tag_name: str, ns_prefix: str = 'cfdi'):
        nodes = parent.findall(f'{ns_prefix}:{tag_name}', ns)
        if nodes:
            return nodes
        results = []
        for child in parent:
            child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if child_tag == tag_name:
                results.append(child)
        return results

    # 1. Timbre Fiscal Digital (UUID)
    uuid = None
    timbre = root.find('.//tfd:TimbreFiscalDigital', ns)
    if timbre is None:
        # Búsqueda por tag ignorando namespace
        for elem in root.iter():
            tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag_name == 'TimbreFiscalDigital':
                timbre = elem
                break

    if timbre is not None:
        uuid = timbre.attrib.get('UUID') or timbre.attrib.get('uuid')
        if uuid:
            uuid = uuid.strip().upper()

    if not uuid:
        raise ValueError("No se encontró el nodo TimbreFiscalDigital (UUID) en el XML.")

    # 2. Atributos generales del Comprobante
    fecha_raw = root.attrib.get('Fecha') or root.attrib.get('fecha') or ''
    fecha_dt = None
    if fecha_raw:
        try:
            fecha_dt = datetime.fromisoformat(fecha_raw.replace('Z', ''))
        except ValueError:
            try:
                fecha_dt = datetime.strptime(fecha_raw[:10], "%Y-%m-%d")
            except ValueError:
                fecha_dt = datetime.utcnow()
    else:
        fecha_dt = datetime.utcnow()

    tipo_comprobante = (root.attrib.get('TipoDeComprobante') or root.attrib.get('tipoDeComprobante') or 'I').upper()
    total = float(root.attrib.get('Total') or root.attrib.get('total') or 0.0)
    subtotal = float(root.attrib.get('SubTotal') or root.attrib.get('subtotal') or 0.0)
    metodo_pago = root.attrib.get('MetodoPago') or root.attrib.get('metodoPago') or 'PUE'
    forma_pago = root.attrib.get('FormaPago') or root.attrib.get('formaPago') or ''
    serie = (root.attrib.get('Serie') or root.attrib.get('serie') or '').strip()
    folio = (root.attrib.get('Folio') or root.attrib.get('folio') or '').strip()

    # 3. Emisor
    emisor = find_node(root, 'Emisor')
    rfc_emisor = (emisor.attrib.get('Rfc') or emisor.attrib.get('rfc') or '').strip().upper() if emisor is not None else ''
    nombre_emisor = (emisor.attrib.get('Nombre') or emisor.attrib.get('nombre') or '').strip() if emisor is not None else ''

    # 4. Receptor
    receptor = find_node(root, 'Receptor')
    rfc_receptor = (receptor.attrib.get('Rfc') or receptor.attrib.get('rfc') or '').strip().upper() if receptor is not None else ''
    nombre_receptor = (receptor.attrib.get('Nombre') or receptor.attrib.get('nombre') or '').strip() if receptor is not None else ''

    # 5. Impuestos (Traslados y Retenciones)
    iva_trasladado = 0.0
    retenciones_total = 0.0
    retencion_isr = 0.0
    retencion_iva = 0.0

    impuestos = find_node(root, 'Impuestos')
    if impuestos is not None:
        # Traslados (IVA código 002)
        traslados_wrapper = find_node(impuestos, 'Traslados')
        if traslados_wrapper is not None:
            for t in find_all_nodes(traslados_wrapper, 'Traslado'):
                impuesto_tipo = t.attrib.get('Impuesto') or t.attrib.get('impuesto')
                importe_str = t.attrib.get('Importe') or t.attrib.get('importe') or '0'
                if impuesto_tipo in ('002', 'IVA'):
                    try:
                        iva_trasladado += float(importe_str)
                    except ValueError:
                        pass

        # Retenciones (ISR 001 / IVA 002)
        retenciones_wrapper = find_node(impuestos, 'Retenciones')
        if retenciones_wrapper is not None:
            for r in find_all_nodes(retenciones_wrapper, 'Retencion'):
                impuesto_tipo = r.attrib.get('Impuesto') or r.attrib.get('impuesto')
                importe_str = r.attrib.get('Importe') or r.attrib.get('importe') or '0'
                try:
                    r_val = float(importe_str)
                    retenciones_total += r_val
                    if impuesto_tipo == '001':
                        retencion_isr += r_val
                    elif impuesto_tipo in ('002', 'IVA'):
                        retencion_iva += r_val
                except ValueError:
                    pass

    # 6. Conceptos resumidos
    conceptos_list = []
    conceptos_wrapper = find_node(root, 'Conceptos')
    if conceptos_wrapper is not None:
        for c in find_all_nodes(conceptos_wrapper, 'Concepto'):
            desc = c.attrib.get('Descripcion') or c.attrib.get('descripcion') or ''
            if desc:
                conceptos_list.append(desc.strip())
    folio_tag = f"[{serie}-{folio}] " if (serie and folio) else (f"[{folio}] " if folio else (f"[{serie}] " if serie else ""))
    conceptos_resumen = (folio_tag + " | ".join(conceptos_list[:3])).strip() if conceptos_list else folio_tag.strip()

    # 7. Soporte Avanzado para Complemento para Recepción de Pagos (Tipo 'P', CFDI 3.3 y 4.0)
    doctos_relacionados = []
    fecha_pago_dt = None
    es_pago = (tipo_comprobante == 'P')

    pagos_wrapper = None
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local == 'Pagos':
            pagos_wrapper = elem
            es_pago = True
            break

    if es_pago and pagos_wrapper is not None:
        metodo_pago = "PAGO"
        totales_elem = None
        for child in pagos_wrapper:
            if child.tag.split('}')[-1] == 'Totales':
                totales_elem = child
                break

        monto_totales = 0.0
        if totales_elem is not None:
            try:
                monto_totales = float(totales_elem.attrib.get('MontoTotalPagos') or totales_elem.attrib.get('montoTotalPagos') or 0.0)
            except ValueError:
                monto_totales = 0.0
            try:
                iva_tot = float(totales_elem.attrib.get('TotalTrasladosImpuestoIVA16') or 0.0)
                if iva_tot > 0:
                    iva_trasladado = iva_tot
            except ValueError:
                pass

        pago_nodes = [c for c in pagos_wrapper if c.tag.split('}')[-1] == 'Pago']
        monto_pagos_sum = 0.0
        for p in pago_nodes:
            try:
                monto_p = float(p.attrib.get('Monto') or p.attrib.get('monto') or 0.0)
                monto_pagos_sum += monto_p
            except ValueError:
                pass

            fp_raw = p.attrib.get('FechaPago') or p.attrib.get('fechaPago') or ''
            if fp_raw and not fecha_pago_dt:
                try:
                    fecha_pago_dt = datetime.fromisoformat(fp_raw.replace('Z', ''))
                except ValueError:
                    try:
                        fecha_pago_dt = datetime.strptime(fp_raw[:10], "%Y-%m-%d")
                    except ValueError:
                        pass

            fp_code = p.attrib.get('FormaDePagoP') or p.attrib.get('formaDePagoP') or ''
            if fp_code:
                forma_pago = fp_code

            # Buscar DoctoRelacionado dentro de cada Pago
            for elem_sub in p.iter():
                if elem_sub.tag.split('}')[-1] == 'DoctoRelacionado':
                    id_doc = (elem_sub.attrib.get('IdDocumento') or elem_sub.attrib.get('idDocumento') or '').strip().upper()
                    try:
                        imp_pagado = float(elem_sub.attrib.get('ImpPagado') or elem_sub.attrib.get('impPagado') or 0.0)
                    except ValueError:
                        imp_pagado = 0.0
                    try:
                        imp_ant = float(elem_sub.attrib.get('ImpSaldoAnt') or elem_sub.attrib.get('impSaldoAnt') or 0.0)
                    except ValueError:
                        imp_ant = 0.0
                    try:
                        imp_ins = float(elem_sub.attrib.get('ImpSaldoInsoluto') or elem_sub.attrib.get('impSaldoInsoluto') or 0.0)
                    except ValueError:
                        imp_ins = 0.0
                    try:
                        parc = int(elem_sub.attrib.get('NumParcialidad') or elem_sub.attrib.get('numParcialidad') or 1)
                    except ValueError:
                        parc = 1

                    if id_doc:
                        doctos_relacionados.append({
                            "uuid": id_doc,
                            "imp_pagado": imp_pagado,
                            "imp_saldo_ant": imp_ant,
                            "imp_saldo_insoluto": imp_ins,
                            "num_parcialidad": parc
                        })

        final_pago_total = monto_totales if monto_totales > 0 else monto_pagos_sum
        if final_pago_total > 0:
            total = final_pago_total
            if subtotal == 0.0:
                subtotal = round(total - iva_trasladado, 2)

        if fecha_pago_dt:
            fecha_dt = fecha_pago_dt

        if doctos_relacionados:
            docs_summary = ", ".join([f"{d['uuid'][:8]} (${d['imp_pagado']:,.2f})" for d in doctos_relacionados[:3]])
            extra = f" (+{len(doctos_relacionados)-3} más)" if len(doctos_relacionados) > 3 else ""
            conceptos_resumen = f"Complemento de Pago (${total:,.2f}) ampara {len(doctos_relacionados)} factura(s): {docs_summary}{extra}"

    # 8. Soporte para CFDI de Nómina (Tipo 'N')
    es_nomina = (tipo_comprobante == 'N')
    if not es_nomina:
        for elem in root.iter():
            if elem.tag.split('}')[-1] == 'Nomina':
                es_nomina = True
                break

    if es_nomina:
        metodo_pago = "NOMINA"
        if not conceptos_resumen or conceptos_resumen.upper() == "PAGO":
            conceptos_resumen = f"Recibo de Nómina: {nombre_receptor}"

    # 9. Clasificación Fiscal determinista (INGRESO vs EGRESO)
    tipo = "EGRESO"
    mi_rfc_clean = (mi_rfc or "").strip().upper()

    if es_nomina:
        tipo = "EGRESO"
    elif es_pago:
        if mi_rfc_clean and rfc_emisor == mi_rfc_clean:
            tipo = "INGRESO"
        else:
            tipo = "EGRESO"
    elif tipo_comprobante == 'E':
        if mi_rfc_clean and rfc_emisor == mi_rfc_clean:
            tipo = "EGRESO"
        else:
            tipo = "INGRESO"
    else:
        if mi_rfc_clean:
            if rfc_emisor == mi_rfc_clean:
                tipo = "INGRESO"
            else:
                tipo = "EGRESO"
        else:
            tipo = "INGRESO" if tipo_comprobante == 'I' else "EGRESO"

    # Enriquecer conceptos_resumen para Complemento de Pago según clasificación fiscal
    if es_pago and doctos_relacionados:
        docs_summary = ", ".join([f"{d['uuid'][:8]} (${d['imp_pagado']:,.2f})" for d in doctos_relacionados[:3]])
        extra = f" (+{len(doctos_relacionados)-3} más)" if len(doctos_relacionados) > 3 else ""
        if tipo == "INGRESO":
            conceptos_resumen = f"Pago recibido de ${total:,.2f} que ampara {len(doctos_relacionados)} factura(s) PPD (Ingreso): {docs_summary}{extra}"
        else:
            conceptos_resumen = f"Pago emitido a proveedor de ${total:,.2f} que ampara {len(doctos_relacionados)} factura(s) PPD (Egreso): {docs_summary}{extra}"
    elif es_pago and not conceptos_resumen:
        conceptos_resumen = f"Pago recibido de ${total:,.2f} (Ingreso)" if tipo == "INGRESO" else f"Pago emitido de ${total:,.2f} (Egreso)"

    iva_ingresos = round(iva_trasladado, 2) if tipo == "INGRESO" else 0.0
    iva_egresos = round(iva_trasladado, 2) if tipo == "EGRESO" else 0.0

    return {
        "uuid": uuid,
        "tipo": tipo,
        "tipo_comprobante": tipo_comprobante,
        "rfc_emisor": rfc_emisor,
        "nombre_emisor": nombre_emisor,
        "rfc_receptor": rfc_receptor,
        "nombre_receptor": nombre_receptor,
        "fecha_emision": fecha_dt,
        "subtotal": round(subtotal, 2),
        "iva_trasladado": round(iva_trasladado, 2),
        "iva_ingresos": iva_ingresos,
        "iva_egresos": iva_egresos,
        "retencion_isr": round(retencion_isr, 2),
        "retencion_iva": round(retencion_iva, 2),
        "retenciones": round(retenciones_total, 2),
        "total": round(total, 2),
        "metodo_pago": metodo_pago,
        "forma_pago": forma_pago,
        "serie": serie,
        "folio": folio,
        "conceptos_resumen": conceptos_resumen[:500] if conceptos_resumen else "",
        "doctos_relacionados": doctos_relacionados,
        "es_pago": es_pago,
        "es_nomina": es_nomina,
        "fecha_pago": fecha_pago_dt
    }
