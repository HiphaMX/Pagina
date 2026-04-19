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
