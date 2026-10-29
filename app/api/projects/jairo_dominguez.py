import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import settings
from app.core.security import verify_recaptcha
from app.core.mailer import (
    send_jairodominguez_confirmation_email,
    send_jairodominguez_notification_team
)

router = APIRouter()
logger = logging.getLogger(__name__)


class JairoDominguezForm(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    mensaje: Optional[str] = ""
    honeypot: Optional[str] = None
    recaptcha_token: Optional[str] = None


@router.post("/jairo-dominguez")
@router.post("")
async def submit_jairo_dominguez_form(form_data: JairoDominguezForm):
    # Detección de Bots vía Honeypot
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for Dr. Jairo Domínguez (email: {form_data.email}).")
        return {"message": "Solicitud recibida correctamente"}

    # Validación reCAPTCHA v3 si el token está presente
    if form_data.recaptcha_token and form_data.recaptcha_token.strip():
        secret_key = settings.JAIRODOMINGUEZ_RECAPTCHA_SECRET_KEY or settings.HIPHA_RECAPTCHA_SECRET_KEY
        is_human = await verify_recaptcha(form_data.recaptcha_token, secret_key, "JairoDominguez")
        if not is_human:
            logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for Dr. Jairo Domínguez (email: {form_data.email}).")
            return {"message": "Solicitud recibida correctamente"}

    # 1. Enviar correo de notificación directo al Dr. Jairo Domínguez y copia a Hipha
    team_email_sent = await send_jairodominguez_notification_team(form_data)

    # 2. Enviar correo de confirmación al paciente
    customer_email_sent = await send_jairodominguez_confirmation_email(form_data)

    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos de notificación")

    return {"message": "Solicitud recibida correctamente"}
