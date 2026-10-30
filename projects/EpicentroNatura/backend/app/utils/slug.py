import re
import unicodedata


def slugify(text: str) -> str:
    """
    Convierte una cadena de texto en un slug URL-friendly.
    Ejemplo: 'Natura - Coto Roble!' -> 'natura-coto-roble'
    """
    if not text:
        return ""
    # Normalizar caracteres unicode (remover acentos)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", text)
