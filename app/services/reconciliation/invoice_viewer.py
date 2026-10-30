import xml.etree.ElementTree as ET
import html
from datetime import datetime
from typing import Dict, Any, Optional, List


FORMA_PAGO_CATALOG = {
    "01": "01 - Efectivo",
    "02": "02 - Cheque nominativo",
    "03": "03 - Transferencia electrónica de fondos (SPEI)",
    "04": "04 - Tarjeta de crédito",
    "05": "05 - Monedero electrónico",
    "06": "06 - Dinero electrónico",
    "08": "08 - Vales de despensa",
    "12": "12 - Dación en pago",
    "13": "13 - Pago por subrogación",
    "14": "14 - Pago por consignación",
    "15": "15 - Condonación",
    "17": "17 - Compensación",
    "23": "23 - Novación",
    "24": "24 - Confusión",
    "25": "25 - Remisión de deuda",
    "26": "26 - Prescripción o caducidad",
    "27": "27 - A satisfacción del acreedor",
    "28": "28 - Tarjeta de débito",
    "29": "29 - Tarjeta de servicios",
    "30": "30 - Aplicación de anticipos",
    "31": "31 - Intermediario pagos",
    "99": "99 - Por definir",
}

METODO_PAGO_CATALOG = {
    "PUE": "PUE - Pago en una sola exhibición",
    "PPD": "PPD - Pago en parcialidades o diferido",
    "PAGO": "PAGO - Complemento de Recepción de Pagos (REP)",
}

REGIMEN_FISCAL_CATALOG = {
    "601": "601 - General de Ley Personas Morales",
    "603": "603 - Personas Morales con Fines no Lucrativos",
    "605": "605 - Sueldos y Salarios e Ingresos Asimilados a Salarios",
    "606": "606 - Arrendamiento",
    "607": "607 - Régimen de Enajenación o Adquisición de Bienes",
    "608": "608 - Demás ingresos",
    "610": "610 - Residentes en el Extranjero sin Establecimiento Permanente en México",
    "611": "611 - Ingresos por Dividendos (socios y accionistas)",
    "612": "612 - Personas Físicas con Actividades Empresariales y Profesionales",
    "614": "614 - Ingresos por intereses",
    "615": "615 - Régimen de los ingresos por obtención de premios",
    "616": "616 - Sin obligaciones fiscales",
    "620": "620 - Sociedades Cooperativas de Producción que optan por diferir sus ingresos",
    "621": "621 - Incorporación Fiscal",
    "622": "622 - Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras",
    "623": "623 - Opcional para Grupos de Sociedades",
    "624": "624 - Coordinados",
    "625": "625 - Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas",
    "626": "626 - Régimen Simplificado de Confianza (RESICO)",
}

USO_CFDI_CATALOG = {
    "G01": "G01 - Adquisición de mercancías",
    "G02": "G02 - Devoluciones, descuentos o bonificaciones",
    "G03": "G03 - Gastos en general",
    "I01": "I01 - Construcciones",
    "I02": "I02 - Mobilario y equipo de oficina por inversiones",
    "I03": "I03 - Equipo de transporte",
    "I04": "I04 - Equipo de computo y accesorios",
    "I05": "I05 - Dados, troqueles, moldes, matrices y herramental",
    "I06": "I06 - Comunicaciones telefónicas",
    "I07": "I07 - Comunicaciones satelitales",
    "I08": "I08 - Otra maquinaria y equipo",
    "D01": "D01 - Honorarios médicos, dentales y gastos hospitalarios",
    "D02": "D02 - Gastos médicos por incapacidad o discapacidad",
    "D03": "D03 - Gastos funerales",
    "D04": "D04 - Donativos",
    "D05": "D05 - Intereses reales efectivamente pagados por créditos hipotecarios",
    "D07": "D07 - Primas por seguros de gastos médicos",
    "D08": "D08 - Gastos de transportación escolar obligatoria",
    "D10": "D10 - Pagos por servicios educativos (colegiaturas)",
    "P01": "P01 - Por definir",
    "CP01": "CP01 - Pagos",
    "CN01": "CN01 - Nómina",
    "S01": "S01 - Sin efectos fiscales",
}

TIPO_COMPROBANTE_CATALOG = {
    "I": "Ingreso (Factura comercial)",
    "E": "Egreso (Nota de crédito)",
    "P": "Pago (Complemento de Recepción de Pagos)",
    "T": "Traslado",
    "N": "Nómina",
}


