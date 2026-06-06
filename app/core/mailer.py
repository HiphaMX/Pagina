import logging
import aiosmtplib
import tempfile
import base64
import os
from fpdf import FPDF
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
from app.core.config import settings

logger = logging.getLogger(__name__)

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
    pdf.cell(0, 8, text=f"Fecha de aceptacion: {getattr(form_data, 'fecha', '') or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Cliente / Contacto: {form_data.nombre}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Email: {form_data.email}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Telefono: {form_data.telefono}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Proyecto: {getattr(form_data, 'proyecto', '') or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Forma de Pago: {getattr(form_data, 'forma_pago', '') or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    clauses = [
        ("1. Naturaleza del servicio y Autonomia", "Hipha es un prestador de servicios profesionales independiente. El concepto “Tu departamento externo” es una denominacion comercial y no constituye una sociedad mercantil, asociacion ni relacion de subordinacion laboral. Hipha conserva plena autonomia tecnica y administrativa. El personal de Hipha no esta sujeto a la potestad de mando del Cliente, eliminando cualquier indicio de relacion laboral bajo la Ley Federal del Trabajo.\n\nEl cliente puede solicitar asesoria sobre algun tema de su interes, pero sera el quien en base a sus necesidades y experiencia direccione los esfuerzos de marketing y diseño, realizando las solicitudes que desde su vision como lider de su empresa puedan mejorar su desempeño comercial y posicionamiento. En ninguna circunstancia el equipo de Hipha esta habilitado para tomar decisiones respecto a la operacion y funcionamiento de la empresa del Cliente."),
        ("2. Gestion de Proyecto y Comunicacion", "El Cliente designara un 'Responsable de Proyecto' unico con facultades suficientes para autorizar entregables y presupuestos. Las instrucciones de otros socios o terceros no seran vinculantes. La ventana de comunicacion para reuniones virtuales es de lunes a viernes de 9:00 am a 12:00 pm (Hora Centro de Mexico). Reuniones presenciales estaran sujetas a disponibilidad y podran generar cargos adicionales por traslados y viaticos."),
        ("3. Procesamiento de Solicitudes y Terceros", "Toda solicitud de diseño o estrategia requiere un plazo minimo de 72 horas habiles para inicio de gestion. Hipha no actua como comisionista ni intermediario en pagos a terceros. Si el Cliente solicita que Hipha gestione archivos con proveedores externos (imprentas, medios, etc.), Hipha se deslinda de cualquier error en la ejecucion, calidad, tiempos de entrega o vicios ocultos de dichos terceros. La ejecucion fisica (recolecciones, instalaciones) es responsabilidad del personal interno del Cliente."),
        ("4. Responsabilidad y Seguridad del Cliente", "La vigencia de los tiempos de entrega inicia tras la recepcion total de los insumos (Brief, manuales, accesos). El retraso del Cliente no suspende la obligacion de pago de las facturas o igualas pactadas. Respecto al Protocolo de Seguridad, el Cliente es responsable total de sus claves y accesos. Hipha se deslinda de hackeos, bloqueos o ataques derivados de acciones del Cliente o terceros ajenos a la agencia. Al finalizar la relacion, el Cliente debe revocar accesos en un plazo maximo de 24 horas."),
        ("5. Propiedad Intelectual y Uso de Portafolio", "La transferencia de derechos patrimoniales de los entregables finales (diseños publicados, sitios web, fotos de producto) ocurrira unicamente tras la liquidacion del 100% del pago. Hipha conserva la propiedad intelectual de sus metodologias, procesos internos, flujos de trabajo, estrategias preexistentes y archivos fuente (editables). Salvo existencia de un acuerdo de confidencialidad (NDA) explicito, el Cliente autoriza a Hipha a utilizar muestras del trabajo para su portafolio y redes sociales."),
        ("6. Rescision y Suspension de Servicio", "Cualquier parte podra dar por terminado el servicio con un aviso previo de 30 dias naturales. En caso de impago, Hipha queda facultado para suspender total o parcialmente los servicios (pausar campañas, retirar servicios digitales) sin responsabilidad alguna por perdidas economicas, daños o perjuicios que esta interrupcion pudiera causar al Cliente."),
        ("7. Aprobacion de materiales", "Todo material de diseño o publicidad desarrollado por Hipha requerira la aprobacion expresa del Cliente antes de su produccion o envio a impresion. Una vez otorgada dicha aprobacion, el Cliente asume la total responsabilidad sobre el contenido, ortografia, dimensiones y especificaciones del material. Hipha queda exenta de cualquier responsabilidad economica o legal por errores, omisiones o negligencias detectadas con posterioridad a la aprobacion, asi como por costos de reimpresion, lucro cesante o daños indirectos."),
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
    
    # Check if we need to add a new page to avoid page break in the middle of signatures
    if pdf.get_y() > 220:
        pdf.add_page()
    
    y_before_sigs = pdf.get_y()
    
    # Cliente
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 8, text="El Cliente:", new_x="LMARGIN", new_y="NEXT", align="C")
    
    client_sig_path = None
    if hasattr(form_data, 'firma') and form_data.firma:
        try:
            if "," in form_data.firma:
                header, encoded = form_data.firma.split(",", 1)
                img_data = base64.b64decode(encoded)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(img_data)
                    client_sig_path = tmp.name
        except Exception as e:
            logger.error(f"Error procesando firma para PDF: {e}")
                
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
        
    return bytes(pdf.output())

