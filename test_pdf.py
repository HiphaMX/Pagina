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
    
    logo_path = os.path.join("app", "assets", "logo_hipha.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, w=40)
        pdf.ln(5)
    
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
        ("1. Naturaleza del servicio y Autonomía", "Hipha es un prestador de servicios profesionales independiente. El concepto “Tu departamento externo” es una denominación comercial y no constituye una sociedad mercantil, asociación ni relación de subordinación laboral. Hipha conserva plena autonomía técnica y administrativa. El personal de Hipha no está sujeto a la potestad de mando del Cliente, eliminando cualquier indicio de relación laboral bajo la Ley Federal del Trabajo.\n\nEl cliente puede solicitar asesoría sobre algún tema de su interés, pero será él quien en base a sus necesidades y experiencia direccione los esfuerzos de marketing y diseño, realizando las solicitudes que desde su visión como líder de su empresa puedan mejorar su desempeño comercial y posicionamiento. En ninguna circunstancia el equipo de Hipha está habilitado para tomar decisiones respecto a la operación y funcionamiento de la empresa del Cliente.")
    ]
    
    for title, text in clauses:
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 6, text=title.encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, text=text.encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        
    pdf.ln(10)
    
    # Check if we need to add a new page to avoid page break in the middle of signatures
    if pdf.get_y() > 220:
        pdf.add_page()
    
    y_before_sigs = pdf.get_y()
    
    # Cliente
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 8, text="El Cliente:", new_x="LMARGIN", new_y="NEXT", align="C")
    
    client_sig_path = None
    if hasattr(form_data, 'firma') and form_data.firma:
        if "," in form_data.firma:
            header, encoded = form_data.firma.split(",", 1)
            img_data = base64.b64decode(encoded)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(img_data)
                client_sig_path = tmp.name
                
    if client_sig_path:
        pdf.image(client_sig_path, x=25, y=pdf.get_y(), w=50)
        os.remove(client_sig_path)
    
    pdf.set_y(y_before_sigs + 35)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 5, text="________________________________", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(90, 5, text=form_data.nombre.upper(), new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Hipha
    pdf.set_y(y_before_sigs)
    pdf.set_x(110)
    pdf.cell(90, 8, text="Hipha:", new_x="LMARGIN", new_y="NEXT", align="C")
    
    fran_sig_path = os.path.join("app", "assets", "firma_francisco.jpg")
    if os.path.exists(fran_sig_path):
        pdf.image(fran_sig_path, x=130, y=pdf.get_y(), w=50)
        
    pdf.set_y(y_before_sigs + 35)
    pdf.set_x(110)
    pdf.cell(90, 5, text="________________________________", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_x(110)
    pdf.cell(90, 5, text="FRANCISCO DELGADILLO", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf_bytes = pdf.output()
    return bytes(pdf_bytes)

if __name__ == "__main__":
    data = MockData()
    pdf_data = generate_contract_pdf(data)
    with open("test_contract.pdf", "wb") as f:
        f.write(pdf_data)
    print("PDF generated successfully.")
