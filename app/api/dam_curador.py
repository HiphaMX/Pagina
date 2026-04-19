from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
import time
from typing import List, Optional

router = APIRouter()

# --- Schemas ---

class CatalogItem(BaseModel):
    nombre: str
    marca: str
    formato: str
    razon: str

class CuradorResponse(BaseModel):
    estilo_detectado: str
    vibra: str
    productos_seleccionados: List[CatalogItem]

class GenerationResponse(BaseModel):
    curador_data: CuradorResponse
    prompt_final: str
    image_url: str

@router.post("/analyze-inspiration", response_model=GenerationResponse)
async def analyze_inspiration(
    file_insp: UploadFile = File(...),
    file_piso: Optional[UploadFile] = File(None),
    file_comp: Optional[UploadFile] = File(None),
    context: Optional[str] = Form(None)
):
    """
    Motor de Generación Directa: Image-to-Image Pipeline.
    El usuario ahora sube imágenes de referencia físicas para sobreescribir estilos,
    y recibe un Render HR directamente.
    """
    
    if not file_insp.filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado.")
    
    # Simular tiempo de procesamiento avanzado (Multi-Image Parsing)
    time.sleep(3)
    
    # Determinar qué texturas entraron
    has_piso = file_piso is not None
    has_comp = file_comp is not None

    piso_nombre = "Textura de Piso Cargada por KAM" if has_piso else "Daltile Neutral Base"
    comp_nombre = "Complemento Auxiliar KAM" if has_comp else "Llave Genérica"

    context_note = f" (Nota: {context})" if context else ""
    
    # 1. CuradorDAM analiza la inspiración
    curador_data = CuradorResponse(
        estilo_detectado="Ultra-Realismo Personalizado",
        vibra=f"Entorno curado a partir de múltiples fuentes visuales. Fuerte inyección de texturas reales proporcionadas por KAM.{context_note}",
        productos_seleccionados=[
            CatalogItem(
                nombre=piso_nombre,
                marca="Daltile (Imposición de Textura Física)",
                formato="Adaptativo Visual",
                razon="La textura extraída del recorte será empleada como canal base para Alpha y Depth-map en el render final."
            ),
            CatalogItem(
                nombre=comp_nombre,
                marca="Marcas DAM Complementarias",
                formato="Adaptativo Visual",
                razon="Extracción de material, forma y refracción de luz detectada desde la imagen de referencia."
            )
        ]
    )
    
    # 2. Pipeline de Prompt para Gemini Imagen 3 / Nano Banana
    # El prompt ahora sigue estrictamente la arquitectura élite de IMAGENOLOGO.
    prompt_final = f"""Hyperrealistic architectural advertising photograph.
[CONTEXT & SCENE]: Interior design space featuring {context if context else 'a balanced, high-end Architectural Digest aesthetic'} inspired by the provided reference image.
[LIGHTING]: Professional interior lighting setup. Mix of natural daylight from volumetric windows and subtle artificial fill light to highlight material textures. Warm 3200k-4500k color temperature.
[MATERIALS & SURFACES - CRITICAL]: 
1. Floor/Wall Base: The primary surface must EXACTLY match the provided texture reference ({piso_nombre}). Render with 100% accurate material finish (matte, gloss, or satin as shown). 
2. Fixtures/Complements: Replicate the style, color, and metal finish of the secondary texture reference ({comp_nombre}) meticulously.
[COMPOSITION & CAMERA]: Eye-level architectural perspective, shot on Phase One IQ4 150MP, 35mm lens, f/8 for maximum depth of field. 
[POST-PROCESSING]: Editorial retouching, vibrant yet realistic color grading. No CG/AI artifacts, no uncanny valley geometry. 
[TECHNICAL PARAMETERS]: Resolution: 8K ultra-high definition | Aspect ratio: 16:9 | Rendering: photorealistic octane render | Output: maximum resolution available."""
    
    # Placeholder de estructura
    mock_image_result_url = "https://images.unsplash.com/photo-1620626011761-996317b8d101?q=80&w=1000&auto=format&fit=crop"

    return GenerationResponse(
        curador_data=curador_data,
        prompt_final=prompt_final,
        image_url=mock_image_result_url
    )
