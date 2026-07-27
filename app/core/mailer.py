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

async def _send_smtp(message, smtp_host=None, smtp_port=None, smtp_user=None, smtp_password=None):
    host = smtp_host or settings.SMTP_HOST
    port = smtp_port or settings.SMTP_PORT
    user = smtp_user or settings.SMTP_USER
    password = smtp_password or settings.SMTP_PASSWORD

    use_tls = (port == 465)
    start_tls = (port != 465)
    await aiosmtplib.send(
        message,
        hostname=host,
        port=port,
        username=user,
        password=password,
        use_tls=use_tls,
        start_tls=start_tls,
        timeout=5.0
    )


def format_spanish_date(date_str: str) -> str:
    if not date_str:
        return 'N/A'
    try:
        parts = date_str.split('-')
        if len(parts) == 3 and len(parts[0]) == 4:
            year, month, day = parts
            months = {
                '01': 'enero', '02': 'febrero', '03': 'marzo', '04': 'abril',
                '05': 'mayo', '06': 'junio', '07': 'julio', '08': 'agosto',
                '09': 'septiembre', '10': 'octubre', '11': 'noviembre', '12': 'diciembre'
            }
            day_num = int(day)
            month_name = months.get(month, month)
            return f"{day_num} de {month_name} de {year}"
    except Exception:
        pass
    return date_str

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
    fecha_acuerdo = format_spanish_date(getattr(form_data, 'fecha', '') or 'N/A')
    pdf.cell(0, 8, text=f"Fecha de aceptacion: {fecha_acuerdo}", new_x="LMARGIN", new_y="NEXT")
    dia_pago = getattr(form_data, 'fecha_pago', '')
    dia_pago_formatted = f"{dia_pago} (de cada mes)" if dia_pago else 'N/A'
    pdf.cell(0, 8, text=f"Dia de pago: {dia_pago_formatted}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Cliente / Contacto: {form_data.nombre}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Email: {form_data.email}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Telefono: {form_data.telefono}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Proyecto: {getattr(form_data, 'proyecto', '') or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Plan contratado: {getattr(form_data, 'plan_contratado', '') or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
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

    from_email = settings.EMAILS_FROM_EMAIL if settings.EMAILS_FROM_EMAIL else "hola@hipha.mx"
    from_name = settings.EMAILS_FROM_NAME if settings.EMAILS_FROM_NAME else "HiphaMX"
    
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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HIPHA",
        from_name=from_name,
        from_email=from_email,
        to_email=lead_email,
        subject=f"¡Hola {lead_name}! Recibimos tu solicitud en HiphaMX",
        html_content=html_content,
        domain="hipha.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Correo enviado exitosamente a {lead_email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo a {lead_email}: {str(e)}")
        return False

async def send_lead_notification_to_team(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo para {form_data.email}")
        return True

    from_email = settings.EMAILS_FROM_EMAIL if settings.EMAILS_FROM_EMAIL else "hola@hipha.mx"
    from_name = settings.EMAILS_FROM_NAME if settings.EMAILS_FROM_NAME else "HiphaMX"
    
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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HIPHA",
        from_name=from_name,
        from_email=from_email,
        to_email=settings.EMAILS_FROM_EMAIL,
        subject=f"Nuevo Lead de HiphaMX: {form_data.nombre}",
        html_content=html_content,
        domain="hipha.mx"
    )
    del message['Reply-To']
    message['Reply-To'] = form_data.email
    
    # Adjuntar PDF si es contrato
    if form_data.mensaje.startswith("ACEPTACIÓN DE CONTRATO VÍA WEB") and hasattr(form_data, 'firma') and form_data.firma:
        try:
            pdf_bytes = generate_contract_pdf(form_data)
            safe_name = form_data.nombre.replace(' ', '_')
            message.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=f"Contrato_Hipha_{safe_name}.pdf")
        except Exception as e:
            logger.error(f"Error al generar o adjuntar PDF en send_lead_notification_to_team: {e}")
    
    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info("Notificación de lead enviada al equipo")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación al equipo: {str(e)}")
        return False

async def send_newsletter_welcome(subscriber_email: str):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP no configurado. Simulando bienvenida de newsletter a {subscriber_email}")
        return True

    from_email = settings.EMAILS_FROM_EMAIL if settings.EMAILS_FROM_EMAIL else "hola@hipha.mx"
    from_name = settings.EMAILS_FROM_NAME if settings.EMAILS_FROM_NAME else "HiphaMX"
    
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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HIPHA",
        from_name=from_name,
        from_email=from_email,
        to_email=subscriber_email,
        subject="¡Bienvenido a los insights de HiphaMX!",
        html_content=html_content,
        domain="hipha.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar bienvenida de newsletter: {str(e)}")
        return False

async def send_newsletter_notification_to_team(subscriber_email: str):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        return True

    from_email = settings.EMAILS_FROM_EMAIL if settings.EMAILS_FROM_EMAIL else "hola@hipha.mx"
    from_name = settings.EMAILS_FROM_NAME if settings.EMAILS_FROM_NAME else "HiphaMX"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Nuevo suscriptor al newsletter</h2>
        <p><strong>Email:</strong> {subscriber_email}</p>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HIPHA",
        from_name=from_name,
        from_email=from_email,
        to_email=settings.EMAILS_FROM_EMAIL,
        subject="Nueva Suscripción al Newsletter de HiphaMX",
        html_content=html_content,
        domain="hipha.mx"
    )
    del message['Reply-To']
    message['Reply-To'] = subscriber_email

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación de newsletter al equipo: {str(e)}")
        return False

