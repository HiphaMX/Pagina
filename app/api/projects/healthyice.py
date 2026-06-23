from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from app.api.projects.hipha import ContactForm
from app.core.mailer import (
    send_healthyice_order_customer,
    send_healthyice_order_team,
    generate_healthyice_contract_pdf,
    send_healthyice_contract_customer,
    send_healthyice_contract_team
)

router = APIRouter()

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
    # Por ahora omitimos el envío de correos de notificación del lead por petición del usuario
    # customer_email_sent = await send_healthyice_order_customer(form_data)
    # team_email_sent = await send_healthyice_order_team(form_data)
    
    # if not customer_email_sent and not team_email_sent:
    #     raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}

@router.post("/healthyice/contract")
async def submit_healthyice_contract(form_data: HealthyIceContractForm):
    try:
        pdf_bytes = generate_healthyice_contract_pdf(form_data)
        
        # If it's a digital signature/submission, email the contract to customer and team
        if not form_data.llenado_manual:
            try:
                # Por ahora omitimos el envío de correos de contrato por petición del usuario
                # await send_healthyice_contract_customer(form_data)
                # await send_healthyice_contract_team(form_data)
                pass
            except Exception as email_err:
                # Log email failure but don't block the user's PDF download
                import logging
                logging.getLogger(__name__).error(f"Error sending contract emails: {str(email_err)}")
                
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
