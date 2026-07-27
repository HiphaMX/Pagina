import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.mailer import (
    send_grupogari_confirmation_email,
    send_grupogari_notification_team
)

router = APIRouter()
logger = logging.getLogger(__name__)

class GrupoGariForm(BaseModel):
    nombre: str
    apellido: Optional[str] = ""
    email: EmailStr
    telefono: str
    rol: str
    empleados: str
    industria: str
    servicio: str
    mensaje: Optional[str] = ""
    honeypot: Optional[str] = None

@router.post("/grupogari")
async def submit_grupogari_form(form_data: GrupoGariForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for Grupo Gari (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    customer_email_sent = await send_grupogari_confirmation_email(form_data)
    team_email_sent = await send_grupogari_notification_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}

