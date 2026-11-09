import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import settings
from app.core.security import verify_recaptcha
from app.core.mailer import (
    send_ieer_notification_team,
    send_ieer_confirmation_email
)

router = APIRouter()
logger = logging.getLogger(__name__)

class IEERContactForm(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    sector: Optional[str] = ""
    ubicacion: Optional[str] = ""
    mensaje: Optional[str] = ""
    honeypot: Optional[str] = None
    recaptcha_token: Optional[str] = None

@router.post("/ieer")
async def submit_ieer_contact_form(form_data: IEERContactForm):
    """
    Endpoint para procesar solicitudes de análisis técnico y cotización de micro-redes de IEER.
    """
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for IEER (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    # Validar reCAPTCHA v3 si se proporciona el token o clave configurada
    if form_data.recaptcha_token and form_data.recaptcha_token.strip():
        secret_key = settings.IEER_RECAPTCHA_SECRET_KEY or settings.HIPHA_RECAPTCHA_SECRET_KEY
        if secret_key:
            is_human = await verify_recaptcha(form_data.recaptcha_token, secret_key, "IEER")
            if not is_human:
                logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for IEER (email: {form_data.email}).")
                return {"message": "Formulario recibido correctamente"}

    team_email_sent = await send_ieer_notification_team(form_data)
    customer_email_sent = await send_ieer_confirmation_email(form_data)

    if not team_email_sent and not customer_email_sent:
        logger.warning(f"No fue posible enviar correos para IEER ({form_data.email}), pero la solicitud se registró en log.")

    return {
        "status": "success",
        "message": "Solicitud de consulta técnica recibida correctamente. Un ingeniero de IEER te contactará a la brevedad."
    }
