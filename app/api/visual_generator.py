from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import time
import json
import httpx
import base64
import uuid

router = APIRouter()

# --- MODELOS DE PYDANTIC ---

class PhotoSpecs(BaseModel):
    camera_body: str = Field("Phase One XF IQ4 150MP", description="Cámara o sensor de referencia")
    lens: str = Field("50mm", description="Lente y distancia focal")
    aperture: str = Field("f/1.8", description="Apertura del diafragma para control de profundidad de campo")
    lighting_scheme: str = Field("studio", description="Esquema o tipo de iluminación")
    lighting_direction: str = Field("rembrandt", description="Dirección de la fuente de luz")
    temp: int = Field(5600, description="Temperatura de color en Kelvin")
    angle: str = Field("eye-level", description="Ángulo de la toma de cámara")
    framing: str = Field("close-up", description="Tipo de encuadre")

class ConsistencyConfig(BaseModel):
    module_a_active: bool = Field(True, description="Activa consistencia de Producto (IP-Adapter)")
    module_a_weight: float = Field(0.85, description="Peso de influencia del Producto")
    module_a_image: Optional[str] = Field(None, description="Imagen codificada en base64 o URL para el producto")
    
    module_b_active: bool = Field(False, description="Activa consistencia de Rostro (InstantID)")
    module_b_weight: float = Field(0.70, description="Peso de influencia de Rostro")
    module_b_image: Optional[str] = Field(None, description="Imagen para consistencia del rostro")
    
    module_c_active: bool = Field(False, description="Activa consistencia de Estructura (ControlNet)")
    module_c_weight: float = Field(0.60, description="Peso de influencia de Estructura")
    module_c_image: Optional[str] = Field(None, description="Imagen de mapa de bordes/depth")
    
    module_d_active: bool = Field(True, description="Activa consistencia cromática (Paleta de color)")
    module_d_weight: float = Field(0.90, description="Peso de influencia cromática")
    module_d_image: Optional[str] = Field(None, description="Imagen de referencia cromática")

class VisualGeneratorPayload(BaseModel):
    subject: str = Field(..., description="Sujeto principal del anuncio / Prompt base")
    context: str = Field(..., description="Entorno o escena detallada")
    negative_prompt: Optional[str] = Field("blurry, low quality, cheap look", description="Prompt negativo")
    photo_specs: PhotoSpecs
    consistency: ConsistencyConfig
    engine: str = Field("mock", description="Motor de renderizado: mock, comfyui, webui")
    aspect_ratio: Optional[str] = Field("1:1", description="Relación de aspecto de la imagen")

class GenerateResponse(BaseModel):
    success: bool
    prompt_compiled: str
    image_url: str
    engine_used: str
    timestamp: float
    dimensions: str = "2048x2048"

# --- MODELOS PARA EL NUEVO FLUJO ---

class DraftPromptPayload(BaseModel):
    subject_description: str = Field(..., description="Breve descripción de la necesidad visual")
    aspect_ratio: str = Field("1:1", description="Formato o relación de aspecto de la imagen")

class DraftPromptResponse(BaseModel):
    prompt_drafted: str
    inferred_lens: str
    inferred_aperture: str
    inferred_lighting: str
    inferred_camera: str

class SaveSessionPayload(BaseModel):
    name: str = Field(..., description="Nombre del perfil del producto o modelo")
    aspect_ratio: str = Field("1:1", description="Formato guardado")
    subject_description: str = Field(..., description="Breve descripción guardada")
    module_a_image: Optional[str] = Field(None, description="Base64 de producto")
    module_a_weight: float = Field(0.85, description="Peso de producto")
    module_b_image: Optional[str] = Field(None, description="Base64 de rostro")
    module_b_weight: float = Field(0.70, description="Peso de rostro")
    module_c_image: Optional[str] = Field(None, description="Base64 de estructura")
    module_c_weight: float = Field(0.60, description="Peso de estructura")
    module_d_image: Optional[str] = Field(None, description="Base64 de paleta")
    module_d_weight: float = Field(0.90, description="Peso de paleta")

# --- POOL DE IMÁGENES MOCK ENRIQUECIDO ---
IMAGES_POOL = {
    "perfume": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=1200&auto=format&fit=crop",
    "audifonos": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1200&auto=format&fit=crop",
    "zapatillas": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1200&auto=format&fit=crop",
    "watches": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?q=80&w=1200&auto=format&fit=crop",
    "cosmetics": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?q=80&w=1200&auto=format&fit=crop",
    "gym": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1200&auto=format&fit=crop",
    "coffee": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=1200&auto=format&fit=crop",
    "food": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=1200&auto=format&fit=crop",
    "car": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=1200&auto=format&fit=crop",
    "default": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1200&auto=format&fit=crop"
}

