from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.mailer import (
    send_grupogari_confirmation_email,
    send_grupogari_notification_team
)

router = APIRouter()

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

@router.post("/grupogari")
async def submit_grupogari_form(form_data: GrupoGariForm):
    customer_email_sent = await send_grupogari_confirmation_email(form_data)
    team_email_sent = await send_grupogari_notification_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}
