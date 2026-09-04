import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import settings
from app.core.security import verify_recaptcha
from app.core.mailer import (
    send_letrerama_quote_confirmation_customer,
    send_letrerama_quote_notification_team
)

router = APIRouter()
logger = logging.getLogger(__name__)

class LetreramaQuoteForm(BaseModel):
    nombre: str
    telefono: Optional[str] = ""
    email: EmailStr
    empresa: Optional[str] = ""
    tiene_vector: str  # "SI" / "NO"
    logo_base64: Optional[str] = None
    logo_filename: Optional[str] = None
    tecnica: str
    medida_ancho: float
    medida_alto: float
    medida_canto: Optional[float] = None
    iluminacion: str
    material: str
    altura_instalacion: float
    direccion_instalacion: str
    privacidad: bool
    honeypot: Optional[str] = None
    recaptcha_token: Optional[str] = None

@router.post("/letrerama")
async def submit_letrerama_quote(form_data: LetreramaQuoteForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for Letrerama (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    # Validar reCAPTCHA v3 de forma estricta (no opcional)
    if not form_data.recaptcha_token or not form_data.recaptcha_token.strip():
        logger.warning(f"[SPAM DETECTED] Missing or empty reCAPTCHA token for Letrerama (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    secret_key = settings.LETRERAMA_RECAPTCHA_SECRET_KEY or settings.HIPHA_RECAPTCHA_SECRET_KEY
    is_human = await verify_recaptcha(form_data.recaptcha_token, secret_key, "Letrerama")
    if not is_human:
        logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for Letrerama (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    # Log received form data details in console
    logger.info(f"[Letrerama Backend] Cotización recibida de: {form_data.nombre} ({form_data.email})")
    logger.info(f"  Proyecto: {form_data.tecnica} | Medidas: {form_data.medida_ancho}x{form_data.medida_alto} cm")
    
    # Enviar correos de confirmación al cliente y notificación al equipo
    customer_email_sent = await send_letrerama_quote_confirmation_customer(form_data)
    team_email_sent = await send_letrerama_quote_notification_team(form_data)

    if not customer_email_sent and not team_email_sent:
        logger.error(f"Fallo crítico al despachar correos de cotización para {form_data.email}")
        raise HTTPException(status_code=500, detail="Error al enviar correos de confirmación")

    return {"message": "Formulario recibido correctamente"}