def _find_node(parent, tag_name: str):
    for child in parent:
        tag_local = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag_local.lower() == tag_name.lower():
            return child
    return None


def _find_all_nodes(parent, tag_name: str):
    results = []
    for child in parent:
        tag_local = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag_local.lower() == tag_name.lower():
            results.append(child)
    return results


def parse_cfdi_for_view(xml_content: Optional[str], fallback_obj: Any = None) -> Dict[str, Any]:
    """
    Extrae todos los campos requeridos para la representación visual fidedigna del CFDI.
    Si xml_content está disponible, parsea el árbol XML completo. Si no, usa el objeto en BD.
    """
    data = {
        "uuid": "",
        "version": "4.0",
        "tipo_comprobante": "I",
        "tipo_label": "Ingreso (Factura Comercial)",
        "serie": "",
        "folio": "",
        "fecha": "",
        "fecha_timbrado": "",
        "moneda": "MXN",
        "lugar_expedicion": "",
        "metodo_pago": "PUE",
        "metodo_label": "PUE - Pago en una sola exhibición",
        "forma_pago": "03",
        "forma_label": "03 - Transferencia electrónica (SPEI)",
        "emisor_rfc": "",
        "emisor_nombre": "",
        "emisor_regimen": "",
        "emisor_regimen_label": "",
        "receptor_rfc": "",
        "receptor_nombre": "",
        "receptor_regimen": "",
        "receptor_regimen_label": "",
        "receptor_uso": "",
        "receptor_uso_label": "",
        "receptor_cp": "",
        "conceptos": [],
        "subtotal": 0.0,
        "descuento": 0.0,
        "iva_trasladado": 0.0,
        "retencion_isr": 0.0,
        "retencion_iva": 0.0,
        "retenciones_total": 0.0,
        "total": 0.0,
        "doctos_relacionados": [],
        "rfc_prov_certif": "",
        "no_cert_sat": "",
        "no_cert_emisor": "",
        "sello_cfd": "",
        "sello_sat": "",
        "cadena_original_tfd": "",
        "sat_verificacion_url": "",
        "has_xml": False,
    }

    # Poblado inicial con fallback_obj (CFDIInvoice o SatInvoice)
    if fallback_obj:
        data["uuid"] = getattr(fallback_obj, "uuid", "") or ""
        data["emisor_rfc"] = getattr(fallback_obj, "rfc_emisor", None) or getattr(fallback_obj, "emisor_rfc", "") or ""
        data["emisor_nombre"] = getattr(fallback_obj, "nombre_emisor", None) or getattr(fallback_obj, "emisor_nombre", "") or ""
        data["receptor_rfc"] = getattr(fallback_obj, "rfc_receptor", None) or getattr(fallback_obj, "receptor_rfc", "") or ""
        data["receptor_nombre"] = getattr(fallback_obj, "nombre_receptor", None) or getattr(fallback_obj, "receptor_nombre", "") or ""
        data["subtotal"] = float(getattr(fallback_obj, "subtotal", 0.0) or 0.0)
        data["total"] = float(getattr(fallback_obj, "total", 0.0) or 0.0)
        data["iva_trasladado"] = float(getattr(fallback_obj, "iva_trasladado", 0.0) or 0.0)
        data["retencion_isr"] = float(getattr(fallback_obj, "retencion_isr", 0.0) or getattr(fallback_obj, "isr_retenido", 0.0) or 0.0)
        data["retencion_iva"] = float(getattr(fallback_obj, "retencion_iva", 0.0) or getattr(fallback_obj, "iva_retenido", 0.0) or 0.0)
        data["metodo_pago"] = getattr(fallback_obj, "metodo_pago", "PUE") or "PUE"
        data["forma_pago"] = getattr(fallback_obj, "forma_pago", "03") or "03"
        f_dt = getattr(fallback_obj, "fecha_emision", None)
        if f_dt:
            data["fecha"] = f_dt.strftime("%Y-%m-%d %H:%M:%S") if isinstance(f_dt, datetime) else str(f_dt)

        conceptos_raw = getattr(fallback_obj, "conceptos_resumen", "") or ""
        if conceptos_raw:
            data["conceptos"].append({
                "clave_prod_serv": "81111500",
                "cantidad": "1.00",
                "clave_unidad": "E48",
                "unidad": "Servicio",
                "descripcion": conceptos_raw,
                "valor_unitario": data["subtotal"],
                "importe": data["subtotal"],
                "descuento": 0.0
            })

    if not xml_content:
        _finish_metadata(data)
        return data

    try:
        root = ET.fromstring(xml_content.encode("utf-8") if isinstance(xml_content, str) else xml_content)
        data["has_xml"] = True
    except Exception:
        _finish_metadata(data)
        return data

    # 1. Comprobante general
    data["version"] = root.attrib.get("Version") or root.attrib.get("version") or data["version"]
    data["serie"] = root.attrib.get("Serie") or root.attrib.get("serie") or ""
    data["folio"] = root.attrib.get("Folio") or root.attrib.get("folio") or ""
    fecha_attr = root.attrib.get("Fecha") or root.attrib.get("fecha")
    if fecha_attr:
        data["fecha"] = fecha_attr
    data["moneda"] = root.attrib.get("Moneda") or root.attrib.get("moneda") or "MXN"
    data["lugar_expedicion"] = root.attrib.get("LugarExpedicion") or root.attrib.get("lugarExpedicion") or ""
    data["no_cert_emisor"] = root.attrib.get("NoCertificado") or root.attrib.get("noCertificado") or ""
    data["tipo_comprobante"] = (root.attrib.get("TipoDeComprobante") or root.attrib.get("tipoDeComprobante") or "I").upper()
    data["metodo_pago"] = root.attrib.get("MetodoPago") or root.attrib.get("metodoPago") or data["metodo_pago"]
    data["forma_pago"] = root.attrib.get("FormaPago") or root.attrib.get("formaPago") or data["forma_pago"]

    try:
        data["subtotal"] = float(root.attrib.get("SubTotal") or root.attrib.get("subtotal") or data["subtotal"])
        data["total"] = float(root.attrib.get("Total") or root.attrib.get("total") or data["total"])
        data["descuento"] = float(root.attrib.get("Descuento") or root.attrib.get("descuento") or 0.0)
    except Exception:
        pass

    # 2. Emisor
    emisor_node = _find_node(root, "Emisor")
    if emisor_node is not None:
        data["emisor_rfc"] = (emisor_node.attrib.get("Rfc") or emisor_node.attrib.get("rfc") or data["emisor_rfc"]).strip().upper()
        data["emisor_nombre"] = (emisor_node.attrib.get("Nombre") or emisor_node.attrib.get("nombre") or data["emisor_nombre"]).strip()
        data["emisor_regimen"] = emisor_node.attrib.get("RegimenFiscal") or emisor_node.attrib.get("regimenFiscal") or ""

    # 3. Receptor
    receptor_node = _find_node(root, "Receptor")
    if receptor_node is not None:
        data["receptor_rfc"] = (receptor_node.attrib.get("Rfc") or receptor_node.attrib.get("rfc") or data["receptor_rfc"]).strip().upper()
        data["receptor_nombre"] = (receptor_node.attrib.get("Nombre") or receptor_node.attrib.get("nombre") or data["receptor_nombre"]).strip()
        data["receptor_regimen"] = receptor_node.attrib.get("RegimenFiscalReceptor") or receptor_node.attrib.get("regimenFiscalReceptor") or ""
        data["receptor_uso"] = receptor_node.attrib.get("UsoCFDI") or receptor_node.attrib.get("usoCFDI") or ""
        data["receptor_cp"] = receptor_node.attrib.get("DomicilioFiscalReceptor") or receptor_node.attrib.get("domicilioFiscalReceptor") or ""

    # 4. Conceptos
    conceptos_node = _find_node(root, "Conceptos")
    if conceptos_node is not None:
        xml_conceptos = []
        for c in _find_all_nodes(conceptos_node, "Concepto"):
            try:
                xml_conceptos.append({
                    "clave_prod_serv": c.attrib.get("ClaveProdServ") or c.attrib.get("claveProdServ") or "",
                    "cantidad": c.attrib.get("Cantidad") or c.attrib.get("cantidad") or "1",
                    "clave_unidad": c.attrib.get("ClaveUnidad") or c.attrib.get("claveUnidad") or "",
                    "unidad": c.attrib.get("Unidad") or c.attrib.get("unidad") or "",
                    "descripcion": c.attrib.get("Descripcion") or c.attrib.get("descripcion") or "",
                    "valor_unitario": float(c.attrib.get("ValorUnitario") or c.attrib.get("valorUnitario") or 0.0),
                    "importe": float(c.attrib.get("Importe") or c.attrib.get("importe") or 0.0),
                    "descuento": float(c.attrib.get("Descuento") or c.attrib.get("descuento") or 0.0),
                })
            except Exception:
                continue
        if xml_conceptos:
            data["conceptos"] = xml_conceptos

    # 5. Impuestos globales
    impuestos_node = _find_node(root, "Impuestos")
    if impuestos_node is not None:
        try:
            data["iva_trasladado"] = float(impuestos_node.attrib.get("TotalImpuestosTrasladados") or impuestos_node.attrib.get("totalImpuestosTrasladados") or data["iva_trasladado"])
            data["retenciones_total"] = float(impuestos_node.attrib.get("TotalImpuestosRetenidos") or impuestos_node.attrib.get("totalImpuestosRetenidos") or 0.0)
        except Exception:
            pass

        # Desglose de retenciones
        ret_wrapper = _find_node(impuestos_node, "Retenciones")
        if ret_wrapper is not None:
            for r in _find_all_nodes(ret_wrapper, "Retencion"):
                imp = r.attrib.get("Impuesto") or r.attrib.get("impuesto")
                try:
                    val = float(r.attrib.get("Importe") or r.attrib.get("importe") or 0.0)
                    if imp == "001":
                        data["retencion_isr"] += val
                    elif imp in ("002", "IVA"):
                        data["retencion_iva"] += val
                except Exception:
                    pass

    # 6. Soporte de Complemento de Pago (REP)
    for elem in root.iter():
        tag_local = elem.tag.split("}")[-1]
        if tag_local == "Pagos":
            data["tipo_comprobante"] = "P"
            data["metodo_pago"] = "PAGO"
            for docto in elem.iter():
                d_tag = docto.tag.split("}")[-1]
                if d_tag == "DoctoRelacionado":
                    data["doctos_relacionados"].append({
                        "id_documento": docto.attrib.get("IdDocumento") or docto.attrib.get("idDocumento") or "",
                        "serie": docto.attrib.get("Serie") or "",
                        "folio": docto.attrib.get("Folio") or "",
                        "moneda": docto.attrib.get("MonedaDR") or "MXN",
                        "num_parcialidad": docto.attrib.get("NumParcialidad") or "1",
                        "imp_saldo_ant": float(docto.attrib.get("ImpSaldoAnt") or 0.0),
                        "imp_pagado": float(docto.attrib.get("ImpPagado") or 0.0),
                        "imp_saldo_insoluto": float(docto.attrib.get("ImpSaldoInsoluto") or 0.0),
                    })

    # 7. Timbre Fiscal Digital (SAT)
    timbre = None
    for elem in root.iter():
        if elem.tag.split("}")[-1] == "TimbreFiscalDigital":
            timbre = elem
            break

    if timbre is not None:
        data["uuid"] = timbre.attrib.get("UUID") or timbre.attrib.get("uuid") or data["uuid"]
        data["fecha_timbrado"] = timbre.attrib.get("FechaTimbrado") or timbre.attrib.get("fechaTimbrado") or ""
        data["rfc_prov_certif"] = timbre.attrib.get("RfcProvCertif") or timbre.attrib.get("rfcProvCertif") or ""
        data["no_cert_sat"] = timbre.attrib.get("NoCertificadoSAT") or timbre.attrib.get("noCertificadoSAT") or ""
        data["sello_cfd"] = timbre.attrib.get("SelloCFD") or timbre.attrib.get("selloCFD") or ""
        data["sello_sat"] = timbre.attrib.get("SelloSAT") or timbre.attrib.get("selloSAT") or ""

    _finish_metadata(data)
    return data


