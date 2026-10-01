import html
import re
import ssl
import urllib.parse
import urllib.request
from typing import Dict, Optional, Tuple

CRAWLER_USER_AGENTS = [
    "Twitterbot/1.0",
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)",
]


def _clean_unicode_escapes(s: str) -> str:
    if not s:
        return ""
    res = s
    for _ in range(2):
        if "\\u" in res:
            try:
                res = res.encode("utf-8").decode("unicode_escape")
            except Exception:
                pass
    return res


def _extract_instagram_embed(clean_url: str, handle: str) -> Optional[Dict]:
    """
    Extrae seguidores, nombre y avatar directamente desde la página de embed
    pública oficial de Instagram (https://www.instagram.com/{user}/embed/).
    Este endpoint está optimizado para incrustación pública global y devuelve
    metadatos pre-renderizados en JSON sin activar bloqueos ni muros de login.
    """
    clean_handle = handle.lstrip("@").strip()
    if not clean_handle or clean_handle.lower() in ["instagram", "p", "explore", "reels"]:
        return None

    embed_url = f"https://www.instagram.com/{clean_handle}/embed/"
    req = urllib.request.Request(
        embed_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
        },
    )

    try:
        ctx = ssl.create_default_context()
    except Exception:
        ctx = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=7) as resp:
            if resp.status != 200:
                return None
            html_raw = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None

    # 1. Seguidores
    followers = 0
    m_f = re.search(r"followers_count[^\d]+(\d+)", html_raw)
    if not m_f:
        m_f = re.search(r"edge_followed_by[^\d]+(\d+)", html_raw)
    if m_f:
        followers = int(m_f.group(1))

    if followers <= 0:
        return None

    # 2. Nombre del perfil
    page_name = clean_handle
    m_name = re.search(r'full_name[\\]*":\s*[\\]*"([^"]+?)[\\]*",', html_raw)
    if m_name:
        page_name = _clean_unicode_escapes(m_name.group(1)).strip() or clean_handle

    # 3. Avatar de perfil
    avatar_url = None
    m_avatar = re.search(r'profile_pic_url[\\]*":\s*[\\]*"(https:[^"\\]+)', html_raw)
    if not m_avatar:
        m_avatar = re.search(r'profile_pic_url[^\w]+(https:[^\"\'\s]+)', html_raw)
    if m_avatar:
        avatar_url = m_avatar.group(1).replace(r"\/", "/").replace("\\", "")

    return {
        "platform": "instagram",
        "handle": f"@{clean_handle}",
        "name": page_name,
        "url": clean_url,
        "avatar_url": avatar_url,
        "followers": followers,
        "raw_snippet": f"{followers} seguidores (Instagram Embed)",
    }


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

    # 1. Prioridad para Instagram: Embed oficial público (alta fidelidad y sin bloqueos)
    if platform == "instagram":
        embed_data = _extract_instagram_embed(clean_url, handle)
        if embed_data and embed_data.get("followers", 0) > 0:
            return embed_data

    # 2. Crawler para Facebook o como fallback de Instagram
    try:
        ctx = ssl.create_default_context()
    except Exception:
        ctx = ssl._create_unverified_context()

    html_content = ""
    last_error = None

    # Seleccionar user-agents adecuados según la red
    user_agents_to_try = (
        ["Twitterbot/1.0"] if platform == "instagram"
        else ["facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)", "Twitterbot/1.0"]
    )

    for ua in user_agents_to_try:
        req = urllib.request.Request(
            clean_url,
            headers={
                "User-Agent": ua,
                "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                final_url = resp.geturl()
                if "login" in final_url.lower() or "checkpoint" in final_url.lower():
                    continue
                raw_bytes = resp.read()
                raw_decoded = raw_bytes.decode("utf-8", errors="ignore")
                unescaped = html.unescape(raw_decoded)

                if (
                    "seguidores" in unescaped.lower()
                    or "followers" in unescaped.lower()
                    or "og:image" in unescaped.lower()
                    or "twitter:image" in unescaped.lower()
                ):
                    html_content = unescaped
                    break
                elif not html_content:
                    html_content = unescaped
        except urllib.error.URLError:
            try:
                unverified_ctx = ssl._create_unverified_context()
                with urllib.request.urlopen(req, context=unverified_ctx, timeout=8) as resp:
                    final_url = resp.geturl()
                    if "login" in final_url.lower() or "checkpoint" in final_url.lower():
                        continue
                    unescaped = html.unescape(resp.read().decode("utf-8", errors="ignore"))
                    if "seguidores" in unescaped.lower() or "followers" in unescaped.lower():
                        html_content = unescaped
                        break
                    elif not html_content:
                        html_content = unescaped
            except Exception as ex:
                last_error = ex
                continue
        except Exception as e:
            last_error = e
            continue

    if not html_content:
        raise RuntimeError(
            f"No se pudo consultar el enlace público de {clean_url} ({last_error or 'Acceso restringido por la red social'})"
        )

    # 1. Extraer Avatar (og:image o twitter:image)
    avatar_url = None
    img_matches = re.findall(
        r'<meta[^>]*(?:property|name)=[\"\'](?:og:image|twitter:image)[\"\'][^>]*content=[\"\']([^\"\']*)[\"\']',
        html_content,
        re.I,
    )
    if not img_matches:
        img_matches = re.findall(
            r'<meta[^>]*content=[\"\']([^\"\']*)[\"\'][^>]*(?:property|name)=[\"\'](?:og:image|twitter:image)[\"\']',
            html_content,
            re.I,
        )
    if img_matches:
        avatar_url = img_matches[0].strip()

    # 2. Extraer Título / Nombre
    page_name = handle
    title_matches = re.findall(
        r'<meta[^>]*(?:property|name)=[\"\'](?:og:title|twitter:title)[\"\'][^>]*content=[\"\']([^\"\']*)[\"\']',
        html_content,
        re.I,
    )
    if not title_matches:
        title_matches = re.findall(
            r'<meta[^>]*content=[\"\']([^\"\']*)[\"\'][^>]*(?:property|name)=[\"\'](?:og:title|twitter:title)[\"\']',
            html_content,
            re.I,
        )
    if not title_matches:
        title_matches = re.findall(r'<title[^>]*>(.*?)</title>', html_content, re.I)

    if title_matches:
        raw_title = title_matches[0].strip()
        if platform == "instagram":
            raw_title = re.sub(r"\s*\(?@[\w\.-]+\)?\s*•.*", "", raw_title).strip()
            raw_title = re.sub(r"\s*•\s*(?:Instagram|Fotos y videos|Perfil).*$", "", raw_title, flags=re.I).strip()
        elif platform == "facebook":
            raw_title = re.sub(r"\s*\|\s*Facebook.*", "", raw_title).strip()
            if " | " in raw_title:
                raw_title = raw_title.split(" | ")[0].strip()
        if raw_title:
            page_name = raw_title

    # 3. Extraer Seguidores según plataforma
    followers = 0
    raw_snippet = ""

    # Buscar en todo el HTML desescapado con regex amplio
    m = re.search(
        r"([\d\.,]+[kKmM]?)\s*(?:seguidores|personas siguen esto|Followers|likes|me gusta)",
        html_content,
        re.IGNORECASE,
    )
    if m:
        raw_snippet = m.group(0)
        followers = parse_follower_number(m.group(1))

    # Respaldo: buscar en JSON embebido de Instagram/Facebook
    if followers == 0:
        json_match = re.search(
            r'\"(?:edge_followed_by|follower_count)\":\s*(?:\{\"count\":\s*)?(\d+)',
            html_content,
        )
        if json_match:
            followers = int(json_match.group(1))
            raw_snippet = f"{followers} seguidores (JSON)"

    return {
        "platform": platform,
        "handle": handle,
        "name": page_name,
        "url": clean_url,
        "avatar_url": avatar_url,
        "followers": followers,
        "raw_snippet": raw_snippet,
    }