# --- HEURÍSTICAS DE IMAGENOLOGO ---

def infer_photo_parameters(desc: str):
    """
    Analiza semánticamente la descripción para inferir la mejor configuración de cámara.
    """
    desc_lower = desc.lower()
    
    # Valores por defecto
    camera = "Phase One XF IQ4 150MP"
    lens = "50mm prime"
    aperture = "f/2.8"
    lighting = "three-point studio lighting with softbox diffusers"
    temp = 5600
    framing = "close-up"
    angle = "eye-level"
    direction = "rembrandt"
    
    # Heurística de Lente, Apertura y Cámara según producto o sujeto
    if any(k in desc_lower for k in ["perfume", "crema", "maquillaje", "cosmetico", "cosmetics", "creamy", "macro", "detalle", "joya", "anillo", "frasco", "botella"]):
        lens = "105mm macro"
        aperture = "f/8.0"
        framing = "extreme-close-up"
        camera = "Phase One XF IQ4 150MP"
    elif any(k in desc_lower for k in ["gimnasio", "gym", "atleta", "deporte", "ejercicio", "kira", "entrenamiento"]):
        lens = "50mm prime"
        aperture = "f/2.0"
        framing = "medium-shot"
        camera = "Sony A7R V"
    elif any(k in desc_lower for k in ["modelo", "retrato", "rostro", "persona", "hombre", "mujer", "chica", "chico", "face", "portrait", "beauty"]):
        lens = "85mm prime"
        aperture = "f/1.8"
        framing = "close-up"
        camera = "Hasselblad X2D 100C"
    elif any(k in desc_lower for k in ["street", "lifestyle", "ciudad", "calle", "paisaje", "exterior", "playa", "beach", "cielo"]):
        lens = "35mm prime"
        aperture = "f/2.8"
        framing = "medium-shot"
        camera = "Sony A7R V"
    elif any(k in desc_lower for k in ["cine", "pelicula", "cinematic", "car", "auto", "coche", "action"]):
        lens = "35mm anamorphic"
        aperture = "f/2.0"
        framing = "full-shot"
        camera = "ARRI Alexa LF"
        
    # Heurística de Iluminación según la atmósfera deseada
    if any(k in desc_lower for k in ["sunset", "atardecer", "amanecer", "sunrise", "golden hour", "calido", "warm"]):
        lighting = "warm sunset golden hour light, 2700k backlighting"
        temp = 3200
        direction = "rim"
    elif any(k in desc_lower for k in ["neon", "cyberpunk", "futurista", "dark", "nocturno", "night", "luces"]):
        lighting = "high-contrast cyberpunk neon rim lighting with cyan and magenta accents"
        temp = 8000
        direction = "rim"
    elif any(k in desc_lower for k in ["dramatica", "dramatic", "misterioso", "sombras", "shadow", "oscuro"]):
        lighting = "dramatic Rembrandt chiaroscuro lighting, deep shadows"
        temp = 4500
        direction = "rembrandt"
    elif any(k in desc_lower for k in ["limpia", "clean", "catalogo", "e-commerce", "white", "blanco", "brillante"]):
        lighting = "bright high-key commercial lighting setup, soft clean illumination"
        temp = 5600
        direction = "frontal"
        
    return {
        "camera_body": camera,
        "lens": lens,
        "aperture": aperture,
        "lighting_scheme": lighting,
        "lighting_direction": direction,
        "temp": temp,
        "angle": angle,
        "framing": framing
    }

def compile_prompt_layers(payload: VisualGeneratorPayload) -> str:
    """
    Ensambla el prompt completo siguiendo el framework IMAGENOLOGO.
    """
    specs = payload.photo_specs
    
    camera_map = {
        "medium-format": "Hasselblad X2D 100C medium format camera",
        "full-frame": "Sony A7R V high-resolution full-frame camera",
        "super-35": "ARRI Alexa LF cinematic Super 35 camera",
        "16mm": "vintage Bolex H16 16mm film camera"
    }
    camera_desc = camera_map.get(specs.camera_body, specs.camera_body)
    
    subject_part = f"Hyperrealistic commercial advertising photograph of {payload.subject}"
    context_part = payload.context
    framing_desc = f"{specs.framing} shot, {specs.angle} perspective"
    optical_desc = f"shot on {camera_desc}, {specs.lens} lens, aperture {specs.aperture}, color temperature {specs.temp}K"
    
    prompt_elements = [
        subject_part,
        context_part,
        f"{framing_desc}, {optical_desc}",
        f"{specs.lighting_scheme}, direction {specs.lighting_direction}",
        "exquisite detailed texture, commercial packshot style",
        "tack-sharp focus on the main subject, natural depth of field fall-off",
        "8K resolution, photorealistic, no AI artifacts, clean professional retouching"
    ]
    
    return ", ".join([el.strip() for el in prompt_elements if el.strip()])

