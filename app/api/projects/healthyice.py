import logging
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings
from app.core.security import verify_recaptcha
from app.api.projects.hipha import ContactForm
from app.core.mailer import (
    send_healthyice_order_customer,
    send_healthyice_order_team,
    generate_healthyice_contract_pdf,
    send_healthyice_contract_customer,
    send_healthyice_contract_team
)

router = APIRouter()
logger = logging.getLogger(__name__)

class HealthyIceContractForm(BaseModel):
    nombre: Optional[str] = None # Representante legal
    razon_social: Optional[str] = None
    rfc: Optional[str] = None
    domicilio: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    tipo_alianza: Optional[str] = "Punto de Venta"
    firma: Optional[str] = ""
    fecha: Optional[str] = None
    honeypot: Optional[str] = None
    recaptcha_token: Optional[str] = None
    
    # Nuevos campos del contrato de colaboracion comercial
    nombre_establecimiento: Optional[str] = ""
    esquema_comercial: Optional[str] = "Compra directa"
    esquema_comercial_otro: Optional[str] = ""
    frecuencia_pagos: Optional[str] = "Semanal"
    metodo_pago: Optional[str] = "Transferencia bancaria"
    metodo_pago_otro: Optional[str] = ""
    vigencia_meses: Optional[int] = 12
    fecha_inicio_dia: Optional[int] = None
    fecha_inicio_mes: Optional[str] = ""
    fecha_inicio_anio: Optional[int] = None
    ciudad_jurisdiccion: Optional[str] = "Guadalajara, Jalisco"
    representante_healthyice: Optional[str] = "FRANCISCO DELGADILLO"
    llenado_manual: Optional[bool] = False

@router.post("/healthyice")
async def submit_healthyice_form(form_data: ContactForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for HealthyIce contact form (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    # Validar reCAPTCHA v3 de forma estricta (no opcional)
    if not form_data.recaptcha_token or not form_data.recaptcha_token.strip():
        logger.warning(f"[SPAM DETECTED] Missing or empty reCAPTCHA token for HealthyIce contact form (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    secret_key = settings.HEALTHYICE_RECAPTCHA_SECRET_KEY or settings.HIPHA_RECAPTCHA_SECRET_KEY
    is_human = await verify_recaptcha(form_data.recaptcha_token, secret_key, "HealthyIce")
    if not is_human:
        logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for HealthyIce contact form (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    # Enviar correo de confirmación al cliente
    customer_email_sent = await send_healthyice_order_customer(form_data)
    
    # Enviar correo de notificación al equipo
    team_email_sent = await send_healthyice_order_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}

@router.post("/healthyice/contract")
async def submit_healthyice_contract(form_data: HealthyIceContractForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for HealthyIce contract form (email: {form_data.email}).")
        # Devolvemos un PDF vacío o error silencioso de tipo exitoso
        return Response(content=b"", media_type="application/pdf")

    # Validar reCAPTCHA v3 de forma estricta
    if not form_data.recaptcha_token or not form_data.recaptcha_token.strip():
        logger.warning(f"[SPAM DETECTED] Missing or empty reCAPTCHA token for HealthyIce contract form (email: {form_data.email}).")
        return Response(content=b"", media_type="application/pdf")

    secret_key = settings.HEALTHYICE_RECAPTCHA_SECRET_KEY or settings.HIPHA_RECAPTCHA_SECRET_KEY
    is_human = await verify_recaptcha(form_data.recaptcha_token, secret_key, "HealthyIce_Contract")
    if not is_human:
        logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for HealthyIce contract form (email: {form_data.email}).")
        return Response(content=b"", media_type="application/pdf")

    try:
        pdf_bytes = generate_healthyice_contract_pdf(form_data)
        
        # If it's a digital signature/submission, email the contract to customer and team
        if not form_data.llenado_manual:
            try:
                await send_healthyice_contract_customer(form_data)
                await send_healthyice_contract_team(form_data)
            except Exception as email_err:
                logger.error(f"Error sending contract emails: {str(email_err)}")
                
        razon_social = form_data.razon_social or "Formato_Manual"
        safe_name = razon_social.replace(' ', '_').replace('/', '_')
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Contrato_HealthyIce_{safe_name}.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")

