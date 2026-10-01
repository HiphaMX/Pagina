import html
import re
import ssl
import urllib.parse
import urllib.request
from typing import Dict, Optional, Tuple

CRAWLER_USER_AGENT = (
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
)
FALLBACK_USER_AGENT = "Twitterbot/1.0"


def normalize_social_url(raw_url: str) -> str:
    url = raw_url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    parsed = urllib.parse.urlparse(url)
    clean_path = parsed.path.rstrip("/") + "/"
    if parsed.query:
        clean_url = f"{parsed.scheme}://{parsed.netloc}{clean_path}?{parsed.query}"
    else:
        clean_url = f"{parsed.scheme}://{parsed.netloc}{clean_path}"
    return clean_url


def detect_platform_and_handle(raw_url: str) -> Tuple[str, str, str]:
    clean_url = normalize_social_url(raw_url)
    parsed = urllib.parse.urlparse(clean_url)
    domain = parsed.netloc.lower()

    if "instagram.com" in domain:
        platform = "instagram"
        parts = [p for p in parsed.path.split("/") if p]
        handle = f"@{parts[0]}" if parts else "@instagram"
    elif "facebook.com" in domain or "fb.com" in domain:
        platform = "facebook"
        if "profile.php" in parsed.path:
            handle = parsed.query or "facebook_page"
        else:
            parts = [p for p in parsed.path.split("/") if p and p not in ["pages", "groups"]]
            handle = parts[0] if parts else "facebook_page"
    else:
        raise ValueError(
            "Plataforma no soportada. Por favor ingresa un enlace de Instagram o Facebook."
        )

    return platform, handle, clean_url


def parse_follower_number(raw_str: str) -> int:
    if not raw_str:
        return 0
    clean = raw_str.replace("\xa0", " ").strip().upper()
    try:
        if "M" in clean:
            num = float(clean.replace("M", "").replace(",", ".").strip())
            return int(num * 1_000_000)
        elif "K" in clean:
            num = float(clean.replace("K", "").replace(",", ".").strip())
            return int(num * 1_000)
        else:
            clean_digits = re.sub(r"[^\d]", "", clean)
            return int(clean_digits) if clean_digits else 0
    except Exception:
        clean_digits = re.sub(r"[^\d]", "", clean)
        return int(clean_digits) if clean_digits else 0


def fetch_social_metadata(url: str, platform: Optional[str] = None) -> Dict:
    if not platform:
        platform, handle, clean_url = detect_platform_and_handle(url)
    else:
        clean_url = normalize_social_url(url)
        _, handle, _ = detect_platform_and_handle(clean_url)

    # Contexto SSL tolerante para entornos de ejecución heterogéneos
    try:
        ctx = ssl.create_default_context()
    except Exception:
        ctx = ssl._create_unverified_context()

    # Si falla la validación de certificados local, usamos contexto unverified como fallback
    def _fetch_content(target_url: str, user_agent: str) -> Tuple[int, str]:
        req = urllib.request.Request(
            target_url,
            headers={
                "User-Agent": user_agent,
                "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                return resp.status, resp.read().decode("utf-8", errors="ignore")
        except urllib.error.URLError:
            unverified_ctx = ssl._create_unverified_context()
            with urllib.request.urlopen(req, context=unverified_ctx, timeout=10) as resp:
                return resp.status, resp.read().decode("utf-8", errors="ignore")

    try:
        status, html_content = _fetch_content(clean_url, CRAWLER_USER_AGENT)
    except Exception as e_primary:
        try:
            status, html_content = _fetch_content(clean_url, FALLBACK_USER_AGENT)
        except Exception as e_fallback:
            raise RuntimeError(
                f"No se pudo consultar el enlace público ({e_fallback or e_primary})"
            )

    # 1. Extraer og:image (Avatar / Foto de Perfil)
    avatar_url = None
    og_img_matches = re.findall(
        r'<meta[^>]*property=[\"\']og:image[\"\'][^>]*content=[\"\']([^\"\']*)[\"\']',
        html_content,
        re.I,
    )
    if og_img_matches:
        avatar_url = html.unescape(og_img_matches[0])

    # 2. Extraer Título / Nombre
    page_name = handle
    og_title_matches = re.findall(
        r'<meta[^>]*property=[\"\']og:title[\"\'][^>]*content=[\"\']([^\"\']*)[\"\']',
        html_content,
        re.I,
    )
    if og_title_matches:
        raw_title = html.unescape(og_title_matches[0]).strip()
        # Limpieza de títulos de Instagram ej "Nombre (@handle) • Fotos y videos"
        if platform == "instagram":
            raw_title = re.sub(r"\s*\(?@[\w\.-]+\)?\s*•.*", "", raw_title).strip()
            raw_title = re.sub(r"\s*•\s*Instagram.*", "", raw_title).strip()
        elif platform == "facebook":
            raw_title = re.sub(r"\s*\|\s*Facebook.*", "", raw_title).strip()
            if " | " in raw_title:
                raw_title = raw_title.split(" | ")[0].strip()
        if raw_title:
            page_name = raw_title

    # 3. Extraer Seguidores según plataforma
    followers = 0
    raw_snippet = ""

    # Buscar en meta og:description y description
    meta_descriptions = re.findall(
        r'<meta[^>]*(?:name|property)=[\"\'](?:description|og:description)[\"\'][^>]*content=[\"\']([^\"\']*)[\"\']',
        html_content,
        re.I,
    )

    full_text = " ".join([html.unescape(m) for m in meta_descriptions])

    if platform == "instagram":
        # Formato: "11 Followers, 14 Following, 0 Posts..." o "29 seguidores, 0 seguidos..."
        m_ig = re.search(
            r"([\d\.,]+[kKmM]?)\s*(?:Followers|seguidores)", full_text, re.IGNORECASE
        )
        if m_ig:
            raw_snippet = m_ig.group(0)
            followers = parse_follower_number(m_ig.group(1))
    elif platform == "facebook":
        # Formato: "2.558 seguidores · 4 personas..." o "39.511.257 seguidores..." o "1.2K likes"
        m_fb = re.search(
            r"([\d\.,]+[kKmM]?)\s*(?:seguidores|personas siguen esto|Followers|likes|me gusta)",
            full_text,
            re.IGNORECASE,
        )
        if m_fb:
            raw_snippet = m_fb.group(0)
            followers = parse_follower_number(m_fb.group(1))

    return {
        "platform": platform,
        "handle": handle,
        "name": page_name,
        "url": clean_url,
        "avatar_url": avatar_url,
        "followers": followers,
        "raw_snippet": raw_snippet,
    }
