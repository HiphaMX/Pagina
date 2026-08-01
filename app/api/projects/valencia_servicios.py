import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings
from app.core.security import verify_recaptcha
from app.core.mailer import send_valencia_servicios_notification_team

router = APIRouter()
logger = logging.getLogger(__name__)

class ValenciaServiciosForm(BaseModel):
    nombre_completo: str
    telefono: str
    servicio_requerido: str
    direccion: str
    horario_preferido: str
    honeypot: Optional[str] = None
    recaptcha_token: Optional[str] = None

@router.post("/valencia-servicios")
async def submit_valencia_servicios_form(form_data: ValenciaServiciosForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for Valencia Servicios (nombre: {form_data.nombre_completo}).")
        return {"message": "Formulario recibido correctamente"}

    # Validar reCAPTCHA v3 de forma estricta (no opcional)
    if not form_data.recaptcha_token or not form_data.recaptcha_token.strip():
        logger.warning(f"[SPAM DETECTED] Missing or empty reCAPTCHA token for Valencia Servicios (nombre: {form_data.nombre_completo}).")
        return {"message": "Formulario recibido correctamente"}

    secret_key = settings.VALENCIA_RECAPTCHA_SECRET_KEY or settings.HIPHA_RECAPTCHA_SECRET_KEY
    is_human = await verify_recaptcha(form_data.recaptcha_token, secret_key, "ValenciaServicios")
    if not is_human:
        logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for Valencia Servicios (nombre: {form_data.nombre_completo}).")
        return {"message": "Formulario recibido correctamente"}

    # Por ahora omitimos el envío de correo de notificación del lead por petición del usuario
    # team_email_sent = await send_valencia_servicios_notification_team(form_data)
    
    # if not team_email_sent:
    #     raise HTTPException(status_code=500, detail="Error al enviar correo de notificación al equipo")
        
    return {"message": "Formulario recibido correctamente"}

