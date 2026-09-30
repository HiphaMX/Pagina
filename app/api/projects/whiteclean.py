import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import settings
from app.core.security import verify_recaptcha
from app.core.mailer import (
    send_whiteclean_confirmation_email,
    send_whiteclean_notification_team
)

router = APIRouter()
logger = logging.getLogger(__name__)

class WhiteCleanForm(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    servicio: str
    ubicacion: str
    mensaje: Optional[str] = ""
    honeypot: Optional[str] = None
    recaptcha_token: Optional[str] = None

async def dispatch_whiteclean_emails(form_data: WhiteCleanForm):
    """
    Despacha los correos de confirmación al cliente y aviso al equipo
    en paralelo y en segundo plano sin demorar la respuesta de la web.
    """
    try:
        await asyncio.gather(
            send_whiteclean_confirmation_email(form_data),
            send_whiteclean_notification_team(form_data),
            return_exceptions=True
        )
        logger.info(f"Correos de WhiteClean despachados en background con éxito para {form_data.email}")
    except Exception as e:
        logger.error(f"Error despachando correos en background para WhiteClean ({form_data.email}): {e}")

@router.post("/whiteclean")
async def submit_whiteclean_form(form_data: WhiteCleanForm, background_tasks: BackgroundTasks):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for WhiteClean (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    # Validar reCAPTCHA v3 si el token está presente
    if form_data.recaptcha_token and form_data.recaptcha_token.strip():
        secret_key = settings.WHITECLEAN_RECAPTCHA_SECRET_KEY or settings.HIPHA_RECAPTCHA_SECRET_KEY
        is_human = await verify_recaptcha(form_data.recaptcha_token, secret_key, "WhiteClean")
        if not is_human:
            logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for WhiteClean (email: {form_data.email}).")
            return {"message": "Formulario recibido correctamente"}
    else:
        logger.info(f"[SECURITY INFO] No reCAPTCHA token provided for WhiteClean (email: {form_data.email}). Proceeding with submission.")

    # Enviar correos en background de forma asíncrona e inmediata
    background_tasks.add_task(dispatch_whiteclean_emails, form_data)
        
    return {"message": "Formulario recibido correctamente"}

