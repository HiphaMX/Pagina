from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.mailer import (
    send_whiteclean_confirmation_email,
    send_whiteclean_notification_team
)

router = APIRouter()

class WhiteCleanForm(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    servicio: str
    ubicacion: str
    mensaje: Optional[str] = ""

@router.post("/whiteclean")
async def submit_whiteclean_form(form_data: WhiteCleanForm):
    # Enviar correo de confirmación al prospecto
    customer_email_sent = await send_whiteclean_confirmation_email(form_data)
    
    # Enviar aviso con los detalles de la solicitud al equipo
    team_email_sent = await send_whiteclean_notification_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}
