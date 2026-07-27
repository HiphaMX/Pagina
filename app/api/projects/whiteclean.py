import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
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

@router.post("/whiteclean")
async def submit_whiteclean_form(form_data: WhiteCleanForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for WhiteClean (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    # Enviar correo de confirmación al prospecto
    customer_email_sent = await send_whiteclean_confirmation_email(form_data)
    
    # Enviar aviso con los detalles de la solicitud al equipo
    team_email_sent = await send_whiteclean_notification_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}

