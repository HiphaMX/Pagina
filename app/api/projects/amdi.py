import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import settings
from app.core.security import verify_recaptcha
from app.core.mailer import (
    send_amdi_contact_confirmation_email,
    send_amdi_contact_notification_team,
    send_amdi_newsletter_welcome,
    send_amdi_newsletter_notification_team
)

router = APIRouter()
logger = logging.getLogger(__name__)

class AMDIContactoForm(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    mensaje: Optional[str] = ""
    honeypot: Optional[str] = None
    recaptcha_token: Optional[str] = None

class AMDINewsletterForm(BaseModel):
    nombre: str
    email: EmailStr
    honeypot: Optional[str] = None
    recaptcha_token: Optional[str] = None



@router.post("/amdi/contacto")
async def submit_amdi_contacto_form(form_data: AMDIContactoForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for AMDI contact form (email: {form_data.email}).")
        return {"message": "Formulario de contacto recibido correctamente"}

    # Validar reCAPTCHA v3 de forma estricta (no opcional)
    if not form_data.recaptcha_token or not form_data.recaptcha_token.strip():
        logger.warning(f"[SPAM DETECTED] Missing or empty reCAPTCHA token for AMDI contact form (email: {form_data.email}).")
        return {"message": "Formulario de contacto recibido correctamente"}

    is_human = await verify_recaptcha(form_data.recaptcha_token, settings.AMDI_RECAPTCHA_SECRET_KEY, "AMDI")
    if not is_human:
        logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for AMDI contact form (email: {form_data.email}).")
        return {"message": "Formulario de contacto recibido correctamente"}

    # Enviar correo de confirmación al prospecto
    customer_email_sent = await send_amdi_contact_confirmation_email(form_data)
    
    # Enviar aviso con los detalles de la solicitud al equipo
    team_email_sent = await send_amdi_contact_notification_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos de contacto")
        
    return {"message": "Formulario de contacto recibido correctamente"}

@router.post("/amdi/newsletter")
async def submit_amdi_newsletter_form(form_data: AMDINewsletterForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for AMDI newsletter form (email: {form_data.email}).")
        return {"message": "Suscripción a newsletter recibida correctamente"}

    # Validar reCAPTCHA v3 de forma estricta (no opcional)
    if not form_data.recaptcha_token or not form_data.recaptcha_token.strip():
        logger.warning(f"[SPAM DETECTED] Missing or empty reCAPTCHA token for AMDI newsletter form (email: {form_data.email}).")
        return {"message": "Suscripción a newsletter recibida correctamente"}

    is_human = await verify_recaptcha(form_data.recaptcha_token, settings.AMDI_RECAPTCHA_SECRET_KEY, "AMDI")
    if not is_human:
        logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for AMDI newsletter form (email: {form_data.email}).")
        return {"message": "Suscripción a newsletter recibida correctamente"}

    # Enviar correo de bienvenida al boletín
    welcome_email_sent = await send_amdi_newsletter_welcome(form_data.email)
    
    # Enviar aviso de nuevo suscriptor al equipo
    team_email_sent = await send_amdi_newsletter_notification_team(form_data.email)
    
    if not welcome_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos de boletín")
        
    return {"message": "Suscripción a newsletter recibida correctamente"}
