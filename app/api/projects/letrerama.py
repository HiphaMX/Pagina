from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter()

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

@router.post("/letrerama")
async def submit_letrerama_quote(form_data: LetreramaQuoteForm):
    # Log received form data details in console
    print(f"[Letrerama Backend] Cotización recibida de: {form_data.nombre} ({form_data.email})")
    print(f"  Proyecto: {form_data.tecnica} | Medidas: {form_data.medida_ancho}x{form_data.medida_alto} cm")
    
    return {"message": "Formulario recibido correctamente"}
