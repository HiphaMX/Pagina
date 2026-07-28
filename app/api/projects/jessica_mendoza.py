import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.mailer import (
    send_jessica_mendoza_confirmation_email,
    send_jessica_mendoza_notification_team
)

router = APIRouter()
logger = logging.getLogger(__name__)

class JessicaMendozaForm(BaseModel):
    nombre: str
    apellido: Optional[str] = ""
    email: EmailStr
    telefono: str
    intencion: str
    propiedad: str
    mensaje: Optional[str] = ""
    honeypot: Optional[str] = None

@router.post("/jessica-mendoza")
async def submit_jessica_mendoza_form(form_data: JessicaMendozaForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for Jessica Mendoza (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    customer_email_sent = await send_jessica_mendoza_confirmation_email(form_data)
    team_email_sent = await send_jessica_mendoza_notification_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}
