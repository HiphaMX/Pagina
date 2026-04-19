from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Dict, Any
import logging

from app.core.webflow_client import webflow_client
from app.core.mailer import send_lead_followup_email

router = APIRouter()
logger = logging.getLogger(__name__)

class BlogPost(BaseModel):
    title: str
    slug: str
    body: str
    collection_id: str
    is_draft: bool = False

@router.post("/blog")
async def create_blog_post(post: BlogPost):
    """
    Inyecta un artículo directamente al CMS de Webflow.
    """
    field_data = {
        "name": post.title,
        "slug": post.slug,
        "post-body": post.body  # Reemplazar con el field_id real del HTML del artículo en tu CMS
    }
    
    try:
        response = await webflow_client.create_item(
            collection_id=post.collection_id,
            field_data=field_data,
            is_draft=post.is_draft
        )
        return {"message": "Blog post published to Webflow successfully", "data": response}
    except Exception as e:
        logger.error(f"Error creating Webflow CMS item: {str(e)}")
        raise HTTPException(status_code=400, detail="Fallo al publicar en Webflow")

@router.post("/webhook/lead")
async def webflow_lead_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Recibe un webhook de Webflow (cuando un cliente llena un formulario)
    y dispara un correo de seguimiento en background.
    """
    try:
        payload = await request.json()
        logger.info(f"Webhook recibido de Webflow: {payload}")
        
        # Los webhooks de Submission en Webflow traen los campos dentro de 'data' -> 'fields' o directo
        data = payload.get("data", payload)
        
        # Nombres de campos dependen de cómo los nombraste en Webflow
        lead_name = data.get("name") or data.get("Name") or "Prospecto de HiphaMX"
        lead_email = data.get("email") or data.get("Email")
        
        if lead_email:
            background_tasks.add_task(send_lead_followup_email, lead_name, lead_email)
            return {"status": "ok", "message": "Email de seguimiento agendado en background."}
        else:
            return {"status": "info", "message": "Webhook válido, pero no se detectó el campo 'Email'."}
            
    except Exception as e:
        logger.error(f"Error procesando el webhook: {str(e)}")
        raise HTTPException(status_code=400, detail="Estructura inprocesable")