def save_base64_image(base64_data: str, folder: str = "projects/visual-generator/output") -> str:
    os.makedirs(folder, exist_ok=True)
    if ";base64," in base64_data:
        base64_data = base64_data.split(";base64,")[1]
    
    file_name = f"gen_{uuid.uuid4().hex[:8]}.png"
    file_path = os.path.join(folder, file_name)
    
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(base64_data))
        
    return f"/projects/visual-generator/output/{file_name}"

def clean_subject_description(desc: str) -> str:
    desc_clean = desc.strip()
    prefixes = [
        "necesito una escena de", "necesito un escenario de", "necesito una imagen de", "necesito un", "necesito una",
        "necesito", "quiero una imagen de", "quiero un escenario de", "quiero un", "quiero una", "quiero",
        "haz una imagen de", "haz un", "haz una", "haz", "crea una imagen de", "crea un", "crea", "generar una imagen de",
        "generar un", "generar"
    ]
    desc_lower = desc_clean.lower()
    for prefix in prefixes:
        if desc_lower.startswith(prefix):
            desc_clean = desc_clean[len(prefix):].strip()
            if desc_clean:
                desc_clean = desc_clean[0].upper() + desc_clean[1:]
            break
    return desc_clean

# --- GOOGLE DEVELOPER API CALLS (GEMINI & IMAGEN 3) ---

async def translate_and_optimize_prompt(user_brief: str, api_key: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    system_instruction = (
        "You are IMAGENOLOGO, an elite art director and prompt engineer. Translate the user's Spanish scene description "
        "into a highly detailed, professional, layered photography prompt in English. "
        "Remove conversational phrases like 'Necesito una...', 'Haz un...', 'Por favor...' or similar. "
        "Describe the subject and action directly (e.g. 'An athletic woman named Kira in a gym holding a popsicle...'). "
        "Return ONLY the optimized English prompt as a single paragraph. Do not write markdown, do not write 'Here is your prompt', do not write any conversational text."
    )
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Translate and optimize this Spanish scene description into a professional English prompt following the layered guidelines: {user_brief}"
                    }
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {
                    "text": system_instruction
                }
            ]
        },
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 300
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=15.0)
        if response.status_code == 200:
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return text
        else:
            try:
                err_msg = response.json().get("error", {}).get("message", "Error de traducción")
            except:
                err_msg = response.text
            raise HTTPException(status_code=response.status_code, detail=f"Gemini API Error: {err_msg}")

