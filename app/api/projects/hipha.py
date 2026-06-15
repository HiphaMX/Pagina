from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.mailer import (
    send_contract_followup_email,
    send_lead_followup_email,
    send_lead_notification_to_team,
    send_newsletter_welcome,
    send_newsletter_notification_to_team
)

router = APIRouter()

class ContactForm(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    mensaje: str = ""
    firma: Optional[str] = None
    fecha: Optional[str] = None
    fecha_pago: Optional[str] = None
    proyecto: Optional[str] = None
    forma_pago: Optional[str] = None
    plan_contratado: Optional[str] = None

class NewsletterForm(BaseModel):
    email: EmailStr

@router.post("/submit")
async def submit_contact_form(form_data: ContactForm):
    is_contract = form_data.mensaje.startswith("ACEPTACIÓN DE CONTRATO VÍA WEB")
    
    # Enviar correo al lead
    if is_contract:
        lead_email_sent = await send_contract_followup_email(form_data)
    else:
        lead_email_sent = await send_lead_followup_email(form_data.nombre, form_data.email)
    
    # Enviar correo al equipo de HiphaMX
    team_email_sent = await send_lead_notification_to_team(form_data)
    
    if not lead_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}

@router.post("/newsletter")
async def submit_newsletter_form(form_data: NewsletterForm):
    # Enviar correo de bienvenida al suscriptor
    subscriber_email_sent = await send_newsletter_welcome(form_data.email)
    
    # Enviar notificación al equipo
    team_email_sent = await send_newsletter_notification_to_team(form_data.email)
    
    if not subscriber_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al procesar suscripción")
        
    return {"message": "Suscripción exitosa"}