def _finish_metadata(data: Dict[str, Any]):
    data["uuid"] = (data.get("uuid") or "").strip().upper()
    data["tipo_label"] = TIPO_COMPROBANTE_CATALOG.get(data.get("tipo_comprobante", "I"), "Comprobante Fiscal")
    data["metodo_label"] = METODO_PAGO_CATALOG.get(data.get("metodo_pago", ""), data.get("metodo_pago", ""))
    data["forma_label"] = FORMA_PAGO_CATALOG.get(data.get("forma_pago", ""), data.get("forma_pago", ""))
    data["emisor_regimen_label"] = REGIMEN_FISCAL_CATALOG.get(data.get("emisor_regimen", ""), data.get("emisor_regimen", ""))
    data["receptor_regimen_label"] = REGIMEN_FISCAL_CATALOG.get(data.get("receptor_regimen", ""), data.get("receptor_regimen", ""))
    data["receptor_uso_label"] = USO_CFDI_CATALOG.get(data.get("receptor_uso", ""), data.get("receptor_uso", ""))

    sello_last8 = (data.get("sello_cfd") or "")[-8:]
    total_fmt = f"{data.get('total', 0.0):.6f}"
    data["sat_verificacion_url"] = (
        f"https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?"
        f"id={data['uuid']}&re={data['emisor_rfc']}&rr={data['receptor_rfc']}&tt={total_fmt}&fe={sello_last8}"
    )


