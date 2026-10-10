import io
from typing import List, Dict, Any, Optional
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def export_reconciliation_excel(
    transacciones: List[Dict[str, Any]],
    mes_label: str = "",
    entity_name: str = "HIPHA",
    account_rfc: Optional[str] = None
) -> bytes:
    if account_rfc:
        if "MEHA" in account_rfc.upper():
            entity_name = "AMDI"
        elif "DEGF" in account_rfc.upper():
            entity_name = "HIPHA"
    """
    Genera un archivo Excel (.xlsx) estructurado y profesional con la sábana de conciliación
    respetando exactamente la estructura de 14 columnas:
    
    1. FECHA
    2. ÁREA / PROYECTO
    3. FOLIO FISCAL
    4. CLIENTE / PROVEEDOR
    5. CONCEPTO
    6. MÉTODO DE PAGO
    7. INGRESOS
    8. EGRESOS
    9. CFDI
    10. TIPO
    11. SUBTOTAL
    12. IVA INGRESOS
    13. RETENCIÓN ISR
    14. IVA EGRESOS
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    clean_label = (mes_label or "Consolidado").replace("/", "-")
    ws.title = f"Conciliacion_{clean_label}"[:30]

    # Estilos
    font_title = Font(name="Arial", size=13, bold=True, color="FFFFFF")
    fill_title = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")  # Slate 800

    font_header = Font(name="Arial", size=9, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="334155", end_color="334155", fill_type="solid")  # Slate 700

    font_data = Font(name="Arial", size=9, color="000000")
    font_bold = Font(name="Arial", size=9, bold=True, color="000000")

    fill_conciliado = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")  # Verde suave
    font_conciliado = Font(name="Arial", size=9, bold=True, color="166534")

    fill_sin_cfdi = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")  # Rojo suave
    font_sin_cfdi = Font(name="Arial", size=9, bold=True, color="991B1B")

    fill_por_revisar = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")  # Amarillo suave
    font_por_revisar = Font(name="Arial", size=9, bold=True, color="854D0E")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # 1. Título principal
    ws.merge_cells('A1:N1')
    cell_title = ws['A1']
    cell_title.value = f"{entity_name.upper()} - SÁBANA MAESTRA DE CONCILIACIÓN BANCARIA Y FISCAL ({mes_label or 'GENERAL'})"
    cell_title.font = font_title
    cell_title.fill = fill_title
    cell_title.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 32

    # 2. Encabezados de tabla (14 columnas exactas)
    headers = [
        "FECHA",
        "ÁREA / PROYECTO",
        "FOLIO FISCAL",
        "CLIENTE / PROVEEDOR",
        "CONCEPTO",
        "MÉTODO DE PAGO",
        "INGRESOS",
        "EGRESOS",
        "CFDI",
        "TIPO",
        "SUBTOTAL",
        "IVA INGRESOS",
        "RETENCIÓN ISR",
        "IVA EGRESOS",
    ]

    ws.row_dimensions[3].height = 24
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col_idx)
        cell.value = header
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = thin_border

    # 3. Filas de datos
    current_row = 4

    for tx in transacciones:
        fecha_val = tx.get("fecha")
        if isinstance(fecha_val, datetime):
            fecha_str = fecha_val.strftime("%Y-%m-%d")
        else:
            fecha_str = str(fecha_val or "")[:10]

        tipo = str(tx.get("tipo") or "EGRESO").upper()
        monto = float(tx.get("monto") or 0.0)
        status = str(tx.get("status_conciliacion") or "SIN_CFDI").upper()
        uuid = tx.get("uuid_cfdi") or ""
        concepto = tx.get("concepto") or ""
        area_proyecto = tx.get("area_proyecto") or entity_name
        tipo_categoria = tx.get("tipo_categoria") or ("INGRESO" if tipo == "INGRESO" else "GASTO")

        # Datos del CFDI asociado si existen
        factura = tx.get("factura") or {}
        if not isinstance(factura, dict) and hasattr(factura, "nombre_emisor"):
            factura_dict = {
                "uuid": factura.uuid,
                "nombre_emisor": factura.nombre_emisor,
                "nombre_receptor": factura.nombre_receptor,
                "subtotal": factura.subtotal,
                "iva_trasladado": factura.iva_trasladado,
                "retencion_isr": getattr(factura, "retencion_isr", 0.0),
                "retencion_iva": getattr(factura, "retencion_iva", 0.0),
                "retenciones": factura.retenciones,
                "metodo_pago": factura.metodo_pago,
                "area_proyecto": getattr(factura, "area_proyecto", None),
            }
        else:
            factura_dict = factura

        if not area_proyecto and factura_dict.get("area_proyecto"):
            area_proyecto = factura_dict.get("area_proyecto")

        # Contraparte: Si es egreso, el proveedor (emisor del CFDI); si es ingreso, el cliente (receptor)
        if tipo == "INGRESO":
            contraparte = factura_dict.get("nombre_receptor") or tx.get("cliente") or tx.get("contraparte") or ""
            ingresos_val = monto
            egresos_val = 0.0
        else:
            contraparte = factura_dict.get("nombre_emisor") or tx.get("proveedor") or tx.get("contraparte") or ""
            ingresos_val = 0.0
            egresos_val = monto

        metodo_pago = factura_dict.get("metodo_pago") or tx.get("metodo_pago") or "PUE"
        
        # Etiqueta CFDI
        if uuid:
            cfdi_label = "CONCILIADO"
        elif status == "POR_REVISAR":
            cfdi_label = "POR REVISAR"
        else:
            cfdi_label = "SIN CFDI"

        # Montos fiscales
        if uuid:
            subtotal_val = float(factura_dict.get("subtotal") or tx.get("subtotal") or 0.0)
            ret_isr = float(factura_dict.get("retencion_isr") or tx.get("retencion_isr") or 0.0)
            if ret_isr == 0.0 and float(factura_dict.get("retenciones") or tx.get("retenciones") or 0.0) > 0:
                ret_isr = float(factura_dict.get("retenciones") or tx.get("retenciones") or 0.0)

            if tipo == "INGRESO":
                iva_tras = float(factura_dict.get("iva_trasladado") or factura_dict.get("iva") or tx.get("iva_ingresos") or 0.0)
                iva_ingresos_val = iva_tras
                iva_egresos_val = 0.0
            else:
                iva_tras = float(factura_dict.get("iva_trasladado") or factura_dict.get("iva") or tx.get("iva_egresos") or 0.0)
                iva_ingresos_val = 0.0
                iva_egresos_val = iva_tras
        else:
            subtotal_val = 0.0
            iva_ingresos_val = 0.0
            ret_isr = 0.0
            iva_egresos_val = 0.0

        # Asignación celda por celda
        # 1. FECHA
        ws.cell(row=current_row, column=1, value=fecha_str).alignment = Alignment(horizontal='center')
        # 2. ÁREA / PROYECTO
        ws.cell(row=current_row, column=2, value=area_proyecto).alignment = Alignment(horizontal='center')
        # 3. FOLIO FISCAL
        ws.cell(row=current_row, column=3, value=uuid).alignment = Alignment(horizontal='center')
        # 4. CLIENTE / PROVEEDOR
        ws.cell(row=current_row, column=4, value=contraparte).alignment = Alignment(horizontal='left')
        # 5. CONCEPTO
        ws.cell(row=current_row, column=5, value=concepto).alignment = Alignment(horizontal='left')
        # 6. MÉTODO DE PAGO
        ws.cell(row=current_row, column=6, value=metodo_pago).alignment = Alignment(horizontal='center')

        # 7. INGRESOS
        c_ing = ws.cell(row=current_row, column=7, value=ingresos_val if ingresos_val > 0 else 0.0)
        c_ing.number_format = '$#,##0.00'
        c_ing.alignment = Alignment(horizontal='right')

        # 8. EGRESOS
        c_egr = ws.cell(row=current_row, column=8, value=egresos_val if egresos_val > 0 else 0.0)
        c_egr.number_format = '$#,##0.00'
        c_egr.alignment = Alignment(horizontal='right')

        # 9. CFDI
        c_cfdi = ws.cell(row=current_row, column=9, value=cfdi_label)
        c_cfdi.alignment = Alignment(horizontal='center')
        if status == "CONCILIADO":
            c_cfdi.fill = fill_conciliado
            c_cfdi.font = font_conciliado
        elif status == "POR_REVISAR":
            c_cfdi.fill = fill_por_revisar
            c_cfdi.font = font_por_revisar
        else:
            c_cfdi.fill = fill_sin_cfdi
            c_cfdi.font = font_sin_cfdi

        # 10. TIPO
        ws.cell(row=current_row, column=10, value=tipo_categoria).alignment = Alignment(horizontal='center')

        # 11. SUBTOTAL
        c_sub = ws.cell(row=current_row, column=11, value=subtotal_val)
        c_sub.number_format = '$#,##0.00'
        c_sub.alignment = Alignment(horizontal='right')

        # 12. IVA INGRESOS
        c_ivai = ws.cell(row=current_row, column=12, value=iva_ingresos_val)
        c_ivai.number_format = '$#,##0.00'
        c_ivai.alignment = Alignment(horizontal='right')

        # 13. RETENCIÓN ISR
        c_ret = ws.cell(row=current_row, column=13, value=ret_isr)
        c_ret.number_format = '$#,##0.00'
        c_ret.alignment = Alignment(horizontal='right')

        # 14. IVA EGRESOS
        c_ivae = ws.cell(row=current_row, column=14, value=iva_egresos_val)
        c_ivae.number_format = '$#,##0.00'
        c_ivae.alignment = Alignment(horizontal='right')

        # Aplicar bordes y fuentes a la fila
        for col_i in range(1, 15):
            c_cell = ws.cell(row=current_row, column=col_i)
            c_cell.border = thin_border
            if col_i != 9:
                c_cell.font = font_data

        ws.row_dimensions[current_row].height = 20
        current_row += 1

    # 4. Fila de Totales con Fórmulas
    total_row = current_row
    ws.cell(row=total_row, column=5, value="TOTALES").font = font_bold
    ws.cell(row=total_row, column=5).alignment = Alignment(horizontal='right')

    end_row = max(4, current_row - 1)

    # Sumatorias con fórmulas Excel =SUM()
    sum_columns = {
        7: f"=SUM(G4:G{end_row})",   # INGRESOS
        8: f"=SUM(H4:H{end_row})",   # EGRESOS
        11: f"=SUM(K4:K{end_row})",  # SUBTOTAL
        12: f"=SUM(L4:L{end_row})",  # IVA INGRESOS
        13: f"=SUM(M4:M{end_row})",  # RETENCIÓN ISR
        14: f"=SUM(N4:N{end_row})",  # IVA EGRESOS
    }

    border_total = Border(
        top=Side(style='thin', color='000000'),
        bottom=Side(style='double', color='000000'),
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1')
    )

    for col_i in range(1, 15):
        cell_t = ws.cell(row=total_row, column=col_i)
        cell_t.border = border_total
        if col_i in sum_columns:
            cell_t.value = sum_columns[col_i]
            cell_t.number_format = '$#,##0.00'
            cell_t.font = font_bold
            cell_t.alignment = Alignment(horizontal='right')

    ws.row_dimensions[total_row].height = 24

    # 5. Ancho de columnas adaptativo
    col_widths = {
        1: 12,  # FECHA
        2: 18,  # ÁREA / PROYECTO
        3: 38,  # FOLIO FISCAL
        4: 34,  # CLIENTE / PROVEEDOR
        5: 38,  # CONCEPTO
        6: 16,  # MÉTODO DE PAGO
        7: 15,  # INGRESOS
        8: 15,  # EGRESOS
        9: 15,  # CFDI
        10: 16, # TIPO
        11: 15, # SUBTOTAL
        12: 15, # IVA INGRESOS
        13: 15, # RETENCIÓN ISR
        14: 15, # IVA EGRESOS
    }
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()

