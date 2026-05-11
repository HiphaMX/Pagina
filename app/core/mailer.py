import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

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
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>¡Hola {lead_name}!</h2>
        <p>Hemos recibido tus datos con éxito. En breve, uno de nuestros creativos o estrategas se pondrá en contacto contigo para platicar sobre cómo podemos potenciar el crecimiento de tu marca.</p>
        <p>Mientras tanto, puedes explorar nuestro ecosistema de soluciones en nuestra web.</p>
        <br>
        <p>Atentamente,<br><strong>El equipo de HiphaMX</strong></p>
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
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Nuevo contacto desde la web HiphaMX</h2>
        <p><strong>Nombre:</strong> {form_data.nombre}</p>
        <p><strong>Email:</strong> {form_data.email}</p>
        <p><strong>Teléfono:</strong> {form_data.telefono}</p>
        <p><strong>Mensaje:</strong></p>
        <p>{form_data.mensaje}</p>
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
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>¡Gracias por suscribirte!</h2>
        <p>A partir de ahora recibirás nuestros mejores insights y recursos sobre marketing y estrategia digital.</p>
        <br>
        <p>Atentamente,<br><strong>El equipo de HiphaMX</strong></p>
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
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #06b6d4;">¡Firma de Contrato Confirmada, {form_data.nombre}!</h2>
            <p>Hemos recibido correctamente tu aceptación de los Términos y Condiciones para comenzar a trabajar juntos.</p>
            
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
                <h3 style="margin-top: 0; color: #0f172a;">Detalles del Acuerdo:</h3>
                <p>{mensaje_formatted}</p>
            </div>
            
            <h3 style="color: #0f172a;">Copia de los Términos y Condiciones Aceptados:</h3>
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0; font-size: 14px;">
                
        <h2>1. Servicios Hipha</h2>
        <p>La definición del concepto “Tu departamento externo de marketing” se refiere a los servicios brindados por un equipo interdisciplinario de marketing y creatividad, Hipha se convierte en un socio y consultor estratégico, que en algunos casos cuando no existe un departamento interno y el cliente contrata también los servicios de ejecución, bajo ninguna circunstancia se deberá interpretar que el personal de Hipha son subordinados operativos del cliente. Hipha actúa como un proveedor de servicios profesionales con autonomía técnica, por lo que no existe relación laboral ni exclusividad, a menos que se pacte por escrito.</p>

        <h2>2. Límites de la disponibilidad y comunicación</h2>
        <p>Es responsabilidad del cliente designar a una sola persona con poder de decisión para evitar instrucciones contradictorias de diferentes socios del cliente, este líder de proyecto será la única vía para canalizar y dar seguimiento a las solicitudes de diseño y estrategia necesarias. La ventana de horario para programar reuniones virtuales son de lunes a viernes de 9:00 am. - 12:00 pm, nuestro equipo trabaja de manera remota en distintas ubicaciones, por lo que las reuniones presenciales son poco frecuentes, cuando son indispensables serán previamente acordadas y estarán sujetas a disponibilidad del equipo de Hipha.</p>

        <h2>3. Solicitudes de materiales</h2>
        <p>Todas las solicitudes de piezas gráficas y materiales deberán realizarse por medio del link de cliente proporcionado por Hipha o mediante las reuniones de seguimiento con el líder de proyecto, la esencia de Hipha es dar acceso a más clientes a servicios de marketing y diseño especializados, para brindar el mejor servicio se establecen como mínimo 72 hrs. para iniciar a procesar las nuevas solicitudes.</p>
        
        <p>Gracias a nuestra amplia experiencia, el equipo de Hipha tiene acceso a proveeduría especializada de servicios digitales, de impresión y publicidad, pero esto no implica que se tengan que compartir contactos ni acuerdos comerciales con sus clientes, contamos con la posibilidad de enviar materiales a impresión directo con los proveedores del cliente, sin que esto implique realizar pagos a terceros, supervisar instalaciones, gestionar paqueterías, recolecciones o entregas, esto deberá ser ejecutado por personal interno del cliente.</p>

        <h2>4. Responsabilidades del cliente</h2>
        <p>El equipo de Hipha podrá iniciar un proyecto siempre que se realice el brief inicial, así como logotipos, manual de identidad en caso de existir, tipografías y cualquier material que pueda ser de utilidad (fotografías, videos, referencias de diseños anteriores, vectores, etc.) El retraso del cliente no posterga las fechas de pago ni las fechas de entrega finales.</p>
        
        <p><strong>Protocolo de Seguridad:</strong> El cliente es responsable de mantener la seguridad de sus accesos, Hipha no se hace responsable por hackeos o bloqueos derivados de acciones del cliente o de terceros ajenos a la agencia, se proporcionarán todos los accesos y contraseñas, en caso de finalización de contrato, es responsabilidad del cliente revocar los accesos de la agencia en un plazo máximo 24 hrs.</p>

        <h2>5. Propiedad intelectual y accesos</h2>
        <p>Los entregables finales pagados al 100% son propiedad del cliente, entiéndase por diseños publicados en redes sociales, sitio web, fotografías de producto o instalaciones, por mencionar algunos ejemplos, son propiedad de Hipha las metodologías, procesos internos, flujos de trabajo, estrategias preexistentes, archivos fuente y cualquier desarrollo propio realizado para brindar soporte al cliente.</p>
        
        <p>Se debe declarar que las cuentas de Ad Manager, Meta Business Suite y Google Analytics son propiedad del cliente y se entregan al líder de proyecto mediante un correo electrónico, la agencia accede como socio externo (Partner).</p>
        
        <p>Hipha se reserva el derecho de utilizar capturas de pantalla, métricas (anonimizadas si es necesario) y muestras del trabajo realizado para su propio portafolio, redes sociales y casos de estudio, a menos que exista un acuerdo de confidencialidad (NDA) que lo prohíba explícitamente.</p>

        <h2>6. Cláusula de Rescisión</h2>
        <p>Ambas partes pueden terminar la relación con un aviso previo de 30 días naturales, Esto da flujo de caja para reemplazar la cuenta y al cliente tiempo para la transición. En caso de impago, la agencia se reserva el derecho de pausar campañas o retirar servicios hasta que se liquide el adeudo y finiquite la relación comercial.</p>

            </div>
            
            <p style="margin-top: 30px;">Estamos muy emocionados de comenzar este proyecto contigo.</p>
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
        logger.info(f"Correo de contrato enviado exitosamente a {form_data.email}")
        return True
    except Exception as e:
        logger.error(f"Fallo al enviar correo de contrato a {form_data.email}: {str(e)}")
        return False