def render_invoice_html(inv: Dict[str, Any]) -> str:
    """
    Genera el HTML del visor web oficial de la factura.
    """
    uuid_str = html.escape(inv.get("uuid") or "SIN-UUID")
    serie_folio = html.escape(f"{inv.get('serie', '')} {inv.get('folio', '')}".strip() or "S/F")
    tipo_label = html.escape(inv.get("tipo_label") or "Ingreso")
    version = html.escape(inv.get("version") or "4.0")

    emisor_nombre = html.escape(inv.get("emisor_nombre") or "Sin Nombre")
    emisor_rfc = html.escape(inv.get("emisor_rfc") or "")
    emisor_regimen = html.escape(inv.get("emisor_regimen_label") or inv.get("emisor_regimen") or "N/A")

    receptor_nombre = html.escape(inv.get("receptor_nombre") or "Sin Nombre")
    receptor_rfc = html.escape(inv.get("receptor_rfc") or "")
    receptor_regimen = html.escape(inv.get("receptor_regimen_label") or inv.get("receptor_regimen") or "N/A")
    receptor_uso = html.escape(inv.get("receptor_uso_label") or inv.get("receptor_uso") or "N/A")
    receptor_cp = html.escape(inv.get("receptor_cp") or "N/A")

    fecha_emision = html.escape(inv.get("fecha") or "N/A")
    fecha_timbrado = html.escape(inv.get("fecha_timbrado") or fecha_emision)
    lugar_exp = html.escape(inv.get("lugar_expedicion") or "N/A")
    moneda = html.escape(inv.get("moneda") or "MXN")

    metodo_pago = html.escape(inv.get("metodo_label") or "N/A")
    forma_pago = html.escape(inv.get("forma_label") or "N/A")

    subtotal = inv.get("subtotal") or 0.0
    descuento = inv.get("descuento") or 0.0
    iva = inv.get("iva_trasladado") or 0.0
    ret_isr = inv.get("retencion_isr") or 0.0
    ret_iva = inv.get("retencion_iva") or 0.0
    total = inv.get("total") or 0.0

    conceptos_rows = ""
    for c in inv.get("conceptos", []):
        conceptos_rows += f"""
        <tr>
            <td class="mono">{html.escape(str(c.get('clave_prod_serv', '')))}</td>
            <td style="text-align:center;">{html.escape(str(c.get('cantidad', '1')))}</td>
            <td style="text-align:center;">{html.escape(str(c.get('clave_unidad', '')))} {html.escape(str(c.get('unidad', '')))}</td>
            <td>
                <div style="font-weight:600; color:#0f172a;">{html.escape(str(c.get('descripcion', '')))}</div>
            </td>
            <td class="num">${float(c.get('valor_unitario', 0.0)):,.2f}</td>
            <td class="num">${float(c.get('importe', 0.0)):,.2f}</td>
        </tr>
        """

    doctos_rows = ""
    if inv.get("doctos_relacionados"):
        for d in inv["doctos_relacionados"]:
            doctos_rows += f"""
            <tr>
                <td class="mono">{html.escape(d.get('id_documento', ''))}</td>
                <td>{html.escape(d.get('serie', ''))} {html.escape(d.get('folio', ''))}</td>
                <td style="text-align:center;">{html.escape(str(d.get('num_parcialidad', '1')))}</td>
                <td class="num">${float(d.get('imp_saldo_ant', 0.0)):,.2f}</td>
                <td class="num" style="color:#059669; font-weight:700;">${float(d.get('imp_pagado', 0.0)):,.2f}</td>
                <td class="num">${float(d.get('imp_saldo_insoluto', 0.0)):,.2f}</td>
            </tr>
            """

    doctos_section = ""
    if doctos_rows:
        doctos_section = f"""
        <div class="card" style="margin-top: 1.5rem;">
            <h3 style="font-size: 0.95rem; font-weight: 700; color: #0284c7; margin-bottom: 0.75rem;">
                Documentos Relacionados Amparados (Complemento para Recepción de Pagos)
            </h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Folio Fiscal UUID Relacionado</th>
                        <th>Serie/Folio</th>
                        <th style="text-align:center;">Parcialidad</th>
                        <th style="text-align:right;">Saldo Anterior</th>
                        <th style="text-align:right;">Monto Pagado</th>
                        <th style="text-align:right;">Saldo Insoluto</th>
                    </tr>
                </thead>
                <tbody>
                    {doctos_rows}
                </tbody>
            </table>
        </div>
        """

    xml_url = f"/api/dashboard/reconciliation/invoices/{uuid_str}/xml"
    sat_url = inv.get("sat_verificacion_url") or "#"

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Factura CFDI {serie_folio} - {emisor_rfc} | Hipha Control Fiscal</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23059669'><path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/></svg>">
    <style>
        :root {{
            --bg: #0b0f19;
            --surface: #ffffff;
            --border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #059669;
            --primary-hover: #047857;
            --sky: #0284c7;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background: #f1f5f9;
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5;
            padding-bottom: 3rem;
        }}
        .top-bar {{
            background: #0f172a;
            color: #ffffff;
            padding: 0.85rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .top-bar-left {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .brand-badge {{
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}
        .top-actions {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.5rem 0.9rem;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.15s ease;
            border: 1px solid transparent;
        }}
        .btn-primary {{
            background: #059669;
            color: #ffffff;
        }}
        .btn-primary:hover {{
            background: #047857;
        }}
        .btn-secondary {{
            background: #1e293b;
            color: #f1f5f9;
            border-color: #334155;
        }}
        .btn-secondary:hover {{
            background: #334155;
        }}
        .btn-outline {{
            background: transparent;
            color: #cbd5e1;
            border-color: #475569;
        }}
        .btn-outline:hover {{
            color: #ffffff;
            border-color: #94a3b8;
        }}
        .btn-sat {{
            background: rgba(2, 132, 199, 0.2);
            color: #38bdf8;
            border-color: rgba(56, 189, 248, 0.4);
        }}
        .btn-sat:hover {{
            background: rgba(2, 132, 199, 0.35);
        }}
        .page-container {{
            max-width: 960px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}
        .invoice-paper {{
            background: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
            padding: 2.5rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        }}
        .invoice-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #0f172a;
            padding-bottom: 1.5rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1.5rem;
        }}
        .invoice-title-block h1 {{
            font-size: 1.45rem;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.02em;
        }}
        .invoice-title-block p {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 0.2rem;
        }}
        .uuid-badge {{
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            padding: 0.65rem 0.9rem;
            border-radius: 8px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.78rem;
            color: #0f172a;
            text-align: right;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.25rem;
            margin-bottom: 1.5rem;
        }}
        .card {{
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.15rem;
        }}
        .card-header {{
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #475569;
            margin-bottom: 0.65rem;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 0.35rem;
        }}
        .meta-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.35rem;
            font-size: 0.82rem;
        }}
        .meta-label {{
            color: var(--text-muted);
            font-weight: 500;
        }}
        .meta-val {{
            color: var(--text-main);
            font-weight: 600;
            text-align: right;
            max-width: 60%;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.5rem;
            font-size: 0.82rem;
        }}
        .data-table th {{
            background: #0f172a;
            color: #ffffff;
            font-weight: 600;
            padding: 0.65rem 0.75rem;
            text-align: left;
            font-size: 0.78rem;
        }}
        .data-table td {{
            padding: 0.65rem 0.75rem;
            border-bottom: 1px solid #e2e8f0;
        }}
        .data-table tbody tr:nth-child(even) {{
            background: #f8fafc;
        }}
        .mono {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.75rem;
        }}
        .num {{
            text-align: right;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }}
        .totals-section {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-top: 1.5rem;
            flex-wrap: wrap;
            gap: 1.5rem;
        }}
        .totals-meta {{
            flex: 1;
            min-width: 280px;
        }}
        .totals-box {{
            width: 320px;
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
        }}
        .total-highlight {{
            border-top: 2px solid #0f172a;
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            font-size: 1.15rem;
            font-weight: 800;
            color: #059669;
            display: flex;
            justify-content: space-between;
        }}
        .stamp-box {{
            margin-top: 2rem;
            border-top: 1px dashed #cbd5e1;
            padding-top: 1.25rem;
            font-size: 0.7rem;
            color: #64748b;
        }}
        .stamp-field {{
            margin-bottom: 0.75rem;
        }}
        .stamp-title {{
            font-weight: 700;
            color: #334155;
            margin-bottom: 0.15rem;
            text-transform: uppercase;
            font-size: 0.68rem;
        }}
        .stamp-content {{
            word-break: break-all;
            background: #f1f5f9;
            padding: 0.4rem 0.6rem;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
            font-family: ui-monospace, monospace;
        }}
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .top-bar {{
                display: none !important;
            }}
            .page-container {{
                max-width: 100%;
                margin: 0;
                padding: 0;
            }}
            .invoice-paper {{
                box-shadow: none;
                border: none;
                padding: 0;
            }}
        }}
    </style>
