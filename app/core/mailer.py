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