async def generate_imagen_api(prompt: str, aspect_ratio: str, api_key: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:generateImages?key={api_key}"
    
    ar_map = {
        "1:1": "1:1",
        "9:16": "9:16",
        "16:9": "16:9",
        "4:5": "3:4"
    }
    ratio = ar_map.get(aspect_ratio, "1:1")
    
    payload = {
        "prompt": prompt,
        "numberOfImages": 1,
        "outputMimeType": "image/jpeg",
        "aspectRatio": ratio
    }
    
    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            images = data.get("generatedImages", [])
            if images:
                b64_bytes = images[0]["image"]["imageBytes"]
                saved_path = save_base64_image(b64_bytes)
                return saved_path
            raise HTTPException(status_code=500, detail="La respuesta de Imagen 3 no contiene imágenes.")
        else:
            try:
                err_json = response.json()
                err_msg = err_json.get("error", {}).get("message", "Error desconocido de Google API")
            except:
                err_msg = response.text
            raise HTTPException(status_code=response.status_code, detail=f"Google API Error: {err_msg}")

# --- ENDPOINTS ---

@router.post("/draft-prompt", response_model=DraftPromptResponse)
async def draft_prompt(payload: DraftPromptPayload, x_gemini_api_key: Optional[str] = Header(None)):
    """
    Endpoint para el Paso 4: Genera el prompt refinado considerando las heurísticas fotográficas o usando Gemini.
    """
    api_key = x_gemini_api_key or os.environ.get("GEMINI_API_KEY")
    prompt_drafted = None
    
    if api_key:
        try:
            prompt_drafted = await translate_and_optimize_prompt(payload.subject_description, api_key)
        except Exception as e:
            print(f"Gemini prompt drafting failed: {e}. Falling back to local heuristics.")
        
    inferred = infer_photo_parameters(payload.subject_description)
    
    if not prompt_drafted:
        # Fallback a heurísticas locales si no hay API Key o falla
        cleaned_desc = clean_subject_description(payload.subject_description)
        subject_part = f"Hyperrealistic commercial advertising photograph of {cleaned_desc}"
        optical_desc = f"shot on {inferred['camera_body']}, {inferred['lens']} lens, aperture {inferred['aperture']}, color temperature {inferred['temp']}K"
        
        prompt_elements = [
            subject_part,
            f"{inferred['framing']} shot, {inferred['angle']} perspective",
            optical_desc,
            f"{inferred['lighting_scheme']}, direction {inferred['lighting_direction']}",
            "exquisite detailed texture, commercial packshot style",
            "tack-sharp focus, 8K resolution, photorealistic, no AI artifacts"
        ]
        prompt_drafted = ", ".join(prompt_elements)
    
    return DraftPromptResponse(
        prompt_drafted=prompt_drafted,
        inferred_lens=inferred["lens"],
        inferred_aperture=inferred["aperture"],
        inferred_lighting=inferred["lighting_scheme"],
        inferred_camera=inferred["camera_body"]
    )

@router.post("/generate", response_model=GenerateResponse)
async def generate_visual(payload: VisualGeneratorPayload, x_gemini_api_key: Optional[str] = Header(None)):
    prompt_compiled = payload.context.strip()
    if not prompt_compiled:
        prompt_compiled = compile_prompt_layers(payload)
        
    api_key = x_gemini_api_key or os.environ.get("GEMINI_API_KEY")
    
    output_dir = "projects/visual-generator/output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. MOTOR GOOGLE IMAGEN 3 API (REAL)
    if payload.engine == "google_imagen":
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="Google API Key no provista. Por favor agrégala en la cabecera (Header de API Key en el panel)."
            )
        
        saved_url = await generate_imagen_api(prompt_compiled, payload.aspect_ratio or "1:1", api_key)
        if saved_url:
            return GenerateResponse(
                success=True,
                prompt_compiled=prompt_compiled,
                image_url=saved_url,
                engine_used="google_imagen_3_api",
                timestamp=time.time()
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error en la API de Google Imagen 3 al generar la imagen. Verifica tu clave de API."
            )
            
    # 2. MOTOR MOCK INTELIGENTE
    elif payload.engine == "mock":
        time.sleep(1.0)
        
        subject_lower = payload.subject.lower()
        target_key = "default"
        if any(x in subject_lower for x in ["perfume", "frasco", "botella"]):
            target_key = "perfume"
        elif any(x in subject_lower for x in ["audifono", "headphone", "oreja", "auriculares"]):
            target_key = "audifonos"
        elif any(x in subject_lower for x in ["sneaker", "zapatilla", "zapato", "calzado"]):
            target_key = "zapatillas"
        elif any(x in subject_lower for x in ["reloj", "watch"]):
            target_key = "watches"
        elif any(x in subject_lower for x in ["cosmetico", "crema", "maquillaje", "skincare", "belleza"]):
            target_key = "cosmetics"
        elif any(x in subject_lower for x in ["gimnasio", "gym", "atleta", "deporte", "ejercicio", "kira", "entrenamiento"]):
            target_key = "gym"
        elif any(x in subject_lower for x in ["cafe", "café", "coffee", "taza"]):
            target_key = "coffee"
        elif any(x in subject_lower for x in ["comida", "food", "platillo", "restaurante", "cena"]):
            target_key = "food"
        elif any(x in subject_lower for x in ["auto", "car", "coche", "vehiculo"]):
            target_key = "car"
            
        remote_url = IMAGES_POOL.get(target_key, IMAGES_POOL["default"])
        image_url = remote_url
        
        # Guardar en local para que aparezca en el historial
        try:
            with httpx.Client() as client:
                res = client.get(remote_url, timeout=10.0)
                if res.status_code == 200:
                    file_name = f"gen_mock_{uuid.uuid4().hex[:8]}.png"
                    local_path = os.path.join(output_dir, file_name)
                    with open(local_path, "wb") as f:
                        f.write(res.content)
                    image_url = f"/projects/visual-generator/output/{file_name}"
        except Exception as e:
            print(f"Error al descargar imagen mock a local: {e}")
        
        return GenerateResponse(
            success=True,
            prompt_compiled=prompt_compiled,
            image_url=image_url,
            engine_used="mock_inteligen_local",
            timestamp=time.time()
        )
        
    # 2. MOTOR SD WEBUI
    elif payload.engine == "webui":
        url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
        
        # Calcular resoluciones óptimas para Mac M1 (velocidad y consistencia)
        ar = payload.aspect_ratio or "1:1"
        if ar == "9:16":
            width, height = 512, 896
        elif ar == "16:9":
            width, height = 896, 512
        elif ar == "4:5" or ar == "3:4":
            width, height = 576, 768
        else:  # 1:1
            width, height = 512, 512

        sd_payload = {
            "prompt": prompt_compiled,
            "negative_prompt": payload.negative_prompt or "ugly, deformed, noise, blurry, low contrast, low quality, duplicate, logo, signature",
            "steps": 20,
            "width": width,
            "height": height,
            "cfg_scale": 7.0,
            "sampler_name": "DPM++ 2M Karras"
        }
        
        if payload.consistency.module_a_active and payload.consistency.module_a_image:
            sd_payload["alwayson_scripts"] = {
                "controlnet": {
                    "args": [
                        {
                            "input_image": payload.consistency.module_a_image,
                            "module": "canny",
                            "model": "control_v11p_sd15_canny [d14cfa4b]",
                            "weight": payload.consistency.module_a_weight
                        }
                    ]
                }
            }
            
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=sd_payload)
                if response.status_code == 200:
                    data = response.json()
                    images = data.get("images", [])
                    if images:
                        saved_url = save_base64_image(images[0])
                        return GenerateResponse(
                            success=True,
                            prompt_compiled=prompt_compiled,
                            image_url=saved_url,
                            engine_used="sd_webui_local",
                            timestamp=time.time()
                        )
                raise Exception(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail="No se pudo conectar con el motor local Stable Diffusion/Draw Things. "
                       "Asegúrate de que la aplicación Draw Things esté abierta en tu Mac y que tengas activo "
                       "el 'HTTP API Server' en los Ajustes (puerto 7860)."
            )
            
    # 3. MOTOR COMFYUI
    elif payload.engine == "comfyui":
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get("http://127.0.0.1:8188/system_info")
                if res.status_code == 200:
                    return GenerateResponse(
                        success=True,
                        prompt_compiled=prompt_compiled + " (ComfyUI API activo)",
                        image_url=IMAGES_POOL["default"],
                        engine_used="comfyui_detected_mock_output",
                        timestamp=time.time()
                    )
            raise Exception("ComfyUI no responde")
        except Exception as e:
            return GenerateResponse(
                success=True,
                prompt_compiled=prompt_compiled + f" (ComfyUI offline: {str(e)})",
                image_url=IMAGES_POOL["default"],
                engine_used="mock_fallback_offline",
                timestamp=time.time()
            )
            
    else:
        raise HTTPException(status_code=400, detail="Motor no soportado")