</head>
<body>

    <!-- Barra Superior Interactiva -->
    <header class="top-bar">
        <div class="top-bar-left">
            <span class="brand-badge">CFDI {version} Oficial</span>
            <span style="font-weight: 600; font-size: 0.9rem;">Visor de Factura Digital</span>
        </div>
        <div class="top-actions">
            <a href="/projects/HiphaMX/dashboard/?search={uuid_str}#reconciliation" class="btn btn-outline">
                ← Dashboard
            </a>
            <a href="{xml_url}" class="btn btn-primary" download>
                <svg width="15" height="15" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                Descargar XML
            </a>
            <button onclick="window.print()" class="btn btn-secondary">
                <svg width="15" height="15" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
                Imprimir / PDF
            </button>
            <a href="{sat_url}" target="_blank" rel="noopener noreferrer" class="btn btn-sat" title="Verificar validez ante el SAT">
                <svg width="15" height="15" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                Verificar SAT
            </a>
        </div>
    </header>

    <div class="page-container">
        <main class="invoice-paper">
            
            <!-- Encabezado de Factura -->
            <div class="invoice-header">
                <div class="invoice-title-block">
                    <h1>COMPROBANTE FISCAL DIGITAL (CFDI)</h1>
                    <p>{tipo_label} • Versión {version}</p>
                    <div style="margin-top: 0.5rem; display: flex; gap: 0.5rem; align-items: center;">
                        <span style="font-weight: 700; color: #059669; font-size: 0.95rem;">Serie y Folio: {serie_folio}</span>
                    </div>
                </div>
                <div class="uuid-badge">
                    <div style="color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase;">Folio Fiscal Digital (UUID)</div>
                    <div style="font-weight: 700; font-size: 0.9rem; margin-top: 0.2rem; color: #0284c7;">{uuid_str}</div>
                    <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.35rem;">
                        Certificación SAT: {fecha_timbrado}
                    </div>
                </div>
            </div>

            <!-- Fichas Emisor y Receptor -->
            <div class="grid-2">
                <!-- Emisor -->
                <div class="card">
                    <div class="card-header">Datos del Emisor</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-bottom: 0.4rem;">{emisor_nombre}</div>
                    <div class="meta-row">
                        <span class="meta-label">RFC Emisor:</span>
                        <span class="meta-val mono" style="color: #0284c7;">{emisor_rfc}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Régimen Fiscal:</span>
                        <span class="meta-val">{emisor_regimen}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Lugar Expedición (C.P.):</span>
                        <span class="meta-val">{lugar_exp}</span>
                    </div>
                </div>

                <!-- Receptor -->
                <div class="card">
                    <div class="card-header">Datos del Receptor</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-bottom: 0.4rem;">{receptor_nombre}</div>
                    <div class="meta-row">
                        <span class="meta-label">RFC Receptor:</span>
                        <span class="meta-val mono" style="color: #0284c7;">{receptor_rfc}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Uso de CFDI:</span>
                        <span class="meta-val">{receptor_uso}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Régimen Receptor:</span>
                        <span class="meta-val">{receptor_regimen}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Domicilio Fiscal (C.P.):</span>
                        <span class="meta-val">{receptor_cp}</span>
                    </div>
                </div>
            </div>

            <!-- Tabla de Conceptos -->
            <div style="margin-top: 1.5rem;">
                <h2 style="font-size: 0.95rem; font-weight: 700; color: #334155; margin-bottom: 0.6rem; text-transform: uppercase; letter-spacing: 0.04em;">
                    Conceptos Facturados
                </h2>
                <div style="overflow-x: auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Clave SAT</th>
                                <th style="text-align:center;">Cant.</th>
                                <th style="text-align:center;">Unidad</th>
                                <th>Descripción del Bien o Servicio</th>
                                <th style="text-align:right;">P. Unitario</th>
                                <th style="text-align:right;">Importe</th>
                            </tr>
                        </thead>
                        <tbody>
                            {conceptos_rows}
                        </tbody>
                    </table>
                </div>
            </div>

            {doctos_section}

            <!-- Sección de Totales y Pagos -->
            <div class="totals-section">
                <div class="totals-meta">
                    <div class="card">
                        <div class="card-header">Detalles de Pago y Validez</div>
                        <div class="meta-row">
                            <span class="meta-label">Método de Pago:</span>
                            <span class="meta-val">{metodo_pago}</span>
                        </div>
                        <div class="meta-row">
                            <span class="meta-label">Forma de Pago:</span>
                            <span class="meta-val">{forma_pago}</span>
                        </div>
                        <div class="meta-row">
                            <span class="meta-label">Moneda:</span>
                            <span class="meta-val">{moneda}</span>
                        </div>
                        <div class="meta-row">
                            <span class="meta-label">Fecha de Emisión:</span>
                            <span class="meta-val">{fecha_emision}</span>
                        </div>
                    </div>
                </div>

                <div class="totals-box">
                    <div class="meta-row">
                        <span class="meta-label">Subtotal:</span>
                        <span class="meta-val num">${subtotal:,.2f}</span>
                    </div>
                    {f'<div class="meta-row"><span class="meta-label">Descuento:</span><span class="meta-val num" style="color:#ef4444;">-${descuento:,.2f}</span></div>' if descuento > 0 else ''}
                    <div class="meta-row">
                        <span class="meta-label">IVA Trasladado (16%):</span>
                        <span class="meta-val num">${iva:,.2f}</span>
                    </div>
                    {f'<div class="meta-row"><span class="meta-label">Retención ISR:</span><span class="meta-val num" style="color:#f59e0b;">-${ret_isr:,.2f}</span></div>' if ret_isr > 0 else ''}
                    {f'<div class="meta-row"><span class="meta-label">Retención IVA:</span><span class="meta-val num" style="color:#f59e0b;">-${ret_iva:,.2f}</span></div>' if ret_iva > 0 else ''}
                    <div class="total-highlight">
                        <span>TOTAL:</span>
                        <span class="num">${total:,.2f} {moneda}</span>
                    </div>
                </div>
            </div>

            <!-- Timbre Fiscal Digital del SAT -->
            <div class="stamp-box">
                <div style="display:flex; justify-content:space-between; margin-bottom:0.75rem; flex-wrap:wrap; gap:0.5rem;">
                    <div><strong>RFC Proveedor de Certificación:</strong> {html.escape(inv.get('rfc_prov_certif') or 'SAT970701NN3')}</div>
                    <div><strong>No. Certificado SAT:</strong> {html.escape(inv.get('no_cert_sat') or 'N/A')}</div>
                    <div><strong>No. Certificado Emisor:</strong> {html.escape(inv.get('no_cert_emisor') or 'N/A')}</div>
                </div>
                
                {f'<div class="stamp-field"><div class="stamp-title">Sello Digital del CFDI</div><div class="stamp-content">{html.escape(inv.get("sello_cfd", "")[:120])}...</div></div>' if inv.get("sello_cfd") else ''}
                {f'<div class="stamp-field"><div class="stamp-title">Sello Digital del SAT</div><div class="stamp-content">{html.escape(inv.get("sello_sat", "")[:120])}...</div></div>' if inv.get("sello_sat") else ''}
            </div>

        </main>
    </div>

</body>
</html>"""

