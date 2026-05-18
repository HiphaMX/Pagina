import tempfile
import base64
import os
from fpdf import FPDF

class MockData:
    fecha = "18 de mayo de 2026"
    nombre = "Juan Pérez"
    email = "juan@example.com"
    telefono = "+52 55 1234 5678"
    proyecto = "Rebranding Básico"
    forma_pago = "Transferencia electrónica"
    firma = None

def generate_contract_pdf(form_data) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, text="CONTRATO DE SERVICIOS - HIPHA", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, text=f"Fecha de aceptación: {form_data.fecha or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Cliente / Contacto: {form_data.nombre}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Email: {form_data.email}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Teléfono: {form_data.telefono}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Proyecto: {form_data.proyecto or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Forma de Pago: {form_data.forma_pago or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    clauses = [
        ("1. Naturaleza del Contrato y Autonomía", "Hipha es un prestador de servicios profesionales independiente. El concepto “Tu departamento externo” es una denominación comercial y no constituye una sociedad mercantil, asociación ni relación de subordinación laboral. Hipha conserva plena autonomía técnica y administrativa. El personal de Hipha no está sujeto a la potestad de mando del Cliente, eliminando cualquier indicio de relación laboral bajo la Ley Federal del Trabajo.")
    ]
    
    for title, text in clauses:
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 6, text=title.encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, text=text.encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 10, text="Firma del Cliente:", new_x="LMARGIN", new_y="NEXT")
    
    pdf_bytes = pdf.output()
    return bytes(pdf_bytes)

if __name__ == "__main__":
    data = MockData()
    pdf_data = generate_contract_pdf(data)
    with open("test_contract.pdf", "wb") as f:
        f.write(pdf_data)
    print("PDF generated successfully.")
