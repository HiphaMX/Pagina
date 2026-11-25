import os
import re
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from app.core.config import settings
from app.core.security import verify_recaptcha
from app.core.mailer import (
    send_jessica_mendoza_confirmation_email,
    send_jessica_mendoza_notification_team
)

router = APIRouter()
logger = logging.getLogger(__name__)

class JessicaMendozaForm(BaseModel):
    nombre: str
    apellido: Optional[str] = ""
    email: EmailStr
    telefono: str
    intencion: str
    propiedad: str
    mensaje: Optional[str] = ""
    honeypot: Optional[str] = None
    recaptcha_token: Optional[str] = None

@router.post("/jessica-mendoza")
async def submit_jessica_mendoza_form(form_data: JessicaMendozaForm):
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for Jessica Mendoza (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    # Validar reCAPTCHA v3 si el token está presente
    if form_data.recaptcha_token and form_data.recaptcha_token.strip():
        secret_key = settings.JESSICAMENDOZA_RECAPTCHA_SECRET_KEY or settings.HIPHA_RECAPTCHA_SECRET_KEY
        is_human = await verify_recaptcha(form_data.recaptcha_token, secret_key, "JessicaMendoza")
        if not is_human:
            logger.warning(f"[SPAM DETECTED] reCAPTCHA validation failed for Jessica Mendoza (email: {form_data.email}).")
            return {"message": "Formulario recibido correctamente"}
    else:
        logger.info(f"[SECURITY INFO] Missing reCAPTCHA token for Jessica Mendoza (email: {form_data.email}). Bypassed verification.")

    customer_email_sent = await send_jessica_mendoza_confirmation_email(form_data)
    team_email_sent = await send_jessica_mendoza_notification_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}


# ============================================================================
# BASE DE DATOS Y RENDERIZADO SSR DINÁMICO PARA SOCIAL PREVIEWS (WHATSAPP / OG)
# ============================================================================

PROPERTIES_CATALOG = {
    1: {
        "id": 1,
        "codigo": "JM0926-01",
        "slug": "casa-en-renta-en-los-robles-residencial",
        "title": "Casa en Renta en Los Robles Residencial",
        "descripcion": "Hermosa y amplia residencia en renta dentro del exclusivo Coto Helechos en Los Robles Residencial, Zapopan. 3 recámaras, paneles solares, cocina con parota y granito, mantenimiento incluido.",
        "og_image": "https://www.jessicamendozabienesraices.com/Assets/Propiedades/LosRobles/preview-los-robles.jpg",
        "og_image_type": "image/jpeg"
    },
    5: {
        "id": 5,
        "codigo": "JM1126-02",
        "slug": "casa-en-venta-en-los-robles-coto-encinos",
        "title": "Casa en Venta en Los Robles Residencial",
        "descripcion": "Hermosa y amplia residencia en venta dentro del exclusivo Fraccionamiento Los Robles Residencial, Coto Encinos, Zapopan. 3 recámaras, 4.5 baños, roof top con flex room, paneles solares.",
        "og_image": "https://www.jessicamendozabienesraices.com/Assets/Propiedades/CotoEncinos/preview-coto-encinos.jpg",
        "og_image_type": "image/jpeg"
    },
    2: {
        "id": 2,
        "codigo": "",
        "slug": "residencia-de-autor-valle-imperial",
        "title": "Residencia de Autor - Valle Imperial",
        "descripcion": "Residencia contemporánea a estrenar dentro de coto privado en Valle Imperial. 3 recámaras, 3 baños, acabados residenciales de primer nivel y jardín posterior.",
        "og_image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&h=630&q=80",
        "og_image_type": "image/jpeg"
    },
    3: {
        "id": 3,
        "codigo": "",
        "slug": "loft-boutique-providencia",
        "title": "Loft Boutique - Providencia",
        "descripcion": "Loft de estilo industrial-chic en Providencia, Guadalajara. Concreto pulido, amplios ventanales y ubicación privilegiada en zona dorada.",
        "og_image": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=1200&h=630&q=80",
        "og_image_type": "image/jpeg"
    },
    4: {
        "id": 4,
        "codigo": "",
        "slug": "lote-residencial-sunset-telchac",
        "title": "Lote Residencial Sunset - Telchac",
        "descripcion": "Terreno plano y regular a solo 200 metros de la orilla de playa en Telchac Puerto, Yucatán. Certeza jurídica y alta plusvalía garantizada.",
        "og_image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&h=630&q=80",
        "og_image_type": "image/jpeg"
    }
}

_CACHED_TEMPLATE = None

def _load_propiedad_template() -> str:
    global _CACHED_TEMPLATE
    if _CACHED_TEMPLATE:
        return _CACHED_TEMPLATE

    candidate_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "templates", "jessica_mendoza_propiedad.html"),
        os.path.join(os.getcwd(), "app", "templates", "jessica_mendoza_propiedad.html"),
        os.path.join(os.getcwd(), "projects", "JessicaMendoza", "propiedad.html"),
        os.path.join("app", "templates", "jessica_mendoza_propiedad.html"),
        os.path.join("projects", "JessicaMendoza", "propiedad.html")
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    _CACHED_TEMPLATE = f.read()
                    if _CACHED_TEMPLATE:
                        return _CACHED_TEMPLATE
            except Exception as e:
                logger.warning(f"No se pudo leer template de {p}: {e}")

    return ""