async def send_lead_followup_email(lead_name: str, lead_email: str):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP not configurado. Simulando envío para {lead_email} (Lead: {lead_name})")
        return True

    message = EmailMessage()
    from_header = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>" if getattr(settings, 'EMAILS_FROM_NAME', '') else settings.EMAILS_FROM_EMAIL
    message["From"] = from_header
    message["To"] = lead_email
    message["Subject"] = f"¡Hola {lead_name}! Recibimos tu solicitud en HiphaMX"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="hipha.mx")
    
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
    from_header = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>" if getattr(settings, 'EMAILS_FROM_NAME', '') else settings.EMAILS_FROM_EMAIL
    message["From"] = from_header
    message["To"] = settings.EMAILS_FROM_EMAIL
    message["Subject"] = f"Nuevo Lead de HiphaMX: {form_data.nombre}"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="hipha.mx")
    
    mensaje_formatted = form_data.mensaje.replace('\n', '<br>') if form_data.mensaje else ''
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0;">
        <h2>Nuevo contacto desde la web HiphaMX</h2>
        <p><strong>Nombre:</strong> {form_data.nombre}</p>
        <p><strong>Email:</strong> {form_data.email}</p>
        <p><strong>Teléfono:</strong> {form_data.telefono}</p>
        <p><strong>Mensaje / Detalles:</strong></p>
        <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; line-height: 1.5;">
            {mensaje_formatted}
        </div>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    # Adjuntar PDF si es contrato
    if form_data.mensaje.startswith("ACEPTACIÓN DE CONTRATO VÍA WEB") and hasattr(form_data, 'firma') and form_data.firma:
        try:
            pdf_bytes = generate_contract_pdf(form_data)
            safe_name = form_data.nombre.replace(' ', '_')
            message.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=f"Contrato_Hipha_{safe_name}.pdf")
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
    # Asegurar que el From no tenga espacios vacíos extra que disparen filtros de SPAM
    from_header = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>" if getattr(settings, 'EMAILS_FROM_NAME', '') else settings.EMAILS_FROM_EMAIL
    message["From"] = from_header
    message["To"] = form_data.email
    message["Subject"] = "¡Bienvenido a Hipha!"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="hipha.mx")
    
    # We replace newlines in the message to `<br>` for correct HTML formatting
    mensaje_formatted = form_data.mensaje.replace("\n", "<br>")
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 0;">
        <div style="background-color: #050810; padding: 30px; text-align: center;">
            <img src="https://hipha.mx/projects/HiphaMX/HiphaIdentidad/Logotipo/HiphaWhite.svg" alt="Hipha Logo" style="height: 40px; margin: 0 auto; display: block;">
        </div>
        <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #06b6d4;">¡Firma de contrato de servicios confirmada!</h2>
            <p>Hemos recibido correctamente tu contrato, esto indica que aceptas los Términos y Condiciones para comenzar a trabajar juntos y convertirnos en una extensión de tu empresa.</p>
            
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
                <h3 style="margin-top: 0; color: #0f172a;">Detalles generales:</h3>
                <p style="margin-bottom: 5px;"><strong>Nombre Contacto:</strong> {form_data.nombre}</p>
                <p style="margin-bottom: 5px;"><strong>Email:</strong> {form_data.email}</p>
                <p style="margin-bottom: 15px;"><strong>Teléfono:</strong> {form_data.telefono}</p>
                <div style="border-top: 1px solid #cbd5e1; padding-top: 15px;">
                    <p>{mensaje_formatted}</p>
                </div>
            </div>
            
            <p>Adjunto a este correo encontrarás una copia de tu contrato en formato PDF, agradecemos la confianza depositada en nuestro proyecto y estamos seguros que esta sinergia potenciará el tuyo.</p>
            <br>
            <p>Atentamente,<br><strong>Frank D.</strong><br>El equipo de Hipha</p>
        </div>
    </body>
    </html>
    """
    message.set_content(html_content, subtype="html")
    
    # Adjuntar PDF
    try:
        pdf_bytes = generate_contract_pdf(form_data)
        safe_name = form_data.nombre.replace(' ', '_')
        message.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=f"Contrato_Hipha_{safe_name}.pdf")
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


async def send_whiteclean_confirmation_email(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a prospecto WhiteClean {form_data.email}")
        return True

    message = EmailMessage()
    message["From"] = "WhiteClean Limpieza Especializada <clientes@whiteclean.com.mx>"
    message["To"] = form_data.email
    message.add_header('Reply-To', 'clientes@whiteclean.com.mx')
    message["Subject"] = f"¡Hemos recibido tu solicitud, {form_data.nombre}! ✨"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="whiteclean.com.mx")

    mensaje_formatted = form_data.mensaje.replace('\n', '<br>') if form_data.mensaje else 'Sin mensaje adicional'

    html_content = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; background-color: #f8fafc; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
            
            <!-- Header con la identidad de WhiteClean -->
            <div style="background-color: #0F3D64; padding: 30px 20px; text-align: center; border-bottom: 4px solid #00E5FF;">
                <img src="https://whiteclean.com.mx/assets/612eb73096523eec44fda754_WhiteCleanW.svg" alt="WhiteClean" style="height: 48px; max-height: 48px; border: 0; display: block; margin: 0 auto;">
            </div>
            
            <!-- Cuerpo del Correo -->
            <div style="padding: 40px 30px;">
                <h2 style="color: #0F3D64; font-size: 22px; font-weight: 700; margin-top: 0; margin-bottom: 20px;">¡Hola, {form_data.nombre}! 👋</h2>
                <p style="font-size: 16px; line-height: 1.6; color: #475569; margin-bottom: 25px;">
                    Agradecemos mucho tu interés en nuestros servicios. Hemos recibido correctamente tus datos desde nuestro sitio web y un asesor experto se pondrá en contacto contigo en breve para brindarte una cotización detallada y adaptada a tus necesidades.
                </p>
                
                <!-- Tarjeta con resumen de solicitud -->
                <div style="background-color: #f0f7ff; border-left: 4px solid #00E5FF; padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 30px;">
                    <h3 style="color: #0F3D64; font-size: 15px; font-weight: 700; margin-top: 0; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Resumen de tu solicitud:</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px; line-height: 1.5;">
                        <tr>
                            <td style="padding: 4px 0; color: #64748b; width: 120px; font-weight: 600;">Servicio:</td>
                            <td style="padding: 4px 0; color: #1e293b; font-weight: bold;">{form_data.servicio}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 0; color: #64748b; font-weight: 600;">Ubicación:</td>
                            <td style="padding: 4px 0; color: #1e293b;">{form_data.ubicacion}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 0; color: #64748b; font-weight: 600;">Teléfono:</td>
                            <td style="padding: 4px 0; color: #1e293b;">{form_data.telefono}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 0; color: #64748b; font-weight: 600; vertical-align: top;">Mensaje:</td>
                            <td style="padding: 4px 0; color: #1e293b; font-style: italic;">{mensaje_formatted}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; color: #475569; margin-bottom: 0;">
                    Con más de 20 años de experiencia, en WhiteClean garantizamos procesos certificados con equipos profesionales y productos especializados para que disfrutes de espacios limpios, sanos e impecables.
                </p>
            </div>
            
            <!-- Footer del Correo -->
            <div style="background-color: #f8fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8;">
                <p style="margin: 0 0 10px 0;">Este es un aviso automático de confirmación de contacto.</p>
                <p style="margin: 0 0 15px 0;"><strong>WhiteClean Limpieza Especializada</strong></p>
                <div style="margin-bottom: 0;">
                    <a href="https://whiteclean.com.mx" style="color: #0F3D64; text-decoration: none; font-weight: bold; margin: 0 10px;">Sitio Web</a>
                    <span style="color: #cbd5e1;">|</span>
                    <a href="mailto:clientes@whiteclean.com.mx" style="color: #0F3D64; text-decoration: none; font-weight: bold; margin: 0 10px;">Contacto</a>
                </div>
            </div>
            
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
        logger.info(f"Correo de confirmación WhiteClean enviado exitosamente a {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de confirmación WhiteClean a {form_data.email}: {str(e)}")
        return False


async def send_whiteclean_notification_team(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo WhiteClean")
        return True

    message = EmailMessage()
    message["From"] = "WhiteClean Web <clientes@whiteclean.com.mx>"
    message["To"] = "clientes@whiteclean.com.mx, whiteclean1@hotmail.com"
    message.add_header('Reply-To', form_data.email)
    message["Subject"] = f"🚨 NUEVA SOLICITUD WEB: {form_data.nombre} {form_data.apellido} - {form_data.servicio}"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="whiteclean.com.mx")

    mensaje_formatted = form_data.mensaje.replace('\n', '<br>') if form_data.mensaje else 'Ninguno'

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333333; background-color: #f1f5f9; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #cbd5e1;">
            
            <div style="background-color: #0F3D64; padding: 20px; text-align: center; color: white;">
                <h2 style="margin: 0; font-size: 20px;">🚨 ¡Nuevo Prospecto Recibido!</h2>
                <p style="margin: 5px 0 0 0; font-size: 13px; color: #00E5FF; font-weight: bold;">WhiteClean Landing Page</p>
            </div>
            
            <div style="padding: 25px;">
                <p style="margin-top: 0; font-size: 15px; color: #475569;">Un usuario ha enviado una solicitud de cotización desde la web. A continuación los detalles:</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0F3D64; width: 150px; background-color: #f8fafc;">Nombre Completo:</td>
                        <td style="padding: 10px; color: #1e293b;">{form_data.nombre} {form_data.apellido}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0F3D64; background-color: #f8fafc;">Email:</td>
                        <td style="padding: 10px; color: #1e293b;"><a href="mailto:{form_data.email}" style="color: #00E5FF; font-weight: bold; text-decoration: none;">{form_data.email}</a></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0F3D64; background-color: #f8fafc;">Teléfono / Celular:</td>
                        <td style="padding: 10px; color: #1e293b;"><a href="tel:{form_data.telefono}" style="color: #0F3D64; font-weight: bold; text-decoration: none;">{form_data.telefono}</a></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0F3D64; background-color: #f8fafc;">Servicio Requerido:</td>
                        <td style="padding: 10px; color: #1e293b; font-weight: bold;">{form_data.servicio}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0F3D64; background-color: #f8fafc;">Ubicación / Municipio:</td>
                        <td style="padding: 10px; color: #1e293b;">{form_data.ubicacion}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold; color: #0F3D64; background-color: #f8fafc; vertical-align: top;">Mensaje:</td>
                        <td style="padding: 10px; color: #1e293b; line-height: 1.5; font-style: italic;">{mensaje_formatted}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 30px; text-align: center;">
                    <a href="https://wa.me/{form_data.telefono.replace(' ', '').replace('+', '')}" style="background-color: #25D366; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-block;">
                        💬 Contactar por WhatsApp
                    </a>
                </div>
            </div>
            
            <div style="background-color: #f8fafc; padding: 15px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #cbd5e1;">
                Mensaje generado de forma automática por el sistema de WhiteClean.
            </div>
            
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
        logger.info("Notificación de lead WhiteClean enviada con éxito al equipo y socio.")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación WhiteClean al equipo: {str(e)}")
        return False


async def send_chilechillon_confirmation_email(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a prospecto Chile Chillón {form_data.email}")
        return True

    message = EmailMessage()
    message["From"] = "Chile Chillón <hola@elchilechillon.com.mx>"
    message["To"] = form_data.email
    message.add_header('Reply-To', 'hola@elchilechillon.com.mx')
    message["Subject"] = f"¡Tu sazón está a punto de potenciarse, {form_data.nombre}! 🌶️🔥"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="elchilechillon.com.mx")

    mensaje_formatted = form_data.mensaje.replace('\n', '<br>') if form_data.mensaje else 'Sin comentarios adicionales'
    
    perfil_map = {
        "usuario_final": "Usuario Final (Recetas y Promociones)",
        "restaurante": "Restaurante (Muestras y Precios Especiales)",
        "distribuidor": "Distribuidor (Incorporar al Catálogo)"
    }
    perfil_text = perfil_map.get(form_data.perfil, form_data.perfil)

    html_content = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9; background-color: #080505; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #0d0707; border-radius: 24px; overflow: hidden; box-shadow: 0 10px 30px rgba(229, 9, 20, 0.1); border: 1px solid rgba(229, 9, 20, 0.2);">
            
            <!-- Header con la identidad de Chile Chillón -->
            <div style="background-color: #080505; padding: 35px 20px; text-align: center; border-bottom: 4px solid #E50914;">
                <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 900; letter-spacing: 2px;">CHILE <span style="color: #E50914;">CHILLÓN</span></h1>
                <p style="color: #FF6A00; margin: 5px 0 0 0; font-size: 11px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase;">Tu sazón en su máxima potencia</p>
            </div>
            
            <!-- Cuerpo del Correo -->
            <div style="padding: 40px 30px;">
                <h2 style="color: #ffffff; font-size: 22px; font-weight: 700; margin-top: 0; margin-bottom: 20px;">¡Hola, {form_data.nombre}! 👋</h2>
                <p style="font-size: 16px; line-height: 1.6; color: #cbd5e1; margin-bottom: 25px;">
                    ¡Bienvenido al Club de la Flama! Hemos recibido correctamente tus datos desde nuestra landing page. Nuestro alquimista de sabor está revisando tu solicitud para ayudarte a elevar cada comida y botana de forma fácil y sin complicaciones.
                </p>
                
                <!-- Tarjeta con resumen de solicitud -->
                <div style="background-color: rgba(229, 9, 20, 0.05); border-left: 4px solid #E50914; padding: 25px; border-radius: 0 16px 16px 0; margin-bottom: 30px; border-top: 1px solid rgba(229, 9, 20, 0.1); border-right: 1px solid rgba(229, 9, 20, 0.1); border-bottom: 1px solid rgba(229, 9, 20, 0.1);">
                    <h3 style="color: #FF6A00; font-size: 14px; font-weight: 800; margin-top: 0; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px;">Detalles de tu registro:</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px; line-height: 1.6; color: #e2e8f0;">
                        <tr>
                          <td style="padding: 6px 0; color: #94a3b8; width: 120px; font-weight: 600;">Perfil:</td>
                          <td style="padding: 6px 0; color: #ffffff; font-weight: bold;">{perfil_text}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #94a3b8; font-weight: 600;">WhatsApp / Cel:</td>
                            <td style="padding: 6px 0; color: #ffffff;">{form_data.telefono}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #94a3b8; font-weight: 600; vertical-align: top;">Comentarios:</td>
                            <td style="padding: 6px 0; color: #cbd5e1; font-style: italic;">{mensaje_formatted}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; color: #94a3b8; margin-bottom: 0;">
                    En Chile Chillón elaboramos picante premium con fórmulas minuciosamente balanceadas y 100% naturales, asegurando la consistencia exacta en cada lote desde hace 10 años. ¡Prepárate para experimentar el sazón definitivo!
                </p>
            </div>
            
            <!-- Footer del Correo -->
            <div style="background-color: #080505; padding: 30px; text-align: center; border-top: 1px solid rgba(255,255,255,0.05); font-size: 12px; color: #64748b;">
                <p style="margin: 0 0 10px 0;">Este es un aviso automático de confirmación de registro.</p>
                <p style="margin: 0 0 15px 0;"><strong>Chile Chillón &middot; Salsas & Picantes Premium</strong></p>
                <div style="margin-bottom: 0;">
                    <a href="https://www.elchilechillon.com.mx" style="color: #FF6A00; text-decoration: none; font-weight: bold; margin: 0 10px;">Sitio Web</a>
                    <span style="color: rgba(255,255,255,0.1);">|</span>
                    <a href="mailto:hola@elchilechillon.com.mx" style="color: #E50914; text-decoration: none; font-weight: bold; margin: 0 10px;">Contacto</a>
                </div>
            </div>
            
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
        logger.info(f"Correo de confirmación Chile Chillón enviado con éxito a {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de confirmación Chile Chillón a {form_data.email}: {str(e)}")
        return False


async def send_chilechillon_notification_team(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío de notificación de Chile Chillón al equipo")
        return True

    message = EmailMessage()
    message["From"] = "Chile Chillón Web <hola@elchilechillon.com.mx>"
    message["To"] = settings.EMAILS_FROM_EMAIL
    message.add_header('Reply-To', form_data.email)
    message["Subject"] = f"🌶️ NUEVA SOLICITUD WEB CHILE CHILLÓN: {form_data.nombre} - {form_data.perfil.upper()}"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="elchilechillon.com.mx")

    mensaje_formatted = form_data.mensaje.replace('\n', '<br>') if form_data.mensaje else 'Ninguno'
    
    perfil_map = {
        "usuario_final": "Usuario Final (Recetas y Promociones)",
        "restaurante": "Restaurante (Muestras y Precios Especiales)",
        "distribuidor": "Distribuidor (Incorporar al Catálogo)"
    }
    perfil_text = perfil_map.get(form_data.perfil, form_data.perfil)

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333333; background-color: #f1f5f9; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #cbd5e1;">
            
            <div style="background-color: #080505; padding: 20px; text-align: center; color: white; border-bottom: 4px solid #E50914;">
                <h2 style="margin: 0; font-size: 20px; color: #ffffff;">🌶️ ¡Nuevo Prospecto Chile Chillón!</h2>
                <p style="margin: 5px 0 0 0; font-size: 13px; color: #FF6A00; font-weight: bold;">Ecosistema Web</p>
            </div>
            
            <div style="padding: 25px;">
                <p style="margin-top: 0; font-size: 15px; color: #475569;">Se ha registrado un usuario en la landing de Chile Chillón con los siguientes detalles:</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #080505; width: 150px; background-color: #f8fafc;">Nombre:</td>
                        <td style="padding: 10px; color: #1e293b;">{form_data.nombre}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #080505; background-color: #f8fafc;">Email:</td>
                        <td style="padding: 10px; color: #1e293b;"><a href="mailto:{form_data.email}" style="color: #E50914; font-weight: bold; text-decoration: none;">{form_data.email}</a></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #080505; background-color: #f8fafc;">WhatsApp / Celular:</td>
                        <td style="padding: 10px; color: #1e293b;"><a href="tel:{form_data.telefono}" style="color: #080505; font-weight: bold; text-decoration: none;">{form_data.telefono}</a></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #080505; background-color: #f8fafc;">Perfil:</td>
                        <td style="padding: 10px; color: #1e293b; font-weight: bold;">{perfil_text}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold; color: #080505; background-color: #f8fafc; vertical-align: top;">Comentarios:</td>
                        <td style="padding: 10px; color: #1e293b; line-height: 1.5; font-style: italic;">{mensaje_formatted}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 30px; text-align: center;">
                    <a href="https://wa.me/{form_data.telefono.replace(' ', '').replace('+', '')}" style="background-color: #25D366; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-block;">
                        💬 Contactar por WhatsApp
                    </a>
                </div>
            </div>
            
            <div style="background-color: #f8fafc; padding: 15px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #cbd5e1;">
                Mensaje generado de forma automática por el sistema de Chile Chillón.
            </div>
            
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
        logger.info("Notificación de lead Chile Chillón enviada con éxito al equipo.")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación de Chile Chillón al equipo: {str(e)}")
        return False


async def send_grupogari_confirmation_email(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a prospecto Grupo Gari {form_data.email}")
        return True

    message = EmailMessage()
    message["From"] = "Grupo Gari | Cumplimiento Regulatorio <contacto@grupogari.com>"
    message["To"] = form_data.email
    message.add_header('Reply-To', 'contacto@grupogari.com')
    message["Subject"] = f"Autodiagnóstico Recibido - Registro GARI-{form_data.nombre.upper()} 📄"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="grupogari.com")

    mensaje_formatted = form_data.mensaje.replace('\n', '<br>') if form_data.mensaje else 'Sin detalles adicionales'
    rol_text = "Recursos Humanos & Capacitación" if form_data.rol == "hr" else "Dueño de Empresa / Operativo"

    html_content = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; background-color: #f8fafc; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
            
            <!-- Header Técnico Estilo Blueprint -->
            <div style="background-color: #0A0D14; padding: 30px 20px; text-align: center; border-bottom: 4px solid #FF9F1C;">
                <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 2px;">GRUPO <span style="color: #FF9F1C;">GARI</span></h1>
                <p style="color: #64748B; margin: 5px 0 0 0; font-size: 11px; font-family: monospace; letter-spacing: 1px; text-transform: uppercase;">[REGULACIÓN · HIGIENE · SEGURIDAD]</p>
            </div>
            
            <!-- Cuerpo del Correo -->
            <div style="padding: 40px 30px;">
                <h2 style="color: #0A0D14; font-size: 20px; font-weight: 700; margin-top: 0; margin-bottom: 20px;">Estimado(a) {form_data.nombre},</h2>
                <p style="font-size: 15px; line-height: 1.6; color: #475569; margin-bottom: 25px;">
                    Confirmamos la recepción de las variables operativas de su empresa para el proceso de autodiagnóstico preliminar de cumplimiento industrial. Nuestro departamento de ingeniería regulatoria está analizando la información suministrada para emitir su matriz de soluciones técnicas modulares.
                </p>
                
                <!-- Resumen de Variables Capturadas -->
                <div style="background-color: #f8fafc; border-left: 4px solid #FF9F1C; padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 30px; border: 1px solid #e2e8f0; border-left-width: 4px;">
                    <h3 style="color: #0A0D14; font-size: 14px; font-weight: 700; margin-top: 0; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Variables de Diagnóstico Registradas:</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px; line-height: 1.5; font-family: sans-serif;">
                        <tr>
                            <td style="padding: 4px 0; color: #64748b; width: 140px; font-weight: 600;">Posición B2B:</td>
                            <td style="padding: 4px 0; color: #1e293b; font-weight: bold;">{rol_text}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 0; color: #64748b; font-weight: 600;">Industria:</td>
                            <td style="padding: 4px 0; color: #1e293b; text-transform: uppercase;">{form_data.industria}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 0; color: #64748b; font-weight: 600;">Volumen de Personal:</td>
                            <td style="padding: 4px 0; color: #1e293b;">{form_data.empleados} colaboradores</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 0; color: #64748b; font-weight: 600;">Servicio Requerido:</td>
                            <td style="padding: 4px 0; color: #1e293b; font-weight: bold;">{form_data.servicio}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 0; color: #64748b; font-weight: 600; vertical-align: top;">Requerimientos:</td>
                            <td style="padding: 4px 0; color: #1e293b; font-style: italic;">{mensaje_formatted}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="font-size: 14px; line-height: 1.6; color: #475569; margin-bottom: 0;">
                    Nuestro equipo técnico se comunicará en un plazo máximo de 24 horas hábiles para presentar la propuesta económica de cumplimiento y agendamiento preventivo de firmas autorizadas ante Protección Civil y la STPS.
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8;">
                <p style="margin: 0 0 10px 0;">Este es un aviso procedimental automatizado de Grupo Gari.</p>
                <p style="margin: 0 0 15px 0;"><strong>Grupo Gari | Consultoría de Cumplimiento Regulatorio</strong></p>
                <div style="margin-bottom: 0;">
                    <a href="https://wa.me/523300000000" style="color: #FF9F1C; text-decoration: none; font-weight: bold;">Canal Directo de WhatsApp</a>
                </div>
            </div>
            
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
        logger.info(f"Correo de confirmación Grupo Gari enviado exitosamente a {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de confirmación Grupo Gari a {form_data.email}: {str(e)}")
        return False


async def send_grupogari_notification_team(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo Grupo Gari")
        return True

    message = EmailMessage()
    message["From"] = "Grupo Gari Web <contacto@grupogari.com>"
    message["To"] = settings.EMAILS_FROM_EMAIL
    message.add_header('Reply-To', form_data.email)
    message["Subject"] = f"🚨 NUEVO DIAGNÓSTICO WEB GARI: {form_data.nombre.upper()} - {form_data.servicio.upper()}"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="grupogari.com")

    mensaje_formatted = form_data.mensaje.replace('\n', '<br>') if form_data.mensaje else 'Ninguno'
    rol_text = "Recursos Humanos & Capacitación" if form_data.rol == "hr" else "Dueño de Empresa / Operativo"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333333; background-color: #f1f5f9; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #cbd5e1;">
            
            <div style="background-color: #0A0D14; padding: 20px; text-align: center; color: white; border-bottom: 4px solid #FF9F1C;">
                <h2 style="margin: 0; font-size: 18px; color: #ffffff;">🚨 NUEVA SOLICITUD DE DIAGNÓSTICO</h2>
                <p style="margin: 5px 0 0 0; font-size: 11px; color: #FF9F1C; font-weight: bold; font-family: monospace;">[Ecosistema Grupo Gari]</p>
            </div>
            
            <div style="padding: 25px;">
                <p style="margin-top: 0; font-size: 14px; color: #475569;">Se han capturado las siguientes variables desde la plataforma de autodiagnóstico:</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0D14; width: 160px; background-color: #f8fafc; font-size: 13px;">Prospecto:</td>
                        <td style="padding: 10px; color: #1e293b; font-size: 13px;">{form_data.nombre} {form_data.apellido}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0D14; background-color: #f8fafc; font-size: 13px;">Email Corporativo:</td>
                        <td style="padding: 10px; color: #1e293b; font-size: 13px;"><a href="mailto:{form_data.email}" style="color: #FF9F1C; font-weight: bold; text-decoration: none;">{form_data.email}</a></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0D14; background-color: #f8fafc; font-size: 13px;">Teléfono / WhatsApp:</td>
                        <td style="padding: 10px; color: #1e293b; font-size: 13px;"><a href="tel:{form_data.telefono}" style="color: #0A0D14; font-weight: bold; text-decoration: none;">{form_data.telefono}</a></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0D14; background-color: #f8fafc; font-size: 13px;">Rol B2B:</td>
                        <td style="padding: 10px; color: #1e293b; font-size: 13px;">{rol_text}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0D14; background-color: #f8fafc; font-size: 13px;">Colaboradores:</td>
                        <td style="padding: 10px; color: #1e293b; font-size: 13px;">{form_data.empleados} empleados</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0D14; background-color: #f8fafc; font-size: 13px;">Giro de Industria:</td>
                        <td style="padding: 10px; color: #1e293b; text-transform: uppercase; font-size: 13px;">{form_data.industria}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0D14; background-color: #f8fafc; font-size: 13px;">Servicio Requerido:</td>
                        <td style="padding: 10px; color: #1e293b; font-weight: bold; font-size: 13px;">{form_data.servicio}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold; color: #0A0D14; background-color: #f8fafc; vertical-align: top; font-size: 13px;">Detalles:</td>
                        <td style="padding: 10px; color: #1e293b; line-height: 1.5; font-style: italic; font-size: 13px;">{mensaje_formatted}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 30px; text-align: center;">
                    <a href="https://wa.me/{form_data.telefono.replace(' ', '').replace('+', '')}" style="background-color: #25D366; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-block;">
                        💬 Contactar por WhatsApp de Inmediato
                    </a>
                </div>
            </div>
            
            <div style="background-color: #f8fafc; padding: 15px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #cbd5e1;">
                Mensaje generado de forma automática por el sistema de Grupo Gari.
            </div>
            
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
        logger.info("Notificación de lead Grupo Gari enviada con éxito al equipo.")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación de Grupo Gari al equipo: {str(e)}")
        return False


