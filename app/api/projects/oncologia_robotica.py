import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import settings
from app.core.security import verify_recaptcha
from app.core.mailer import (
    send_oncologiarobotica_confirmation_email,
    send_oncologiarobotica_notification_team
)

router = APIRouter()
logger = logging.getLogger(__name__)


class OncologiaRoboticaForm(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    tipo_procedimiento: Optional[str] = "Valoración General"
    mensaje: Optional[str] = ""
    honeypot: Optional[str] = None
    recaptcha_token: Optional[str] = None


@router.post("/oncologia-robotica")
@router.post("")
async def submit_oncologia_robotica_form(form_data: OncologiaRoboticaForm):
    # Detección de Bots vía Honeypot
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for Oncología Robótica (email: {form_data.email}).")
        return {"message": "Solicitud recibida correctamente"}

    # Validación reCAPTCHA v3 si el token está presente
    if form_data.recaptcha_token and form_data.recaptcha_token.strip():
        secret_key = settings.ONCOLOGIAROBOTICA_RECAPTCHA_SECRET_KEY or settings.HIPHA_RECAPTCHA_SECRET_KEY
        is_human = await verify_recaptcha(form_data.recaptcha_token, secret_key, "OncologiaRobotica")
        if not is_human:
            logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for Oncología Robótica (email: {form_data.email}).")
            return {"message": "Solicitud recibida correctamente"}

    # Enviar correo de confirmación al paciente
    customer_email_sent = await send_oncologiarobotica_confirmation_email(form_data)

    # Enviar correo de notificación al equipo médico
    team_email_sent = await send_oncologiarobotica_notification_team(form_data)

    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos de notificación")

    return {"message": "Solicitud recibida correctamente"}
