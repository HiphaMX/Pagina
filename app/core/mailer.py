import logging
import aiosmtplib
import tempfile
import base64
import os
from fpdf import FPDF
from email.message import EmailMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

def generate_contract_pdf(form_data) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, text="CONTRATO DE SERVICIOS - HIPHA", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, text=f"Fecha de aceptacion: {getattr(form_data, 'fecha', '') or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Cliente / Contacto: {form_data.nombre}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Email: {form_data.email}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Telefono: {form_data.telefono}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Proyecto: {getattr(form_data, 'proyecto', '') or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Forma de Pago: {getattr(form_data, 'forma_pago', '') or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    clauses = [
        ("1. Naturaleza del Contrato y Autonomia", "Hipha es un prestador de servicios profesionales independiente. El concepto “Tu departamento externo” es una denominacion comercial y no constituye una sociedad mercantil, asociacion ni relacion de subordinacion laboral. Hipha conserva plena autonomia tecnica y administrativa. El personal de Hipha no esta sujeto a la potestad de mando del Cliente, eliminando cualquier indicio de relacion laboral bajo la Ley Federal del Trabajo."),
        ("2. Gestion de Proyecto y Comunicacion", "El Cliente designara un 'Responsable de Proyecto' unico con facultades suficientes para autorizar entregables y presupuestos. Las instrucciones de otros socios o terceros no seran vinculantes. La ventana de comunicacion para reuniones virtuales es de lunes a viernes de 9:00 am a 12:00 pm (Hora Centro de Mexico). Reuniones presenciales estaran sujetas a disponibilidad y podran generar cargos adicionales por traslados y viaticos."),
        ("3. Procesamiento de Solicitudes y Terceros", "Toda solicitud de diseño o estrategia requiere un plazo minimo de 72 horas habiles para inicio de gestion. Hipha no actua como comisionista ni intermediario en pagos a terceros. Si el Cliente solicita que Hipha gestione archivos con proveedores externos (imprentas, medios, etc.), Hipha se deslinda de cualquier error en la ejecucion, calidad, tiempos de entrega o vicios ocultos de dichos terceros. La ejecucion fisica (recolecciones, instalaciones) es responsabilidad del personal interno del Cliente."),
        ("4. Responsabilidad y Seguridad del Cliente", "La vigencia de los tiempos de entrega inicia tras la recepcion total de los insumos (Brief, manuales, accesos). El retraso del Cliente no suspende la obligacion de pago de las facturas o igualas pactadas. Respecto al Protocolo de Seguridad, el Cliente es responsable total de sus claves y accesos. Hipha se deslinda de hackeos, bloqueos o ataques derivados de acciones del Cliente o terceros ajenos a la agencia. Al finalizar la relacion, el Cliente debe revocar accesos en un plazo maximo de 24 horas."),
        ("5. Propiedad Intelectual y Uso de Portafolio", "La transferencia de derechos patrimoniales de los entregables finales (diseños publicados, sitios web, fotos de producto) ocurrira unicamente tras la liquidacion del 100% del pago. Hipha conserva la propiedad intelectual de sus metodologias, procesos internos, flujos de trabajo, estrategias preexistentes y archivos fuente (editables). Salvo existencia de un acuerdo de confidencialidad (NDA) explicito, el Cliente autoriza a Hipha a utilizar muestras del trabajo para su portafolio y redes sociales."),
        ("6. Rescision y Suspension de Servicio", "Cualquier parte podra dar por terminado el servicio con un aviso previo de 30 dias naturales. En caso de impago, Hipha queda facultado para suspender total o parcialmente los servicios (pausar campañas, retirar servicios digitales) sin responsabilidad alguna por perdidas economicas, daños o perjuicios que esta interrupcion pudiera causar al Cliente."),
        ("7. Limite de Responsabilidad", "La responsabilidad total de Hipha ante cualquier reclamacion derivada de la prestacion de los servicios, ya sea por negligencia, error u omision, estara limitada como maximo al monto total pagado por el Cliente en el mes inmediato anterior a la fecha de la reclamacion. Bajo ninguna circunstancia Hipha sera responsable por lucro cesante o daños indirectos."),
        ("8. Clausula de No Solicitud (Anti-Poaching)", "El Cliente se compromete a no contratar, solicitar, ni emplear de manera directa o indirecta a ningun colaborador, empleado o consultor de Hipha durante la vigencia de este contrato y hasta por 12 meses posteriores a su terminacion. El incumplimiento de esta clausula generara una pena convencional equivalente a 12 meses de la iguala vigente al momento del incumplimiento."),
        ("9. Jurisdiccion y Competencia", "Para la interpretacion y cumplimiento del presente, las partes se someten a las leyes comerciales de Mexico y a la jurisdiccion de los tribunales competentes en la ciudad de Guadalajara, Jalisco, renunciando expresamente a cualquier otro fuero que pudiera corresponderles por razon de sus domicilios presentes o futuros.")
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
    
    if hasattr(form_data, 'firma') and form_data.firma:
        try:
            if "," in form_data.firma:
                header, encoded = form_data.firma.split(",", 1)
                img_data = base64.b64decode(encoded)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(img_data)
                    tmp_path = tmp.name
                
                pdf.image(tmp_path, w=80)
                os.remove(tmp_path)
        except Exception as e:
            logger.error(f"Error procesando firma para PDF: {e}")
            pdf.multi_cell(0, 10, text=f"[Firma Digital Aplicada - Error renderizando imagen]", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.multi_cell(0, 10, text="[Firma no proporcionada]", new_x="LMARGIN", new_y="NEXT")
        
    return bytes(pdf.output())

async def send_lead_followup_email(lead_name: str, lead_email: str):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP not configurado. Simulando envío para {lead_email} (Lead: {lead_name})")
        return True

    message = EmailMessage()
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = lead_email
    message["Subject"] = f"¡Hola {lead_name}! Recibimos tu solicitud en HiphaMX"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0;">
        <div style="background-color: #050810; padding: 30px; text-align: center;">
            <img src="https://hipha.mx/projects/HiphaMX/HiphaIdentidad/Logotipo/HiphaWhite.svg" alt="Hipha Logo" style="height: 40px; margin: 0 auto; display: block;">
        </div>
        <div style="padding: 20px;">
            <h2>¡Hola {lead_name}!</h2>
            <p>Hemos recibido tus datos con éxito. En breve, uno de nuestros creativos o estrategas se pondrá en contacto contigo para platicar sobre cómo podemos potenciar el crecimiento de tu marca.</p>
            <p>Mientras tanto, puedes explorar nuestro ecosistema de soluciones en nuestra web.</p>
            <br>
            <p>Atentamente,<br><strong>El equipo de Hipha</strong></p>
        </div>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        logger.info(f"Correo enviado exitosamente a {lead_email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo a {lead_email}: {str(e)}")
        return False

async def send_lead_notification_to_team(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo para {form_data.email}")
        return True

    message = EmailMessage()
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = settings.EMAILS_FROM_EMAIL
    message["Subject"] = f"Nuevo Lead de HiphaMX: {form_data.nombre}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0;">
        <h2>Nuevo contacto desde la web HiphaMX</h2>
        <p><strong>Nombre:</strong> {form_data.nombre}</p>
        <p><strong>Email:</strong> {form_data.email}</p>
        <p><strong>Teléfono:</strong> {form_data.telefono}</p>
        <p><strong>Mensaje / Detalles:</strong></p>
        <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; line-height: 1.5;">
            {form_data.mensaje.replace('\n', '<br>')}
        </div>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    # Adjuntar PDF si es contrato
    if form_data.mensaje.startswith("ACEPTACIÓN DE CONTRATO VÍA WEB") and hasattr(form_data, 'firma') and form_data.firma:
        try:
            from email.mime.application import MIMEApplication
            pdf_bytes = generate_contract_pdf(form_data)
            pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"Contrato_Hipha_{form_data.nombre.replace(' ', '_')}.pdf")
            message.add_attachment(pdf_attachment.get_payload(decode=True), maintype='application', subtype='pdf', filename=f"Contrato_Hipha_{form_data.nombre.replace(' ', '_')}.pdf")
        except Exception as e:
            logger.error(f"Error al generar o adjuntar PDF en send_lead_notification_to_team: {e}")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        logger.info("Notificación de lead enviada al equipo")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación al equipo: {str(e)}")
        return False

async def send_newsletter_welcome(subscriber_email: str):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando bienvenida de newsletter a {subscriber_email}")
        return True

    message = EmailMessage()
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = subscriber_email
    message["Subject"] = "¡Bienvenido a los insights de HiphaMX!"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0;">
        <div style="background-color: #050810; padding: 30px; text-align: center;">
            <img src="https://hipha.mx/projects/HiphaMX/HiphaIdentidad/Logotipo/HiphaWhite.svg" alt="Hipha Logo" style="height: 40px; margin: 0 auto; display: block;">
        </div>
        <div style="padding: 20px;">
            <h2>¡Gracias por suscribirte!</h2>
            <p>A partir de ahora recibirás nuestros mejores insights y recursos sobre marketing y estrategia digital.</p>
            <br>
            <p>Atentamente,<br><strong>El equipo de Hipha</strong></p>
        </div>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar bienvenida de newsletter: {str(e)}")
        return False

async def send_newsletter_notification_to_team(subscriber_email: str):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        return True

    message = EmailMessage()
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = settings.EMAILS_FROM_EMAIL
    message["Subject"] = "Nueva Suscripción al Newsletter de HiphaMX"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Nuevo suscriptor al newsletter</h2>
        <p><strong>Email:</strong> {subscriber_email}</p>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación de newsletter al equipo: {str(e)}")
        return False

async def send_botica_order_customer(payer_name: str, payer_email: str, order_details: str, total: float):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a cliente {payer_email}")
        return True

    message = EmailMessage()
    message["From"] = f"Botica Silvestre <hola@botica-silvestre.com>"
    message["To"] = payer_email
    message["Subject"] = f"¡Tu ritual está en preparación, {payer_name}!"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #1A3636; background-color: #F4F6F5; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px;">
            <h2 style="color: #40534C; font-weight: normal;">Hola {payer_name},</h2>
            <p>Hemos recibido la solicitud de tu pedido. Si tu pago ya fue procesado, nuestro equipo comenzará a preparar tus adaptógenos de inmediato.</p>
            <h3 style="color: #40534C; border-bottom: 1px solid #E8F0EA; padding-bottom: 10px;">Resumen de tu pedido:</h3>
            <div style="background: #FCFDFD; padding: 15px; border-radius: 8px;">
                {{order_details}}
                <p><strong>Total (con envío si aplica): ${total} MXN</strong></p>
            </div>
            <p>Si tienes alguna duda o quieres enviarnos tu comprobante de pago, puedes responder a este correo (hola@botica-silvestre.com).</p>
            <br>
            <p style="color: #677D6A;">Con cariño,<br><strong>El equipo de Botica Silvestre</strong></p>
        </div>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo a cliente botica: {str(e)}")
        return False

async def send_botica_order_team(payer_name: str, payer_email: str, payer_phone: str, address_str: str, order_details: str, total: float):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo Botica")
        return True

    message = EmailMessage()
    message["From"] = f"Botica Silvestre (Web) <hola@botica-silvestre.com>"
    message["To"] = "hola@botica-silvestre.com"
    message["Subject"] = f"NUEVO PEDIDO WEB: {payer_name} - ${total} MXN"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>¡Nuevo pedido recibido en Botica Silvestre!</h2>
        <p>Asegúrate de confirmar el pago en Mercado Pago antes de enviar.</p>
        
        <h3>Datos del Cliente:</h3>
        <ul>
            <li><strong>Nombre:</strong> {payer_name}</li>
            <li><strong>Email:</strong> {payer_email}</li>
            <li><strong>Teléfono:</strong> {payer_phone}</li>
            <li><strong>Dirección:</strong> {address_str}</li>
        </ul>
        
        <h3>Detalles del Pedido:</h3>
        {{order_details}}
        <p><strong>Total: ${total} MXN</strong></p>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo al equipo botica: {str(e)}")
        return False


async def send_contract_followup_email(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP not configurado. Simulando envío para {form_data.email} (Contrato: {form_data.nombre})")
        return True

    message = EmailMessage()
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = form_data.email
    message["Subject"] = f"¡Firma de Contrato Exitosa! - Hipha"
    
    # We replace newlines in the message to `<br>` for correct HTML formatting
    mensaje_formatted = form_data.mensaje.replace("\n", "<br>")
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 0;">
        <div style="background-color: #050810; padding: 30px; text-align: center;">
            <img src="https://hipha.mx/projects/HiphaMX/HiphaIdentidad/Logotipo/HiphaWhite.svg" alt="Hipha Logo" style="height: 40px; margin: 0 auto; display: block;">
        </div>
        <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #06b6d4;">¡Firma de Contrato Confirmada, {form_data.nombre}!</h2>
            <p>Hemos recibido correctamente tu aceptación de los Términos y Condiciones para comenzar a trabajar juntos.</p>
            
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
                <h3 style="margin-top: 0; color: #0f172a;">Detalles del Acuerdo:</h3>
                <p style="margin-bottom: 5px;"><strong>Nombre Contacto:</strong> {form_data.nombre}</p>
                <p style="margin-bottom: 5px;"><strong>Email:</strong> {form_data.email}</p>
                <p style="margin-bottom: 15px;"><strong>Teléfono:</strong> {form_data.telefono}</p>
                <div style="border-top: 1px solid #cbd5e1; padding-top: 15px;">
                    <p>{mensaje_formatted}</p>
                </div>
            </div>
            
            <h3 style="color: #0f172a;">Copia de los Términos y Condiciones Aceptados:</h3>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0; font-size: 14px;">
                
        <h2>1. Naturaleza del Contrato y Autonomía</h2>
        <p>Hipha es un prestador de servicios profesionales independiente. El concepto “Tu departamento externo” es una denominación comercial y no constituye una sociedad mercantil, asociación ni relación de subordinación laboral. Hipha conserva plena autonomía técnica y administrativa. El personal de Hipha no está sujeto a la potestad de mando del Cliente, eliminando cualquier indicio de relación laboral bajo la Ley Federal del Trabajo.</p>

        <h2>2. Gestión de Proyecto y Comunicación</h2>
        <p>El Cliente designará un "Responsable de Proyecto" único con facultades suficientes para autorizar entregables y presupuestos. Las instrucciones de otros socios o terceros no serán vinculantes. La ventana de comunicación para reuniones virtuales es de lunes a viernes de 9:00 am a 12:00 pm (Hora Centro de México). Reuniones presenciales estarán sujetas a disponibilidad y podrán generar cargos adicionales por traslados y viáticos.</p>

        <h2>3. Procesamiento de Solicitudes y Terceros</h2>
        <p>Toda solicitud de diseño o estrategia requiere un plazo mínimo de 72 horas hábiles para inicio de gestión. Hipha no actúa como comisionista ni intermediario en pagos a terceros. Si el Cliente solicita que Hipha gestione archivos con proveedores externos (imprentas, medios, etc.), Hipha se deslinda de cualquier error en la ejecución, calidad, tiempos de entrega o vicios ocultos de dichos terceros. La ejecución física (recolecciones, instalaciones) es responsabilidad del personal interno del Cliente.</p>

        <h2>4. Responsabilidad y Seguridad del Cliente</h2>
        <p>La vigencia de los tiempos de entrega inicia tras la recepción total de los insumos (Brief, manuales, accesos). El retraso del Cliente no suspende la obligación de pago de las facturas o igualas pactadas. Respecto al Protocolo de Seguridad, el Cliente es responsable total de sus claves y accesos. Hipha se deslinda de hackeos, bloqueos o ataques derivados de acciones del Cliente o terceros ajenos a la agencia. Al finalizar la relación, el Cliente debe revocar accesos en un plazo máximo de 24 horas.</p>

        <h2>5. Propiedad Intelectual y Uso de Portafolio</h2>
        <p>La transferencia de derechos patrimoniales de los entregables finales (diseños publicados, sitios web, fotos de producto) ocurrirá únicamente tras la liquidación del 100% del pago. Hipha conserva la propiedad intelectual de sus metodologías, procesos internos, flujos de trabajo, estrategias preexistentes y archivos fuente (editables). Salvo existencia de un acuerdo de confidencialidad (NDA) explícito, el Cliente autoriza a Hipha a utilizar muestras del trabajo para su portafolio y redes sociales.</p>

        <h2>6. Rescisión y Suspensión de Servicio</h2>
        <p>Cualquier parte podrá dar por terminado el servicio con un aviso previo de 30 días naturales. En caso de impago, Hipha queda facultado para suspender total o parcialmente los servicios (pausar campañas, retirar servicios digitales) sin responsabilidad alguna por pérdidas económicas, daños o perjuicios que esta interrupción pudiera causar al Cliente.</p>

        <h2>7. Límite de Responsabilidad</h2>
        <p>La responsabilidad total de Hipha ante cualquier reclamación derivada de la prestación de los servicios, ya sea por negligencia, error u omisión, estará limitada como máximo al monto total pagado por el Cliente en el mes inmediato anterior a la fecha de la reclamación. Bajo ninguna circunstancia Hipha será responsable por lucro cesante o daños indirectos.</p>

        <h2>8. Cláusula de No Solicitud (Anti-Poaching)</h2>
        <p>El Cliente se compromete a no contratar, solicitar, ni emplear de manera directa o indirecta a ningún colaborador, empleado o consultor de Hipha durante la vigencia de este contrato y hasta por 12 meses posteriores a su terminación. El incumplimiento de esta cláusula generará una pena convencional equivalente a 12 meses de la iguala vigente al momento del incumplimiento.</p>

        <h2>9. Jurisdicción y Competencia</h2>
        <p>Para la interpretación y cumplimiento del presente, las partes se someten a las leyes comerciales de México y a la jurisdicción de los tribunales competentes en la ciudad de Guadalajara, Jalisco, renunciando expresamente a cualquier otro fuero que pudiera corresponderles por razón de sus domicilios presentes o futuros.</p>

            </div>
            
            <p>Adjunto a este correo encontrarás una copia de tu contrato en formato PDF con la firma y los datos ingresados.</p>
            <br>
            <p>Atentamente,<br><strong>El equipo de Hipha</strong></p>
        </div>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    # Adjuntar PDF
    try:
        from email.mime.application import MIMEApplication
        pdf_bytes = generate_contract_pdf(form_data)
        pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"Contrato_Hipha_{form_data.nombre.replace(' ', '_')}.pdf")
        message.add_attachment(pdf_attachment.get_payload(decode=True), maintype='application', subtype='pdf', filename=f"Contrato_Hipha_{form_data.nombre.replace(' ', '_')}.pdf")
    except Exception as e:
        logger.error(f"Error al generar o adjuntar PDF en send_contract_followup_email: {e}")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        logger.info(f"Correo de contrato enviado exitosamente a {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de contrato a {form_data.email}: {str(e)}")
        return False


async def send_healthyice_order_customer(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a cliente HealthyIce {form_data.email}")
        return True

    message = EmailMessage()
    message["From"] = f"HealthyIce <{settings.SMTP_USER}>"
    message.add_header('Reply-To', 'hola@healthyice.mx')
    message["To"] = form_data.email
    message["Subject"] = f"¡Hemos recibido tus datos, {form_data.nombre}!"
    
    html_content = f"""
    <html>
    <body style="font-family: 'Quicksand', Arial, sans-serif; color: #101729; background-color: #f8fafc; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px;">
            <h2 style="color: #101729; font-weight: bold;">Hola {form_data.nombre},</h2>
            <p>Hemos recibido tus datos correctamente. Muy pronto uno de nuestros asesores se pondrá en contacto contigo para darle seguimiento a tu pedido de paletas HealthyIce.</p>
            <p>Detalles que nos compartiste:</p>
            <ul>
                <li><strong>Teléfono:</strong> {form_data.telefono}</li>
                <li><strong>Mensaje:</strong> {form_data.mensaje}</li>
            </ul>
            <br>
            <p style="color: #98BC3C; font-weight: bold;">El equipo de HealthyIce</p>
        </div>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo a cliente HealthyIce: {str(e)}")
        return False

async def send_healthyice_order_team(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo HealthyIce")
        return True

    message = EmailMessage()
    message["From"] = f"HealthyIce Web <{settings.SMTP_USER}>"
    message.add_header('Reply-To', 'hola@healthyice.mx')
    message["To"] = "hola@healthyice.mx"
    message["Subject"] = f"NUEVO PROSPECTO WEB: {form_data.nombre}"
    
    mensaje_formatted = form_data.mensaje.replace('\n', '<br>')
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>¡Nuevo prospecto desde la landing de HealthyIce!</h2>
        
        <h3>Datos de Contacto:</h3>
        <ul>
            <li><strong>Nombre:</strong> {form_data.nombre}</li>
            <li><strong>Email:</strong> {form_data.email}</li>
            <li><strong>Teléfono:</strong> {form_data.telefono}</li>
        </ul>
        
        <h3>Mensaje Personalizado:</h3>
        <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; line-height: 1.5;">
            {mensaje_formatted}
        </div>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo al equipo HealthyIce: {str(e)}")
        return False