async def send_botica_order_customer(payer_name: str, payer_email: str, order_details: str, total: float):
    botica_configured = bool(settings.BOTICA_SMTP_HOST and settings.BOTICA_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not botica_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a cliente {payer_email}")
        return True

    from_email = settings.BOTICA_EMAILS_FROM_EMAIL if settings.BOTICA_EMAILS_FROM_EMAIL else "hola@botica-silvestre.com"
    from_name = settings.BOTICA_EMAILS_FROM_NAME if settings.BOTICA_EMAILS_FROM_NAME else "Botica Silvestre"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #1A3636; background-color: #F4F6F5; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px;">
            <h2 style="color: #40534C; font-weight: normal;">Hola {payer_name},</h2>
            <p>Hemos recibido la solicitud de tu pedido. Si tu pago ya fue procesado, nuestro equipo comenzará a preparar tus adaptógenos de inmediato.</p>
            <h3 style="color: #40534C; border-bottom: 1px solid #E8F0EA; padding-bottom: 10px;">Resumen de tu pedido:</h3>
            <div style="background: #FCFDFD; padding: 15px; border-radius: 8px;">
                {order_details}
                <p><strong>Total (con envío si aplica): ${total} MXN</strong></p>
            </div>
            <p>Si tienes alguna duda o quieres enviarnos tu comprobante de pago, puedes responder a este correo (hola@botica-silvestre.com).</p>
            <br>
            <p style="color: #677D6A;">Con cariño,<br><strong>El equipo de Botica Silvestre</strong></p>
        </div>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="BOTICA",
        from_name=from_name,
        from_email=from_email,
        to_email=payer_email,
        subject=f"¡Tu ritual está en preparación, {payer_name}!",
        html_content=html_content,
        domain="botica-silvestre.com"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo a cliente botica: {str(e)}")
        return False

async def send_botica_order_team(payer_name: str, payer_email: str, payer_phone: str, address_str: str, order_details: str, total: float):
    botica_configured = bool(settings.BOTICA_SMTP_HOST and settings.BOTICA_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not botica_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo Botica")
        return True

    from_email = settings.BOTICA_EMAILS_FROM_EMAIL if settings.BOTICA_EMAILS_FROM_EMAIL else "hola@botica-silvestre.com"
    to_email = settings.BOTICA_EMAILS_FROM_EMAIL if settings.BOTICA_EMAILS_FROM_EMAIL else "hola@botica-silvestre.com"
    
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
        {order_details}
        <p><strong>Total: ${total} MXN</strong></p>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="BOTICA",
        from_name="Botica Silvestre (Web)",
        from_email=from_email,
        to_email=to_email,
        subject=f"NUEVO PEDIDO WEB: {payer_name} - ${total} MXN",
        html_content=html_content,
        domain="botica-silvestre.com"
    )
    del message['Reply-To']
    message['Reply-To'] = payer_email

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo al equipo botica: {str(e)}")
        return False


async def send_contract_followup_email(form_data):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"SMTP not configurado. Simulando envío para {form_data.email} (Contrato: {form_data.nombre})")
        return True

    from_email = settings.EMAILS_FROM_EMAIL if settings.EMAILS_FROM_EMAIL else "hola@hipha.mx"
    from_name = settings.EMAILS_FROM_NAME if settings.EMAILS_FROM_NAME else "HiphaMX"
    
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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HIPHA",
        from_name=from_name,
        from_email=from_email,
        to_email=form_data.email,
        subject="¡Bienvenido a Hipha!",
        html_content=html_content,
        domain="hipha.mx"
    )

    # Adjuntar PDF
    try:
        pdf_bytes = generate_contract_pdf(form_data)
        safe_name = form_data.nombre.replace(' ', '_')
        message.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=f"Contrato_Hipha_{safe_name}.pdf")
    except Exception as e:
        logger.error(f"Error al generar o adjuntar PDF en send_contract_followup_email: {e}")
    
    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Correo de contrato enviado exitosamente a {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de contrato a {form_data.email}: {str(e)}")
        return False


async def send_healthyice_order_customer(form_data):
    healthyice_configured = bool(settings.HEALTHYICE_SMTP_HOST and settings.HEALTHYICE_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not healthyice_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a cliente HealthyIce {form_data.email}")
        return True

    from_email = settings.HEALTHYICE_EMAILS_FROM_EMAIL if settings.HEALTHYICE_EMAILS_FROM_EMAIL else "hola@healthyice.mx"
    from_name = settings.HEALTHYICE_EMAILS_FROM_NAME if settings.HEALTHYICE_EMAILS_FROM_NAME else "HealthyIce"
    
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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HEALTHYICE",
        from_name=from_name,
        from_email=from_email,
        to_email=form_data.email,
        subject=f"¡Hemos recibido tus datos, {form_data.nombre}!",
        html_content=html_content,
        domain="healthyice.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo a cliente HealthyIce: {str(e)}")
        return False

async def send_healthyice_order_team(form_data):
    healthyice_configured = bool(settings.HEALTHYICE_SMTP_HOST and settings.HEALTHYICE_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not healthyice_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo HealthyIce")
        return True

    from_email = settings.HEALTHYICE_EMAILS_FROM_EMAIL if settings.HEALTHYICE_EMAILS_FROM_EMAIL else "hola@healthyice.mx"
    to_email = settings.HEALTHYICE_EMAILS_FROM_EMAIL if settings.HEALTHYICE_EMAILS_FROM_EMAIL else "hola@healthyice.mx, contacto@healthyice.mx"
    
    mensaje_formatted = form_data.mensaje.replace('\n', '<br>')
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>¡Nuevo pedido recibido (Pendiente de Pago contra entrega)!</h2>
        
        <h3>Datos de Contacto:</h3>
        <ul>
            <li><strong>Nombre:</strong> {form_data.nombre}</li>
            <li><strong>Email:</strong> {form_data.email}</li>
            <li><strong>Teléfono:</strong> {form_data.telefono}</li>
            <li><strong>Método de Pago:</strong> Pago contra entrega (Efectivo/Transferencia - PENDIENTE DE PAGO)</li>
        </ul>
        
        <h3>Detalles de la Orden / Mensaje:</h3>
        <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; line-height: 1.5;">
            {mensaje_formatted}
        </div>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HEALTHYICE",
        from_name="HealthyIce Web",
        from_email=from_email,
        to_email=to_email,
        subject=f"NUEVO PEDIDO PENDIENTE (Efectivo/Transferencia): {form_data.nombre}",
        html_content=html_content,
        domain="healthyice.mx"
    )
    del message['Reply-To']
    message['Reply-To'] = form_data.email

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo al equipo HealthyIce: {str(e)}")
        return False


async def send_healthyice_payment_customer(payer_name: str, payer_email: str, order_details: str, total: float):
    healthyice_configured = bool(settings.HEALTHYICE_SMTP_HOST and settings.HEALTHYICE_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not healthyice_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a cliente HealthyIce {payer_email}")
        return True

    from_email = settings.HEALTHYICE_EMAILS_FROM_EMAIL if settings.HEALTHYICE_EMAILS_FROM_EMAIL else "hola@healthyice.mx"
    from_name = settings.HEALTHYICE_EMAILS_FROM_NAME if settings.HEALTHYICE_EMAILS_FROM_NAME else "HealthyIce"
    
    html_content = f"""
    <html>
    <body style="font-family: 'Quicksand', Arial, sans-serif; color: #101729; background-color: #f8fafc; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px;">
            <h2 style="color: #101729; font-weight: bold;">Hola {payer_name},</h2>
            <p>Hemos recibido el pago de tu pedido de paletas HealthyIce. Nuestro equipo comenzará a prepararlo de inmediato para su entrega.</p>
            <h3 style="color: #101729; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px;">Resumen de tu pedido:</h3>
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
                {order_details}
                <p><strong>Total pagado: ${total} MXN</strong></p>
            </div>
            <p>Si tienes alguna duda, puedes responder directamente a este correo o contactarnos por WhatsApp.</p>
            <br>
            <p style="color: #98BC3C; font-weight: bold;">El equipo de HealthyIce</p>
        </div>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HEALTHYICE",
        from_name=from_name,
        from_email=from_email,
        to_email=payer_email,
        subject=f"¡Tu pedido de HealthyIce está en camino, {payer_name}!",
        html_content=html_content,
        domain="healthyice.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de pago a cliente HealthyIce: {str(e)}")
        return False


async def send_healthyice_payment_team(payer_name: str, payer_email: str, payer_phone: str, address_str: str, order_details: str, total: float):
    healthyice_configured = bool(settings.HEALTHYICE_SMTP_HOST and settings.HEALTHYICE_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not healthyice_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo HealthyIce")
        return True

    from_email = settings.HEALTHYICE_EMAILS_FROM_EMAIL if settings.HEALTHYICE_EMAILS_FROM_EMAIL else "hola@healthyice.mx"
    to_email = settings.HEALTHYICE_EMAILS_FROM_EMAIL if settings.HEALTHYICE_EMAILS_FROM_EMAIL else "hola@healthyice.mx, contacto@healthyice.mx"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>¡Nuevo pedido recibido y PAGADO!</h2>
        
        <h3>Datos del Cliente:</h3>
        <ul>
            <li><strong>Nombre:</strong> {payer_name}</li>
            <li><strong>Email:</strong> {payer_email}</li>
            <li><strong>Teléfono:</strong> {payer_phone}</li>
            <li><strong>Dirección/Notas:</strong> {address_str}</li>
            <li><strong>Método de Pago:</strong> Tarjeta (PAGADO por Mercado Pago)</li>
        </ul>
        
        <h3>Detalles del Pedido:</h3>
        {order_details}
        <p><strong>Total: ${total} MXN</strong></p>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HEALTHYICE",
        from_name="HealthyIce Web",
        from_email=from_email,
        to_email=to_email,
        subject=f"NUEVO PEDIDO PAGADO (Mercado Pago): {payer_name} - ${total} MXN",
        html_content=html_content,
        domain="healthyice.mx"
    )
    del message['Reply-To']
    message['Reply-To'] = payer_email

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo al equipo HealthyIce por pedido pagado: {str(e)}")
        return False


class HealthyIcePDF(FPDF):
    def header(self):
        logo_path = os.path.join("app", "assets", "logo_healthyice.svg")
        if os.path.exists(logo_path):
            self.image(logo_path, x=150, y=10, w=45)


def generate_healthyice_contract_pdf(form_data) -> bytes:
    # Set up FPDF with margins (top margin 32 to avoid overlapping header logo on all pages)
    pdf = HealthyIcePDF()
    pdf.set_margins(15, 32, 15)
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(16, 23, 41)
    pdf.cell(0, 8, text="CONTRATO DE COLABORACION COMERCIAL", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    
    # Body text / Introduction
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    
    # Extract form data fields and convert to uppercase, handling blank spaces if manual print is requested
    llenado_manual = getattr(form_data, 'llenado_manual', False)
    
    if llenado_manual:
        razon_social_val = "________________________________________________"
        nombre_val = "________________________________________________"
        nombre_establecimiento_val = "________________________________________________"
        rfc_val = "________________________"
        domicilio_val = "________________________________________________"
        email_val = "________________________"
        telefono_val = "________________________"
        esquema = "________________________"
        metodo = "________________________"
        rep_healthy = (getattr(form_data, 'representante_healthyice', '') or '').upper() or "________________________"
        frecuencia_pagos_val = "________________________"
        vigencia_meses_val = "____"
        fecha_inicio_dia_val = "____"
        fecha_inicio_mes_val = "________________"
        fecha_inicio_anio_val = "________"
        fecha_val = "________________________"
        ciudad_jurisdiccion_val = (getattr(form_data, 'ciudad_jurisdiccion', '') or '').upper() or "________________________"
    else:
        razon_social_val = (getattr(form_data, 'razon_social', '') or '').upper() or "________________________________________________"
        nombre_val = (getattr(form_data, 'nombre', '') or '').upper() or "________________________________________________"
        nombre_establecimiento_val = (getattr(form_data, 'nombre_establecimiento', '') or '').upper() or "________________________________________________"
        rfc_val = (getattr(form_data, 'rfc', '') or '').upper() or "________________________"
        domicilio_val = (getattr(form_data, 'domicilio', '') or '').upper() or "________________________________________________"
        email_val = (getattr(form_data, 'email', '') or '').upper() or "________________________"
        telefono_val = (getattr(form_data, 'telefono', '') or '').upper() or "________________________"
        
        esquema = (getattr(form_data, 'esquema_comercial', '') or 'COMPRA DIRECTA').upper()
        esquema_otro = (getattr(form_data, 'esquema_comercial_otro', '') or '').upper()
        if esquema == "OTRO" and esquema_otro:
            esquema = f"OTRO: {esquema_otro}"
        elif esquema == "OTRO":
            esquema = "OTRO"
            
        metodo = (getattr(form_data, 'metodo_pago', '') or 'TRANSFERENCIA BANCARIA').upper()
        metodo_otro = (getattr(form_data, 'metodo_pago_otro', '') or '').upper()
        if metodo == "OTRO" and metodo_otro:
            metodo = f"OTRO: {metodo_otro}"
        elif metodo == "OTRO":
            metodo = "OTRO"
    
        rep_healthy = (getattr(form_data, 'representante_healthyice', '') or "FRANCISCO DELGADILLO").upper()
        frecuencia_pagos_val = (getattr(form_data, 'frecuencia_pagos', '') or 'SEMANAL').upper()
        vigencia_meses_val = getattr(form_data, 'vigencia_meses', 12) or 12
        
        fecha_inicio_dia_val = getattr(form_data, 'fecha_inicio_dia', None)
        fecha_inicio_mes_val = (getattr(form_data, 'fecha_inicio_mes', '') or '').upper()
        fecha_inicio_anio_val = getattr(form_data, 'fecha_inicio_anio', None)
        
        # Fallback to current date if details are missing
        import datetime
        now = datetime.datetime.now()
        if fecha_inicio_dia_val is None:
            fecha_inicio_dia_val = now.day
        if not fecha_inicio_mes_val:
            meses_es = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
            fecha_inicio_mes_val = meses_es[now.month - 1]
        if fecha_inicio_anio_val is None:
            fecha_inicio_anio_val = now.year
    
        fecha_val = (getattr(form_data, 'fecha', '') or f"{fecha_inicio_dia_val} de {fecha_inicio_mes_val} de {fecha_inicio_anio_val}").upper()
        ciudad_jurisdiccion_val = (getattr(form_data, 'ciudad_jurisdiccion', '') or 'GUADALAJARA, JALISCO').upper()
    
    if llenado_manual:
        intro_text = (
            "CONTRATO DE COLABORACION COMERCIAL que celebran por una parte HEALTHY ICE, representada por "
            "________________________________, a quien en lo sucesivo se le denominara \"HEALTHY ICE\", y por la otra "
            "________________________________ , representada por ___________________________________( Nombre del Establecimiento), "
            "a quien en lo sucesivo se le denominara \"SOCIO DE NEGOCIO\", al tenor de las siguientes declaraciones "
            "y clausulas:"
        )
    else:
        intro_text = (
            f"CONTRATO DE COLABORACION COMERCIAL que celebran por una parte HEALTHY ICE, representada por "
            f"{rep_healthy}, a quien en lo sucesivo se le denominara \"HEALTHY ICE\", y por la otra "
            f"{razon_social_val}, representada por {nombre_val} (Nombre del Establecimiento: {nombre_establecimiento_val}), "
            f"a quien en lo sucesivo se le denominara \"SOCIO DE NEGOCIO\", al tenor de las siguientes declaraciones "
            f"y clausulas:"
        )
    pdf.multi_cell(0, 5, text=intro_text.encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    # Declaraciones
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, text="DECLARACIONES", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, text="I. DECLARA HEALTHY ICE:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    dec_hi = [
        "1. Que es una empresa dedicada a la fabricacion, comercializacion y distribucion de paletas, helados y alimentos congelados con enfoque saludable.",
        "2. Que cuenta con capacidad legal para celebrar el presente contrato.",
        "3. Que tiene interes en comercializar sus productos a traves de puntos de venta externos."
    ]
    for dec in dec_hi:
        pdf.multi_cell(0, 4.5, text=dec.encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, text="II. DECLARA EL SOCIO DE NEGOCIO:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    
    if llenado_manual:
        dec_socio = [
            "1. Que es propietario, representante o administrador del establecimiento denominado:\n_______________________________________________________",
            "1. Que cuenta con las instalaciones necesarias para la exhibicion, conservacion y venta de los productos HEALTHY ICE.",
            "2. Que tiene interes en comercializar los productos objeto de este contrato.",
            "3. Que cuenta con facultades suficientes para celebrar el presente acuerdo."
        ]
    else:
        dec_socio = [
            f"1. Que es propietario, representante o administrador del establecimiento denominado: {nombre_establecimiento_val}",
            f"2. Que cuenta con las instalaciones necesarias para la exhibicion, conservacion y venta de los productos HEALTHY ICE (incluyendo domicilio en {domicilio_val} y RFC {rfc_val}).",
            "3. Que tiene interes en comercializar los productos objeto de este contrato.",
            "4. Que cuenta con facultades suficientes para celebrar el presente acuerdo."
        ]
    for dec in dec_socio:
        pdf.multi_cell(0, 4.5, text=dec.encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 4.5, text="Ambas partes manifiestan su voluntad para sujetarse a las siguientes:".encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Clausulas
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, text="CLAUSULAS", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(2)
    
    # List of clauses
    if llenado_manual:
        clauses = [
            ("PRIMERA. OBJETO", 
             "HEALTHY ICE entregara productos al SOCIO DE NEGOCIO para su comercializacion dentro de su establecimiento bajo el esquema de:\n"
             "( ) Consignacion\n"
             "( ) Compra directa\n"
             "( ) Otro: __________________________"),
            
            ("SEGUNDA. PRODUCTOS", 
             "Los productos incluidos en este acuerdo seran aquellos comercializados por HEALTHY ICE, pudiendo modificarse, ampliarse o sustituirse mediante aviso entre las partes."),
            
            ("TERCERA. PRECIOS", 
             "Las partes acuerdan que los precios de venta al SOCIO DE NEGOCIO seran establecidos por HEALTHY ICE mediante listas de precios vigentes.\n"
             "El precio publico sugerido sera comunicado por HEALTHY ICE para mantener la uniformidad comercial de la marca."),
            
            ("CUARTA. CONSERVACION DEL PRODUCTO", 
             "El SOCIO DE NEGOCIO debera mantener los productos a la temperatura adecuada para garantizar su calidad.\n"
             "Cualquier perdida derivada de:\n"
             "*      Desconexion del congelador.\n"
             "*      Fallas electricas no reportadas.\n"
             "*      Manejo inadecuado.\n"
             "*      Negligencia operativa.\n"
             "sera responsabilidad del SOCIO DE NEGOCIO."),
            
            ("QUINTA. PAGOS", 
             "Los pagos deberan realizarse de forma:\n"
             "( ) Semanal\n"
             "( ) Quincenal\n"
             "( ) Mensual\n"
             "Mediante:\n"
             "( ) Transferencia bancaria\n"
             "( ) Efectivo\n"
             "( ) Deposito\n"
             "( ) Otro: ___________________"),
            
            ("SEXTA. PUBLICIDAD Y MARCA", 
             "El SOCIO DE NEGOCIO podra utilizar materiales promocionales proporcionados por HEALTHY ICE unicamente para promover los productos objeto de este contrato.\n"
             "Las marcas, logotipos, designs e imagen comercial seguiran siendo propiedad exclusiva de HEALTHY ICE."),
            
            ("SEPTIMA. VIGENCIA", 
             "El presente contrato tendra una vigencia inicial de:\n"
             "_______ meses.\n"
             "Iniciando el dia ____ de ______________ de _______.\n"
             "Al concluir dicho plazo podra renovarse por acuerdo entre las partes."),
            
            ("OCTAVA. TERMINACION ANTICIPADA", 
             "Cualquiera de las partes podra dar por terminado el contrato mediante aviso por escrito con al menos 15 dias naturales de anticipacion.\n"
             "Asimismo, HEALTHY ICE podra rescindir inmediatamente el contrato por:\n"
             "*      Falta de pago.\n"
             "*      Uso indebido de la marca.\n"
             "*      Alteracion de productos.\n"
             "*      Mal uso del equipo.\n"
             "*      Informacion falsa.\n"
             "*      Incumplimiento de las obligaciones establecidas."),
            
            ("NOVENA. CONFIDENCIALIDAD", 
             "El SOCIO DE NEGOCIO se obliga a mantener confidencial cualquier informacion comercial, financiera, operativa o estrategica proporcionada por HEALTHY ICE."),
            
            ("DECIMA TERCERA. JURISDICCION", 
             "Para la interpretacion y cumplimiento del presente contrato, las partes se someten a las leyes y tribunales competentes de la ciudad de:\n\n"
             "renunciando a cualquier otro fuero que pudiera corresponderles.")
         ]
    else:
        clauses = [
            ("PRIMERA. OBJETO", 
             f"HEALTHY ICE entregara productos al SOCIO DE NEGOCIO para su comercializacion dentro de su establecimiento bajo el esquema de: {esquema}."),
            
            ("SEGUNDA. PRODUCTOS", 
             "Los productos incluidos en este acuerdo seran aquellos comercializados por HEALTHY ICE, pudiendo modificarse, ampliarse o sustituirse mediante aviso entre las partes."),
            
            ("TERCERA. PRECIOS", 
             "Las partes acuerdan que los precios de venta al SOCIO DE NEGOCIO seran establecidos por HEALTHY ICE mediante listas de precios vigentes.\n"
             "El precio publico sugerido sera comunicado por HEALTHY ICE para mantener la uniformidad comercial de la marca."),
            
            ("CUARTA. CONSERVACION DEL PRODUCTO", 
             "El SOCIO DE NEGOCIO debera mantener los productos a la temperatura adecuada para garantizar su calidad. Cualquier perdida derivada de:\n"
             "  - Desconexion del congelador.\n"
             "  - Fallas electricas no reportadas.\n"
             "  - Manejo inadecuado.\n"
             "  - Negligencia operativa.\n"
             "sera responsabilidad del SOCIO DE NEGOCIO."),
            
            ("QUINTA. PAGOS", 
             f"Los pagos deberan realizarse de forma: {frecuencia_pagos_val}. Mediante: {metodo}."),
            
            ("SEXTA. PUBLICIDAD Y MARCA", 
             "El SOCIO DE NEGOCIO podra utilizar materiales promocionales proporcionados por HEALTHY ICE unicamente para promover los productos objeto de este contrato.\n"
             "Las marcas, logotipos, diseños e imagen comercial seguiran siendo propiedad exclusiva de HEALTHY ICE."),
            
            ("SEPTIMA. VIGENCIA", 
             f"El presente contrato tendra una vigencia inicial de: {vigencia_meses_val} meses. Iniciando el dia {fecha_inicio_dia_val} de {fecha_inicio_mes_val} de {fecha_inicio_anio_val}.\n"
             "Al concluir dicho plazo podra renovarse por acuerdo entre las partes."),
            
            ("OCTAVA. TERMINACION ANTICIPADA", 
             "Cualquiera de las partes podra dar por terminado el contrato mediante aviso por escrito con al menos 15 dias naturales de anticipacion.\n"
             "Asimismo, HEALTHY ICE podra rescindir inmediatamente el contrato por:\n"
             "  - Falta de pago.\n"
             "  - Uso indebido de la marca.\n"
             "  - Alteracion de productos.\n"
             "  - Mal uso del equipo.\n"
             "  - Informacion falsa.\n"
             "  - Incumplimiento de las obligaciones establecidas."),
            
            ("NOVENA. CONFIDENCIALIDAD", 
             "El SOCIO DE NEGOCIO se obliga a mantener confidencial cualquier informacion comercial, financiera, operativa o estrategica proporcionada por HEALTHY ICE."),
            
            ("DECIMA TERCERA. JURISDICCION", 
             f"Para la interpretacion y cumplimiento del presente contrato, las partes se someten a las leyes y tribunales competentes de la ciudad de: {ciudad_jurisdiccion_val}, renunciando a cualquier otro fuero que pudiera corresponderles.")
        ]
    
    for title, text in clauses:
        pdf.set_font("Helvetica", "B", 9)
        pdf.multi_cell(0, 5, text=title.encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 4.5, text=text.encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2.5)
        # Extra spacing for blank checkboxes
        if llenado_manual and title in ["PRIMERA. OBJETO", "QUINTA. PAGOS"]:
            pdf.ln(4)
        
    pdf.ln(5)
    
    # Signatures page break detection (more space needed for sequential vertical signatures block in blank mode)
    limit_y = 150 if llenado_manual else 180
    if pdf.get_y() > limit_y:
        pdf.add_page()
        
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 4.5, text="Leido que fue el presente contrato y enteradas las partes de su contenido y alcance legal, lo firman por duplicado.".encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    
    y_before_sigs = pdf.get_y()
    
    if llenado_manual:
        # Sequential vertical signatures as requested in the template
        # HEALTHY ICE
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 5, text="HEALTHY ICE", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, text="Nombre: ____________________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.cell(0, 5, text="Cargo: ______________________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.cell(0, 5, text="Firma: ______________________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.cell(0, 5, text="Fecha: ______________________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.ln(5)
        
        # SOCIO DE NEGOCIO
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 5, text="SOCIO DE NEGOCIO", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, text="Razon Social / Nombre: ________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.cell(0, 5, text="Representante: _______________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.cell(0, 5, text="Firma: ______________________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.cell(0, 5, text="Fecha: ______________________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.ln(5)
        
        # Witness 1
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 5, text="TESTIGO 1", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, text="Nombre: ____________________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.cell(0, 5, text="Firma: ______________________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.ln(5)
        
        # Witness 2
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 5, text="TESTIGO 2", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, text="Nombre: ____________________________________", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.cell(0, 5, text="Firma: ______________________________________", new_x="LMARGIN", new_y="NEXT", align="L")
    else:
        # Column 1: HEALTHY ICE
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(90, 5, text="HEALTHY ICE", new_x="LMARGIN", new_y="NEXT", align="C")
        
        # Empty space for physical signature
        pdf.ln(18)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 4, text="________________________________", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(90, 4, text=f"Nombre: {rep_healthy}".encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(90, 4, text="Cargo: Representante Legal", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(90, 4, text=f"Fecha: {fecha_val}", new_x="LMARGIN", new_y="NEXT", align="C")
        
        # Column 2: SOCIO DE NEGOCIO
        pdf.set_y(y_before_sigs)
        pdf.set_x(110)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(90, 5, text="SOCIO DE NEGOCIO", new_x="LMARGIN", new_y="NEXT", align="C")
        
        # Empty space for physical signature
        pdf.set_y(y_before_sigs + 23)
        pdf.set_x(110)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 4, text="________________________________", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_x(110)
        pdf.cell(90, 4, text=f"Razon Social / Nombre: {razon_social_val}".encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_x(110)
        pdf.cell(90, 4, text=f"Representante: {nombre_val}".encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_x(110)
        pdf.cell(90, 4, text=f"Fecha: {fecha_val}", new_x="LMARGIN", new_y="NEXT", align="C")
        
        # Witness Row
        pdf.ln(15)
        if pdf.get_y() > 220:
            pdf.add_page()
            
        y_witnesses = pdf.get_y()
        
        # Witness 1
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(90, 5, text="TESTIGO 1", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 4, text="________________________________", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(90, 4, text="Nombre:", new_x="LMARGIN", new_y="NEXT", align="C")
        
        # Witness 2
        pdf.set_y(y_witnesses)
        pdf.set_x(110)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(90, 5, text="TESTIGO 2", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_x(110)
        pdf.cell(90, 4, text="________________________________", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_x(110)
        pdf.cell(90, 4, text="Nombre:", new_x="LMARGIN", new_y="NEXT", align="C")
    
    return bytes(pdf.output())


async def send_healthyice_contract_customer(form_data):
    healthyice_configured = bool(settings.HEALTHYICE_SMTP_HOST and settings.HEALTHYICE_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not healthyice_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envio de contrato HealthyIce a {form_data.email}")
        return True

    from_email = settings.HEALTHYICE_EMAILS_FROM_EMAIL if settings.HEALTHYICE_EMAILS_FROM_EMAIL else "hola@healthyice.mx"
    from_name = settings.HEALTHYICE_EMAILS_FROM_NAME if settings.HEALTHYICE_EMAILS_FROM_NAME else "HealthyIce"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="healthyice.mx")
    
    html_content = f"""
    <html>
    <body style="font-family: 'Quicksand', Arial, sans-serif; color: #101729; background-color: #f8fafc; padding: 20px; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <h2 style="color: #0077ff; font-weight: bold; margin-top: 0;">¡Firma de Contrato Confirmada!</h2>
            <p>Hola <strong>{form_data.nombre}</strong>,</p>
            <p>Queremos darte la mas cordial bienvenida a nuestra red de socios comerciales. Hemos recibido correctamente la firma de tu contrato digital de colaboracion comercial.</p>
            
            <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #cbd5e1; font-size: 14px;">
                <h3 style="margin-top: 0; color: #101729;">Resumen de tu Contrato Comercial:</h3>
                <p style="margin: 5px 0;"><strong>Razon Social / Nombre:</strong> {form_data.razon_social}</p>
                <p style="margin: 5px 0;"><strong>Representante:</strong> {form_data.nombre}</p>
                <p style="margin: 5px 0;"><strong>Establecimiento:</strong> {getattr(form_data, 'nombre_establecimiento', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>RFC:</strong> {form_data.rfc}</p>
                <p style="margin: 5px 0;"><strong>Esquema Comercial:</strong> {getattr(form_data, 'esquema_comercial', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>Frecuencia de Pagos:</strong> {getattr(form_data, 'frecuencia_pagos', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>Domicilio:</strong> {form_data.domicilio}</p>
            </div>
            
            <p>Adjunto a este correo encontraras tu contrato firmado en formato PDF. Por favor, conservalo para tus registros.</p>
            <p>Muy pronto un miembro de nuestro equipo comercial se comunicara contigo para coordinar tu primer pedido y la instalacion del equipo de congelacion si aplica.</p>
            
            <br>
            <p style="color: #98BC3C; font-weight: bold; margin-bottom: 0;">El equipo de HealthyIce</p>
        </div>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HEALTHYICE",
        from_name=from_name,
        from_email=from_email,
        to_email=form_data.email,
        subject="¡Bienvenido a HealthyIce! Contrato de Colaboracion Comercial",
        html_content=html_content,
        domain="healthyice.mx"
    )

    try:
        pdf_bytes = generate_healthyice_contract_pdf(form_data)
        safe_name = form_data.razon_social.replace(' ', '_').replace('/', '_')
        message.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=f"Contrato_HealthyIce_{safe_name}.pdf")
    except Exception as e:
        logger.error(f"Error al generar o adjuntar PDF en send_healthyice_contract_customer: {e}")
        
    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Correo de contrato HealthyIce enviado a cliente: {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de contrato HealthyIce a cliente: {str(e)}")
        return False


async def send_healthyice_contract_team(form_data):
    healthyice_configured = bool(settings.HEALTHYICE_SMTP_HOST and settings.HEALTHYICE_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not healthyice_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envio de contrato HealthyIce al equipo")
        return True

    from_email = settings.HEALTHYICE_EMAILS_FROM_EMAIL if settings.HEALTHYICE_EMAILS_FROM_EMAIL else "hola@healthyice.mx"
    to_email = settings.HEALTHYICE_EMAILS_FROM_EMAIL if settings.HEALTHYICE_EMAILS_FROM_EMAIL else "hola@healthyice.mx, contacto@healthyice.mx"
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain="healthyice.mx")
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #33; line-height: 1.6;">
        <h2>¡Nuevo Socio Comercial Firmado desde la Web!</h2>
        <p>Se ha recibido un nuevo contrato firmado digitalmente. A continuacion, se detallan los datos del socio comercial:</p>
        
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px; max-width: 600px; border: 1px solid #ddd;">
            <tr style="background: #f4f4f4; border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold; width: 180px;">Razon Social / Nombre:</td>
                <td style="padding: 10px;">{form_data.razon_social}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold;">Representante Legal:</td>
                <td style="padding: 10px;">{getattr(form_data, 'nombre', 'N/A')}</td>
            </tr>
            <tr style="background: #f4f4f4; border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold;">Establecimiento:</td>
                <td style="padding: 10px;">{getattr(form_data, 'nombre_establecimiento', 'N/A')}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold;">RFC:</td>
                <td style="padding: 10px;">{form_data.rfc}</td>
            </tr>
            <tr style="background: #f4f4f4; border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold;">Esquema Comercial:</td>
                <td style="padding: 10px;">{getattr(form_data, 'esquema_comercial', 'N/A')}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold;">Frecuencia de Pagos:</td>
                <td style="padding: 10px;">{getattr(form_data, 'frecuencia_pagos', 'N/A')}</td>
            </tr>
            <tr style="background: #f4f4f4; border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold;">Metodo de Pago:</td>
                <td style="padding: 10px;">{getattr(form_data, 'metodo_pago', 'N/A')}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold;">Domicilio Comercial:</td>
                <td style="padding: 10px;">{form_data.domicilio}</td>
            </tr>
            <tr style="background: #f4f4f4; border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold;">Email:</td>
                <td style="padding: 10px;"><a href="mailto:{form_data.email}">{form_data.email}</a></td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold;">Telefono:</td>
                <td style="padding: 10px;">{form_data.telefono}</td>
            </tr>
        </table>
        
        <p>Adjunto encontraras la copia del contrato en formato PDF con la firma del socio.</p>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="HEALTHYICE",
        from_name="HealthyIce Web",
        from_email=from_email,
        to_email=to_email,
        subject=f"NUEVO SOCIO COMERCIAL FIRMADO: {form_data.razon_social}",
        html_content=html_content,
        domain="healthyice.mx"
    )
    del message['Reply-To']
    message['Reply-To'] = form_data.email

    try:
        pdf_bytes = generate_healthyice_contract_pdf(form_data)
        safe_name = form_data.razon_social.replace(' ', '_').replace('/', '_')
        message.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=f"Contrato_HealthyIce_{safe_name}.pdf")
    except Exception as e:
        logger.error(f"Error al generar o adjuntar PDF en send_healthyice_contract_team: {e}")
        
    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info("Notificacion de contrato HealthyIce enviada al equipo")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificacion de contrato HealthyIce al equipo: {str(e)}")
        return False


async def send_whiteclean_confirmation_email(form_data):
    whiteclean_configured = bool(settings.WHITECLEAN_SMTP_HOST and settings.WHITECLEAN_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not whiteclean_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a prospecto WhiteClean {form_data.email}")
        return True

    from_email = settings.WHITECLEAN_EMAILS_FROM_EMAIL if settings.WHITECLEAN_EMAILS_FROM_EMAIL else "clientes@whiteclean.com.mx"
    from_name = settings.WHITECLEAN_EMAILS_FROM_NAME if settings.WHITECLEAN_EMAILS_FROM_NAME else "WhiteClean Limpieza Especializada"

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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="WHITECLEAN",
        from_name=from_name,
        from_email=from_email,
        to_email=form_data.email,
        subject=f"¡Hemos recibido tu solicitud, {form_data.nombre}! ✨",
        html_content=html_content,
        domain="whiteclean.com.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Correo de confirmación WhiteClean enviado exitosamente a {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de confirmación WhiteClean a {form_data.email}: {str(e)}")
        return False


async def send_whiteclean_notification_team(form_data):
    whiteclean_configured = bool(settings.WHITECLEAN_SMTP_HOST and settings.WHITECLEAN_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not whiteclean_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo WhiteClean")
        return True

    from_email = settings.WHITECLEAN_EMAILS_FROM_EMAIL if settings.WHITECLEAN_EMAILS_FROM_EMAIL else "clientes@whiteclean.com.mx"

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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="WHITECLEAN",
        from_name="WhiteClean Web",
        from_email=from_email,
        to_email="clientes@whiteclean.com.mx, whiteclean1@hotmail.com",
        subject=f"🚨 NUEVA SOLICITUD WEB: {form_data.nombre} {form_data.apellido} - {form_data.servicio}",
        html_content=html_content,
        domain="whiteclean.com.mx"
    )
    del message['Reply-To']
    message['Reply-To'] = form_data.email

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info("Notificación de lead WhiteClean enviada con éxito al equipo y socio.")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación WhiteClean al equipo: {str(e)}")
        return False


async def send_chilechillon_confirmation_email(form_data):
    chile_configured = bool(settings.CHILECHILLON_SMTP_HOST and settings.CHILECHILLON_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not chile_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a prospecto Chile Chillón {form_data.email}")
        return True

    from_email = settings.CHILECHILLON_EMAILS_FROM_EMAIL if settings.CHILECHILLON_EMAILS_FROM_EMAIL else "hola@elchilechillon.com.mx"
    from_name = settings.CHILECHILLON_EMAILS_FROM_NAME if settings.CHILECHILLON_EMAILS_FROM_NAME else "Chile Chillón"

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
            
            <!-- Header con el Logotipo Oficial de Chile Chillón -->
            <div style="background-color: #080505; padding: 30px 20px; text-align: center; border-bottom: 4px solid #E50914;">
                <img src="https://elchilechillon.mx/Assets/Logo%20Navbar.svg" alt="Chile Chillón Logo" style="height: 65px; margin: 0 auto; display: block;">
            </div>
            
            <!-- Cuerpo del Correo -->
            <div style="padding: 40px 30px;">
                <h2 style="color: #ffffff; font-size: 22px; font-weight: 700; margin-top: 0; margin-bottom: 20px;">¡Hola, {form_data.nombre}! 👋</h2>
                <p style="font-size: 16px; line-height: 1.6; color: #cbd5e1; margin-bottom: 25px;">
                    Muchas gracias por tu interés en nuestros productos, recibimos tu información y te contactaremos lo antes posible, no tengas duda.
                </p>
                
                <!-- Tarjeta con resumen de solicitud -->
                <div style="background-color: rgba(229, 9, 20, 0.05); border-left: 4px solid #E50914; padding: 25px; border-radius: 0 16px 16px 0; margin-bottom: 30px; border-top: 1px solid rgba(229, 9, 20, 0.1); border-right: 1px solid rgba(229, 9, 20, 0.1); border-bottom: 1px solid rgba(229, 9, 20, 0.1);">
                    <h3 style="color: #FF6A00; font-size: 14px; font-weight: 800; margin-top: 0; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px;">DETALLES DE TU REGISTRO:</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px; line-height: 1.6; color: #e2e8f0;">
                        <tr>
                          <td style="padding: 6px 0; color: #94a3b8; width: 130px; font-weight: 600;">Perfil:</td>
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
                
                <p style="font-size: 15px; line-height: 1.6; color: #cbd5e1; margin-bottom: 25px;">
                    En Chile Chillón elaboramos salsas picantes con fórmulas minuciosamente balanceadas y 100% naturales, asegurando la consistencia exacta en cada lote desde hace 10 años. ¡Prepárate para experimentar tu sazón al máximo en los próximos días!
                </p>
                
                <p style="color: #FF6A00; font-weight: bold; font-size: 16px; margin: 0;">Equipo del Chile Chillón</p>
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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="CHILECHILLON",
        from_name=from_name,
        from_email=from_email,
        to_email=form_data.email,
        subject=f"¡Tu sazón está a punto de potenciarse, {form_data.nombre}! 🌶️🔥",
        html_content=html_content,
        domain="elchilechillon.com.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Correo de confirmación Chile Chillón enviado con éxito a {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de confirmación Chile Chillón a {form_data.email}: {str(e)}")
        return False


async def send_chilechillon_notification_team(form_data):
    chile_configured = bool(settings.CHILECHILLON_SMTP_HOST and settings.CHILECHILLON_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not chile_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío de notificación de Chile Chillón al equipo")
        return True

    from_email = settings.CHILECHILLON_EMAILS_FROM_EMAIL if settings.CHILECHILLON_EMAILS_FROM_EMAIL else "hola@elchilechillon.com.mx"
    to_email = settings.EMAILS_FROM_EMAIL if settings.EMAILS_FROM_EMAIL else "creativo@hipha.mx"

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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="CHILECHILLON",
        from_name="Chile Chillón Web",
        from_email=from_email,
        to_email=to_email,
        subject=f"🌶️ NUEVA SOLICITUD WEB CHILE CHILLÓN: {form_data.nombre} - {form_data.perfil.upper()}",
        html_content=html_content,
        domain="elchilechillon.com.mx"
    )
    del message['Reply-To']
    message['Reply-To'] = form_data.email

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info("Notificación de lead Chile Chillón enviada con éxito al equipo.")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación de Chile Chillón al equipo: {str(e)}")
        return False


async def send_grupogari_confirmation_email(form_data):
    gari_configured = bool(settings.GRUPOGARI_SMTP_HOST and settings.GRUPOGARI_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not gari_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a prospecto Grupo Gari {form_data.email}")
        return True

    from_email = settings.GRUPOGARI_EMAILS_FROM_EMAIL if settings.GRUPOGARI_EMAILS_FROM_EMAIL else "contacto@grupogari.com"
    from_name = settings.GRUPOGARI_EMAILS_FROM_NAME if settings.GRUPOGARI_EMAILS_FROM_NAME else "Grupo Gari | Cumplimiento Regulatorio"

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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="GRUPOGARI",
        from_name=from_name,
        from_email=from_email,
        to_email=form_data.email,
        subject=f"Autodiagnóstico Recibido - Registro GARI-{form_data.nombre.upper()} 📄",
        html_content=html_content,
        domain="grupogari.com"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Correo de confirmación Grupo Gari enviado exitosamente a {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de confirmación Grupo Gari a {form_data.email}: {str(e)}")
        return False


async def send_grupogari_notification_team(form_data):
    gari_configured = bool(settings.GRUPOGARI_SMTP_HOST and settings.GRUPOGARI_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not gari_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo Grupo Gari")
        return True

    from_email = settings.GRUPOGARI_EMAILS_FROM_EMAIL if settings.GRUPOGARI_EMAILS_FROM_EMAIL else "contacto@grupogari.com"
    to_email = settings.EMAILS_FROM_EMAIL if settings.EMAILS_FROM_EMAIL else "contacto@grupogari.com"

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
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="GRUPOGARI",
        from_name="Grupo Gari Web",
        from_email=from_email,
        to_email=to_email,
        subject=f"🚨 NUEVO DIAGNÓSTICO WEB GARI: {form_data.nombre.upper()} - {form_data.servicio.upper()}",
        html_content=html_content,
        domain="grupogari.com"
    )
    del message['Reply-To']
    message['Reply-To'] = form_data.email

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info("Notificación de lead Grupo Gari enviada con éxito al equipo.")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación de Grupo Gari al equipo: {str(e)}")
        return False


async def send_valencia_servicios_notification_team(form_data):
    valencia_configured = bool(settings.VALENCIA_SMTP_HOST and settings.VALENCIA_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not valencia_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo Valencia Servicios: {form_data.nombre_completo}")
        return True

    from_email = settings.VALENCIA_EMAILS_FROM_EMAIL if settings.VALENCIA_EMAILS_FROM_EMAIL else "contacto@valenciaservicios.com.mx"
    to_email = settings.VALENCIA_SMTP_USER if valencia_configured else (settings.SMTP_USER if settings.SMTP_USER else "contacto@valenciaservicios.com.mx")

    html_content = f"""
    <html>
    <body style="font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1f2937; background-color: #f3f4f6; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05); border: 1px solid #e5e7eb;">
            
            <!-- Header con la identidad de Valencia Servicios -->
            <div style="background-color: #0f172a; padding: 30px 20px; text-align: center; border-bottom: 4px solid #00f0ff;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">
                    <span style="color: #00f0ff;">Valencia</span> Servicios
                </h1>
                <p style="margin: 5px 0 0 0; font-size: 13px; color: #94a3b8; letter-spacing: 1px;">NOTIFICACIÓN DE NUEVA SOLICITUD</p>
            </div>
            
            <!-- Cuerpo del Correo -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; line-height: 1.6; color: #4b5563; margin-top: 0; margin-bottom: 25px;">
                    Se ha recibido una nueva solicitud de servicio desde el formulario de la landing page. A continuación, se detallan los datos del cliente para su atención inmediata:
                </p>
                
                <!-- Tabla con detalles de solicitud -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 15px;">
                    <tr style="border-bottom: 1px solid #f3f4f6;">
                        <td style="padding: 12px 10px; font-weight: bold; color: #0f172a; width: 160px; background-color: #f9fafb; border-radius: 8px 0 0 8px;">Nombre Completo:</td>
                        <td style="padding: 12px 10px; color: #111827; background-color: #f9fafb; border-radius: 0 8px 8px 0;">{form_data.nombre_completo}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f3f4f6;">
                        <td style="padding: 12px 10px; font-weight: bold; color: #0f172a; background-color: #ffffff;">Teléfono:</td>
                        <td style="padding: 12px 10px; color: #111827; background-color: #ffffff;">
                            <a href="tel:{form_data.telefono}" style="color: #00b4d8; text-decoration: none; font-weight: bold;">{form_data.telefono}</a>
                        </td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f3f4f6;">
                        <td style="padding: 12px 10px; font-weight: bold; color: #0f172a; background-color: #f9fafb; border-radius: 8px 0 0 8px;">Servicio Solicitado:</td>
                        <td style="padding: 12px 10px; color: #00b4d8; font-weight: bold; background-color: #f9fafb; border-radius: 0 8px 8px 0;">{form_data.servicio_requerido}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f3f4f6;">
                        <td style="padding: 12px 10px; font-weight: bold; color: #0f172a; background-color: #ffffff;">Dirección del Servicio:</td>
                        <td style="padding: 12px 10px; color: #111827; background-color: #ffffff;">{form_data.direccion}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f3f4f6;">
                        <td style="padding: 12px 10px; font-weight: bold; color: #0f172a; background-color: #f9fafb; border-radius: 8px 0 0 8px;">Horario Preferido:</td>
                        <td style="padding: 12px 10px; color: #111827; background-color: #f9fafb; border-radius: 0 8px 8px 0;">{form_data.horario_preferido}</td>
                    </tr>
                </table>
                
                <div style="background-color: #ecfeff; border-left: 4px solid #00f0ff; padding: 15px 20px; border-radius: 0 8px 8px 0; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 14px; line-height: 1.5; color: #0e7490; font-weight: 500;">
                        💡 <strong>Sugerencia:</strong> Haz clic en el número de teléfono arriba para llamar directamente al cliente o guardarlo.
                    </p>
                </div>
            </div>
            
            <!-- Footer del Correo -->
            <div style="background-color: #f9fafb; padding: 25px; text-align: center; border-top: 1px solid #e5e7eb; font-size: 12px; color: #9ca3af;">
                <p style="margin: 0 0 8px 0;">Este correo fue generado automáticamente por la landing page de <strong>Valencia Servicios</strong>.</p>
                <p style="margin: 0;">Zona de Servicio Principal: Zapopan, Jalisco.</p>
            </div>
            
        </div>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="VALENCIA",
        from_name="Valencia Servicios Web",
        from_email=from_email,
        to_email=to_email,
        subject=f"🛠️ NUEVO SERVICIO SOLICITADO: {form_data.nombre_completo} - {form_data.servicio_requerido}",
        html_content=html_content,
        domain="valenciaservicios.com.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Notificación de Valencia Servicios enviada con éxito para el cliente {form_data.nombre_completo}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar notificación de Valencia Servicios para el cliente {form_data.nombre_completo}: {str(e)}")
        return False


def _prepare_project_email(
    project_prefix: str,
    from_name: str,
    from_email: str,
    to_email: str,
    subject: str,
    html_content: str,
    domain: str
) -> tuple[EmailMessage, str, int, str, str]:
    prefix = project_prefix.upper()
    
    # Check if specific SMTP is configured
    specific_host = getattr(settings, f"{prefix}_SMTP_HOST", "")
    specific_user = getattr(settings, f"{prefix}_SMTP_USER", "")
    
    project_configured = bool(specific_host and specific_user)
    
    # Resolve SMTP details
    smtp_host = specific_host if project_configured else settings.SMTP_HOST
    smtp_port = getattr(settings, f"{prefix}_SMTP_PORT", 587) if project_configured else settings.SMTP_PORT
    smtp_user = specific_user if project_configured else settings.SMTP_USER
    smtp_password = getattr(settings, f"{prefix}_SMTP_PASSWORD", "") if project_configured else settings.SMTP_PASSWORD
    
    # Coerce port
    if smtp_port == "" or smtp_port is None:
        smtp_port = 587
    else:
        try:
            smtp_port = int(smtp_port)
        except ValueError:
            smtp_port = 587

    # Domain alignment validation for safety checks
    if smtp_user:
        smtp_user_lower = smtp_user.lower()
        if prefix == "HIPHA":
            # Global agency SMTP must belong to agency domain
            if "hipha.mx" not in smtp_user_lower:
                logger.critical(
                    f"[SMTP ALIGNMENT CRITICAL ERROR] Global agency SMTP user '{smtp_user}' "
                    f"does not belong to the expected domain 'hipha.mx'. "
                    f"Check Vercel env variables!"
                )
        else:
            # Client/Project SMTP
            if project_configured:
                # If project-specific SMTP is configured, it must align with the project's domain
                if domain.lower() not in smtp_user_lower:
                    logger.warning(
                        f"[SMTP ALIGNMENT WARNING] Project '{prefix}' has specific SMTP configured "
                        f"with user '{smtp_user}' but it does not match its domain '{domain}'."
                    )
            else:
                # If falling back to agency SMTP, log info but don't warn about client domain mismatch
                logger.info(
                    f"[SMTP INFO] Project '{prefix}' using agency SMTP fallback ({smtp_user}). "
                    f"Will reply to: {from_email}"
                )

    # Real From calculation to avoid SPF / Sender mismatch failure
    actual_from = smtp_user

    message = EmailMessage()
    message["From"] = f"{from_name} <{actual_from}>"
    message.add_header('Reply-To', from_email)
    message["To"] = to_email
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain=domain)
    message.set_content(html_content, subtype="html")
    
    return message, smtp_host, smtp_port, smtp_user, smtp_password


async def send_amdi_contact_confirmation_email(form_data):
    amdi_configured = bool(settings.AMDI_SMTP_HOST and settings.AMDI_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not amdi_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío de confirmación de contacto AMDI para {form_data.email}")
        return True

    from_email = settings.AMDI_EMAILS_FROM_EMAIL if settings.AMDI_EMAILS_FROM_EMAIL else "contacto@amdi.mx"
    from_name = settings.AMDI_EMAILS_FROM_NAME if settings.AMDI_EMAILS_FROM_NAME else "AMDI | Diseño de Interiores"

    html_content = f"""
    <html>
    <body style="font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif; color: #1e293b; background-color: #fafafa; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            
            <div style="background-color: #0A0E17; padding: 30px; text-align: center;">
                <img src="https://www.amdi.mx/projects/AMDI/images/62ccb83546527a47ccda9cbf_AMDI0.svg" alt="AMDI Logo" style="height: 50px; margin: 0 auto; display: block;">
            </div>
            
            <div style="padding: 40px 30px; line-height: 1.6;">
                <h2 style="color: #0A0E17; font-size: 20px; font-weight: 700; margin-top: 0;">¡Hola, {form_data.nombre}!</h2>
                <p>Muchas gracias por ponerte en contacto con nosotros.</p>
                <p>Hemos recibido tus datos y tu solicitud. Uno de nuestros diseñadores creativos revisará los detalles de tu proyecto y se pondrá en contacto contigo muy pronto para platicar a profundidad.</p>
                
                <div style="margin: 30px 0; padding: 20px; background-color: #f8fafc; border-left: 4px solid #0A0E17; border-radius: 4px;">
                    <h3 style="margin-top: 0; font-size: 14px; color: #0A0E17; text-transform: uppercase; letter-spacing: 0.5px;">Resumen de tu mensaje:</h3>
                    <p style="margin: 5px 0; font-size: 14px;"><strong>Proyecto:</strong> Diseño de interiores</p>
                    <p style="margin: 5px 0; font-size: 14px; font-style: italic; color: #475569;">"{form_data.mensaje}"</p>
                </div>
                
                <p>Mientras tanto, te invitamos a seguir descubriendo nuestro portafolio de proyectos residenciales y comerciales en nuestro sitio web.</p>
                
                <p style="margin-bottom: 0; margin-top: 40px;">Atentamente,<br><strong>El equipo creativo de AMDI</strong></p>
            </div>
            
            <div style="background-color: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
                Este correo fue enviado de manera automática por el sistema de AMDI.<br>
                © 2026 AMDI | Diseño de Interiores.
            </div>
            
        </div>
    </body>
    </html>
    """

    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="AMDI",
        from_name=from_name,
        from_email=from_email,
        to_email=form_data.email,
        subject=f"¡Hola {form_data.nombre}! Recibimos tu mensaje en AMDI",
        html_content=html_content,
        domain="amdi.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Correo de confirmación AMDI enviado a {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar confirmación AMDI a {form_data.email}: {str(e)}")
        return False


async def send_amdi_contact_notification_team(form_data):
    amdi_configured = bool(settings.AMDI_SMTP_HOST and settings.AMDI_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not amdi_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío de notificación AMDI al equipo para {form_data.email}")
        return True

    from_email = settings.AMDI_EMAILS_FROM_EMAIL if settings.AMDI_EMAILS_FROM_EMAIL else "contacto@amdi.mx"

    mensaje_formatted = form_data.mensaje.replace('\n', '<br>') if form_data.mensaje else 'Sin mensaje.'
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #1e293b; background-color: #f1f5f9; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            
            <div style="background-color: #0A0E17; padding: 25px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">
                    AMDI <span style="color: #80ED99;">Lead</span>
                </h1>
            </div>
            
            <div style="padding: 35px 30px;">
                <p style="font-size: 15px; margin-top: 0; margin-bottom: 25px; color: #475569;">
                    Se ha recibido una nueva solicitud de información en la página web de AMDI. Detalles del prospecto:
                </p>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 14px;">
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0E17; background-color: #f8fafc; width: 150px;">Nombre:</td>
                        <td style="padding: 10px; color: #1e293b;">{form_data.nombre} {form_data.apellido}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0E17; background-color: #f8fafc;">Email:</td>
                        <td style="padding: 10px; color: #1e293b;"><a href="mailto:{form_data.email}" style="color: #2EC4B6; text-decoration: none; font-weight: bold;">{form_data.email}</a></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0E17; background-color: #f8fafc;">Teléfono:</td>
                        <td style="padding: 10px; color: #1e293b;"><a href="tel:{form_data.telefono}" style="color: #1e293b; text-decoration: none; font-weight: bold;">{form_data.telefono}</a></td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold; color: #0A0E17; background-color: #f8fafc; vertical-align: top;">Mensaje:</td>
                        <td style="padding: 10px; color: #1e293b; line-height: 1.5; font-style: italic;">{mensaje_formatted}</td>
                    </tr>
                </table>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://wa.me/{form_data.telefono.replace(' ', '').replace('+', '').replace('-', '')}" style="background-color: #25D366; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-block;">
                        💬 Responder por WhatsApp
                    </a>
                </div>
            </div>
            
            <div style="background-color: #f8fafc; padding: 15px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #cbd5e1;">
                Mensaje automático de contacto enviado por el sistema de AMDI.
            </div>
            
        </div>
    </body>
    </html>
    """

    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="AMDI",
        from_name="AMDI Web",
        from_email=from_email,
        to_email="creativo@amdi.mx",
        subject=f"📬 Nuevo mensaje de contacto desde AMDI: {form_data.nombre} {form_data.apellido}",
        html_content=html_content,
        domain="amdi.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Notificación de contacto AMDI enviada al equipo para {form_data.nombre}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación de contacto AMDI al equipo: {str(e)}")
        return False


async def send_amdi_newsletter_welcome(subscriber_email: str):
    amdi_configured = bool(settings.AMDI_SMTP_HOST and settings.AMDI_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not amdi_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío de bienvenida a Newsletter AMDI para {subscriber_email}")
        return True

    from_email = settings.AMDI_EMAILS_FROM_EMAIL if settings.AMDI_EMAILS_FROM_EMAIL else "contacto@amdi.mx"
    from_name = settings.AMDI_EMAILS_FROM_NAME if settings.AMDI_EMAILS_FROM_NAME else "AMDI | Boletín"

    html_content = f"""
    <html>
    <body style="font-family: 'Montserrat', Arial, sans-serif; color: #1e293b; background-color: #fafafa; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            
            <div style="background-color: #0A0E17; padding: 30px; text-align: center;">
                <img src="https://www.amdi.mx/projects/AMDI/images/62ccb83546527a47ccda9cbf_AMDI0.svg" alt="AMDI Logo" style="height: 50px; margin: 0 auto; display: block;">
            </div>
            
            <div style="padding: 40px 30px; line-height: 1.6;">
                <h2 style="color: #0A0E17; font-size: 18px; font-weight: 700; margin-top: 0;">¡Hola!</h2>
                <p>Te damos la más cordial bienvenida al boletín de noticias de <strong>AMDI | Diseño de Interiores</strong>.</p>
                <p>A partir de ahora, recibirás contenido exclusivo sobre las últimas tendencias en diseño, ideas inspiradoras para transformar tus espacios, lanzamientos de nuevos proyectos y consejos de decoración directo a tu bandeja de entrada.</p>
                <p>¡Gracias por ser parte de nuestra comunidad!</p>
                
                <p style="margin-bottom: 0; margin-top: 40px;">Atentamente,<br><strong>El equipo de AMDI</strong></p>
            </div>
            
            <div style="background-color: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
                Recibes este correo porque te suscribiste a nuestro boletín en el sitio web de AMDI.<br>
                © 2026 AMDI | Diseño de Interiores.
            </div>
            
        </div>
    </body>
    </html>
    """

    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="AMDI",
        from_name=from_name,
        from_email=from_email,
        to_email=subscriber_email,
        subject="¡Bienvenido al Newsletter de AMDI!",
        html_content=html_content,
        domain="amdi.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Correo de bienvenida a Newsletter AMDI enviado a {subscriber_email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de bienvenida AMDI a {subscriber_email}: {str(e)}")
        return False


async def send_amdi_newsletter_notification_team(subscriber_email: str):
    amdi_configured = bool(settings.AMDI_SMTP_HOST and settings.AMDI_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not amdi_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío de notificación de boletín AMDI para {subscriber_email}")
        return True

    from_email = settings.AMDI_EMAILS_FROM_EMAIL if settings.AMDI_EMAILS_FROM_EMAIL else "contacto@amdi.mx"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #1e293b; background-color: #f1f5f9; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            
            <div style="background-color: #0A0E17; padding: 25px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">
                    AMDI <span style="color: #80ED99;">Newsletter</span>
                </h1>
            </div>
            
            <div style="padding: 35px 30px;">
                <p style="font-size: 15px; margin-top: 0; margin-bottom: 20px; color: #475569;">
                    Un nuevo usuario se ha registrado en el boletín (Newsletter) de la página web de AMDI.
                </p>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 14px;">
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px; font-weight: bold; color: #0A0E17; background-color: #f8fafc; width: 150px;">Email Registrado:</td>
                        <td style="padding: 10px; color: #1e293b;"><a href="mailto:{subscriber_email}" style="color: #2EC4B6; text-decoration: none; font-weight: bold;">{subscriber_email}</a></td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #f8fafc; padding: 15px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #cbd5e1;">
                Notificación automática enviada por el sistema de AMDI.
            </div>
            
        </div>
    </body>
    </html>
    """

    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="AMDI",
        from_name="AMDI Web",
        from_email=from_email,
        to_email="creativo@amdi.mx",
        subject=f"📰 Nuevo suscriptor al boletín de AMDI",
        html_content=html_content,
        domain="amdi.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        logger.info(f"Notificación de nuevo suscriptor AMDI enviada al equipo para {subscriber_email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar notificación de nuevo suscriptor AMDI al equipo: {str(e)}")
        return False


async def send_chilechillon_order_customer(payer_name: str, payer_email: str, order_details: str, total: float):
    chile_configured = bool(settings.CHILECHILLON_SMTP_HOST and settings.CHILECHILLON_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not chile_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a cliente Chile Chillón {payer_email}")
        return True

    from_email = settings.CHILECHILLON_EMAILS_FROM_EMAIL if settings.CHILECHILLON_EMAILS_FROM_EMAIL else "hola@elchilechillon.com.mx"
    from_name = settings.CHILECHILLON_EMAILS_FROM_NAME if settings.CHILECHILLON_EMAILS_FROM_NAME else "Chile Chillón"

    html_content = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9; background-color: #080505; margin: 0; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #0d0707; border-radius: 24px; overflow: hidden; box-shadow: 0 10px 30px rgba(229, 9, 20, 0.1); border: 1px solid rgba(229, 9, 20, 0.2);">
            
            <div style="background-color: #080505; padding: 35px 20px; text-align: center; border-bottom: 4px solid #E50914;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; letter-spacing: 2px; font-weight: 900;">CHILE <span style="color: #E50914;">CHILLÓN</span></h1>
                <p style="color: #FF6A00; margin: 5px 0 0 0; font-size: 10px; text-transform: uppercase; tracking-widest: 2px; font-weight: bold;">Tu sazón en su máxima potencia</p>
            </div>

            <div style="padding: 40px 30px; background-color: #0d0707;">
                <h2 style="color: #ffffff; font-size: 20px; margin-top: 0; margin-bottom: 20px; font-weight: 700; border-left: 4px solid #E50914; padding-left: 12px;">¡Pedido Recibido, {payer_name}!</h2>
                <p style="line-height: 1.6; font-size: 14px; color: #cbd5e1; margin-bottom: 25px;">
                    Hemos procesado tu pago correctamente. Nuestro equipo ya está empaquetando tus salsas picantes premium para enviarlas lo antes posible.
                </p>

                <h3 style="color: #ffffff; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px;">Detalles de tu compra</h3>
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255,255,255,0.05); padding: 20px; border-radius: 16px; margin-bottom: 30px; font-size: 14px; color: #e2e8f0; line-height: 1.6;">
                    {order_details}
                    <p style="margin-top: 15px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 15px; font-size: 16px; font-weight: bold; color: #FF6A00; text-align: right;">Total pagado: ${total} MXN</p>
                </div>

                <p style="line-height: 1.6; font-size: 13px; color: #94a3b8; text-align: center; margin-top: 30px;">
                    ¿Tienes dudas? Escríbenos directamente a <a href="mailto:hola@elchilechillon.com.mx" style="color: #FF6A00; text-decoration: none; font-weight: bold;">hola@elchilechillon.com.mx</a>.
                </p>
            </div>
            
            <div style="background-color: #080505; padding: 25px 20px; text-align: center; font-size: 11px; color: #64748b; border-top: 1px solid rgba(255,255,255,0.05);">
                <p style="margin: 0 0 10px 0;">&copy; 2026 Chile Chillón. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="CHILECHILLON",
        from_name=from_name,
        from_email=from_email,
        to_email=payer_email,
        subject=f"¡Tu sazón está en camino, {payer_name}! 🌶️🔥",
        html_content=html_content,
        domain="elchilechillon.com.mx"
    )

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de orden a cliente Chile Chillón: {str(e)}")
        return False


async def send_chilechillon_order_team(payer_name: str, payer_email: str, payer_phone: str, address_str: str, order_details: str, total: float):
    chile_configured = bool(settings.CHILECHILLON_SMTP_HOST and settings.CHILECHILLON_SMTP_USER)
    global_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)

    if not chile_configured and not global_configured:
        logger.warning(f"SMTP no configurado. Simulando envío a equipo Chile Chillón")
        return True

    from_email = settings.CHILECHILLON_EMAILS_FROM_EMAIL if settings.CHILECHILLON_EMAILS_FROM_EMAIL else "hola@elchilechillon.com.mx"
    to_email = settings.CHILECHILLON_EMAILS_FROM_EMAIL if settings.CHILECHILLON_EMAILS_FROM_EMAIL else "hola@elchilechillon.com.mx"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; background-color: #f7f7f7; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; border: 1px solid #ddd;">
            <h2 style="color: #E50914; margin-top: 0;">¡Nuevo Pedido Pagado en la Web!</h2>
            <p>Se ha recibido y aprobado el pago de una compra en la tienda de Chile Chillón.</p>
            
            <h3 style="border-bottom: 2px solid #f0f0f0; padding-bottom: 5px;">Datos del Comprador</h3>
            <ul style="list-style: none; padding: 0; line-height: 1.6;">
                <li><strong>Nombre:</strong> {payer_name}</li>
                <li><strong>Email:</strong> {payer_email}</li>
                <li><strong>Teléfono:</strong> {payer_phone}</li>
                <li><strong>Dirección de Envío:</strong> {address_str}</li>
            </ul>
            
            <h3 style="border-bottom: 2px solid #f0f0f0; padding-bottom: 5px; margin-top: 25px;">Detalles de los Productos</h3>
            <div style="background-color: #fafafa; padding: 15px; border-radius: 6px; border: 1px solid #eee;">
                {order_details}
                <p style="margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 10px; font-size: 16px; font-weight: bold; color: #E50914;">Total: ${total} MXN</p>
            </div>
        </div>
    </body>
    </html>
    """
    message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
        project_prefix="CHILECHILLON",
        from_name="Chile Chillón Web",
        from_email=from_email,
        to_email=to_email,
        subject=f"🔥 NUEVA COMPRA WEB: {payer_name} - ${total} MXN",
        html_content=html_content,
        domain="elchilechillon.com.mx"
    )
    del message['Reply-To']
    message['Reply-To'] = payer_email

    try:
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de orden al equipo Chile Chillón: {str(e)}")
        return False





