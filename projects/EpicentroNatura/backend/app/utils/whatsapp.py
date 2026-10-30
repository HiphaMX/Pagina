import re
import urllib.parse
from typing import Optional


def sanitize_whatsapp_number(phone_number: str) -> str:
    """
    Limpia el número telefónico para la API de WhatsApp.
    Elimina caracteres especiales, espacios y guiones, asegurando el formato numérico internacional.
    """
    if not phone_number:
        return ""
    # Remover todo excepto dígitos
    cleaned = re.sub(r"\D", "", phone_number)
    
    # Si tiene 10 dígitos (México local), agregar código de país 52
    if len(cleaned) == 10:
        cleaned = f"52{cleaned}"
    # Si ya tiene +52 o 52 y luego 1, asegurar estándar WhatsApp
    return cleaned


def build_whatsapp_link(
    phone_number: str,
    business_name: str,
    item_context: Optional[str] = None
) -> str:
    """
    Construye un enlace directo a WhatsApp codificado para contacto hiperlocal en Natura.
    
    Args:
        phone_number: Teléfono en formato internacional (+52...)
        business_name: Nombre comercial o del emprendimiento
        item_context: Contexto opcional (ej: 'pedir a domicilio', 'solicitar cotización', nombre de producto)
        
    Returns:
        URL en formato https://wa.me/{phone}?text=...
    """
    clean_phone = sanitize_whatsapp_number(phone_number)
    
    if item_context:
        text = f"Hola {business_name}, vi su perfil en Epicentro Natura y me gustaría {item_context}."
    else:
        text = f"Hola {business_name}, vi su perfil en Epicentro Natura y me gustaría más información."
        
    encoded_text = urllib.parse.quote(text)
    return f"https://wa.me/{clean_phone}?text={encoded_text}"
