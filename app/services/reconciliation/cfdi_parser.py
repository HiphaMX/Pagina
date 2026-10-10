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

    total = float(root.attrib.get('Total') or root.attrib.get('total') or 0.0)
    subtotal = float(root.attrib.get('SubTotal') or root.attrib.get('subtotal') or 0.0)
    metodo_pago = root.attrib.get('MetodoPago') or root.attrib.get('metodoPago') or 'PUE'
    forma_pago = root.attrib.get('FormaPago') or root.attrib.get('formaPago') or ''

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
                if impuesto_tipo == '002':
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
                    elif impuesto_tipo == '002':
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
    conceptos_resumen = " | ".join(conceptos_list[:3]) if conceptos_list else ""

    # 7. Clasificación INGRESO vs EGRESO
    # Si el RFC emisor es igual a mi RFC, la factura es un INGRESO (emitida a un cliente)
    # En cualquier otro caso, es un EGRESO (recibida de un proveedor)
    tipo = "EGRESO"
    if mi_rfc and mi_rfc.strip():
        if rfc_emisor == mi_rfc.strip().upper():
            tipo = "INGRESO"
        else:
            tipo = "EGRESO"
    else:
        # Si no se configuró mi_rfc, evaluar el tipo de comprobante SAT: 'I' = Ingreso
        tipo_comprobante = (root.attrib.get('TipoDeComprobante') or 'I').upper()
        if tipo_comprobante == 'E':  # Nota de crédito
            tipo = "EGRESO"

    iva_ingresos = round(iva_trasladado, 2) if tipo == "INGRESO" else 0.0
    iva_egresos = round(iva_trasladado, 2) if tipo == "EGRESO" else 0.0

    return {
        "uuid": uuid,
        "tipo": tipo,
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
        "conceptos_resumen": conceptos_resumen[:500] if conceptos_resumen else "",
    }