def render_propiedad_page(request: Request) -> HTMLResponse:
    """Renderiza el HTML de la propiedad con OpenGraph dinámico para rastreadores sociales (WhatsApp, Facebook, Twitter, iMessage)."""
    raw_html = _load_propiedad_template()
    if not raw_html:
        raise HTTPException(status_code=500, detail="Plantilla de propiedad no encontrada.")

    # 1. Resolver el inmueble solicitado a partir de los query params
    prop_id = request.query_params.get("id")
    prop_code = request.query_params.get("codigo") or request.query_params.get("ref") or request.query_params.get("id_propiedad")
    prop_slug = request.query_params.get("nombre") or request.query_params.get("slug") or request.query_params.get("propiedad")

    selected_prop = None
    if prop_id:
        try:
            pid = int(prop_id)
            selected_prop = PROPERTIES_CATALOG.get(pid)
        except ValueError:
            pass

    if not selected_prop and prop_code:
        code_clean = prop_code.strip().lower()
        for p in PROPERTIES_CATALOG.values():
            if p.get("codigo", "").lower() == code_clean:
                selected_prop = p
                break

    if not selected_prop and prop_slug:
        slug_clean = prop_slug.strip().lower()
        for p in PROPERTIES_CATALOG.values():
            if p.get("slug", "").lower() == slug_clean:
                selected_prop = p
                break

    # Si no se encuentra o no se pasó parámetro, fallback a la Propiedad 1
    if not selected_prop:
        selected_prop = PROPERTIES_CATALOG[1]

    title = selected_prop["title"]
    full_title = f"{title} | Jessica Mendoza Bienes Raíces"
    desc = selected_prop["descripcion"]
    og_img = selected_prop["og_image"]
    og_img_type = selected_prop.get("og_image_type", "image/jpeg")
    canonical_url = f"https://www.jessicamendozabienesraices.com/propiedad.html?id={selected_prop['id']}&nombre={selected_prop['slug']}"

    rendered = raw_html

    # Reemplazo de título
    rendered = re.sub(r"<title>.*?</title>", f"<title>{full_title}</title>", rendered, flags=re.DOTALL | re.IGNORECASE)

    # Reemplazo de metadatos OpenGraph y Twitter
    rendered = re.sub(r'<meta property="og:title"[^>]*>', f'<meta property="og:title" id="og-title" content="{full_title}">', rendered, flags=re.IGNORECASE)
    rendered = re.sub(r'<meta property="og:description"[^>]*>', f'<meta property="og:description" id="og-desc" content="{desc}">', rendered, flags=re.IGNORECASE)
    rendered = re.sub(r'<meta property="og:image"[^>]*>', f'<meta property="og:image" id="og-image" content="{og_img}">', rendered, flags=re.IGNORECASE)
    rendered = re.sub(r'<meta property="og:image:secure_url"[^>]*>', f'<meta property="og:image:secure_url" id="og-image-secure" content="{og_img}">', rendered, flags=re.IGNORECASE)
    rendered = re.sub(r'<meta property="og:image:type"[^>]*>', f'<meta property="og:image:type" id="og-image-type" content="{og_img_type}">', rendered, flags=re.IGNORECASE)
    rendered = re.sub(r'<meta property="og:image:alt"[^>]*>', f'<meta property="og:image:alt" id="og-image-alt" content="{title}">', rendered, flags=re.IGNORECASE)
    rendered = re.sub(r'<meta property="og:url"[^>]*>', f'<meta property="og:url" id="og-url" content="{canonical_url}">', rendered, flags=re.IGNORECASE)

    rendered = re.sub(r'<meta name="twitter:title"[^>]*>', f'<meta name="twitter:title" id="twitter-title" content="{full_title}">', rendered, flags=re.IGNORECASE)
    rendered = re.sub(r'<meta name="twitter:description"[^>]*>', f'<meta name="twitter:description" id="twitter-desc" content="{desc}">', rendered, flags=re.IGNORECASE)
    rendered = re.sub(r'<meta name="twitter:image"[^>]*>', f'<meta name="twitter:image" id="twitter-image" content="{og_img}">', rendered, flags=re.IGNORECASE)

    # Inyectar canonical link si no está presente
    if 'rel="canonical"' in rendered:
        rendered = re.sub(r'<link [^>]*rel="canonical"[^>]*>', f'<link rel="canonical" href="{canonical_url}">', rendered, flags=re.IGNORECASE)
    else:
        rendered = rendered.replace("</head>", f'    <link rel="canonical" href="{canonical_url}">\n</head>')

    return HTMLResponse(
        content=rendered,
        media_type="text/html; charset=utf-8",
        headers={
            "Cache-Control": "public, max-age=60, s-maxage=3600, stale-while-revalidate=86400",
            "Access-Control-Allow-Origin": "*"
        }
    )
