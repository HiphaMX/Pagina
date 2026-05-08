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
