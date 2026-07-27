import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
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

@router.post("/valencia-servicios")
async def submit_valencia_servicios_form(form_data: ValenciaServiciosForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for Valencia Servicios (nombre: {form_data.nombre_completo}).")
        return {"message": "Formulario recibido correctamente"}

    # Por ahora omitimos el envío de correo de notificación del lead por petición del usuario
    # team_email_sent = await send_valencia_servicios_notification_team(form_data)
    
    # if not team_email_sent:
    #     raise HTTPException(status_code=500, detail="Error al enviar correo de notificación al equipo")
        
    return {"message": "Formulario recibido correctamente"}

