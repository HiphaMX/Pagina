from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.mailer import send_valencia_servicios_notification_team

router = APIRouter()

class ValenciaServiciosForm(BaseModel):
    nombre_completo: str
    telefono: str
    servicio_requerido: str
    direccion: str
    horario_preferido: str

@router.post("/valencia-servicios")
async def submit_valencia_servicios_form(form_data: ValenciaServiciosForm):
    team_email_sent = await send_valencia_servicios_notification_team(form_data)
    
    if not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correo de notificación al equipo")
        
    return {"message": "Formulario recibido correctamente"}