# --- PERSISTENCIA DE MEMORIA DE PRODUCTO (SESIONES) ---

def get_sessions_file_path() -> str:
    folder = "projects/visual-generator/output"
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "sessions.json")

@router.post("/sessions/save")
async def save_session(payload: SaveSessionPayload):
    """
    Paso 7: Guarda la consistencia, sliders e imágenes del producto en un archivo local JSON.
    """
    path = get_sessions_file_path()
    
    # Cargar sesiones existentes
    sessions = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                sessions = json.load(f)
        except Exception:
            sessions = {}
            
    # Guardar o actualizar
    sessions[payload.name] = payload.dict()
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2, ensure_ascii=False)
        
    return {"success": True, "message": f"Perfil '{payload.name}' guardado correctamente en local."}

@router.get("/sessions")
async def list_sessions():
    """
    Lista todos los perfiles de productos guardados en local.
    """
    path = get_sessions_file_path()
    if not os.path.exists(path):
        return []
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            sessions = json.load(f)
        return list(sessions.values())
    except Exception:
        return []

@router.get("/history")
async def get_generation_history():
    output_dir = "projects/visual-generator/output"
    if not os.path.exists(output_dir):
        return []
        
    files = []
    for f in os.listdir(output_dir):
        if f.startswith("gen_") and (f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg")):
            path = os.path.join(output_dir, f)
            files.append({
                "url": f"/projects/visual-generator/output/{f}",
                "created_at": os.path.getctime(path)
            })
            
    files.sort(key=lambda x: x["created_at"], reverse=True)
    return files
