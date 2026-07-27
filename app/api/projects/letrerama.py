import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)

class LetreramaQuoteForm(BaseModel):
    nombre: str
    telefono: str
    email: EmailStr
    empresa: Optional[str] = ""
    tiene_vector: str  # "SI" / "NO"
    logo_base64: Optional[str] = None
    logo_filename: Optional[str] = None
    tecnica: str
    medida_ancho: float
    medida_alto: float
    medida_canto: Optional[float] = None
    iluminacion: str
    material: str
    altura_instalacion: float
    direccion_instalacion: str
    privacidad: bool
    honeypot: Optional[str] = None

@router.post("/letrerama")
async def submit_letrerama_quote(form_data: LetreramaQuoteForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for Letrerama (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    # Log received form data details in console
    logger.info(f"[Letrerama Backend] Cotización recibida de: {form_data.nombre} ({form_data.email})")
    logger.info(f"  Proyecto: {form_data.tecnica} | Medidas: {form_data.medida_ancho}x{form_data.medida_alto} cm")
    
    return {"message": "Formulario recibido correctamente"}

