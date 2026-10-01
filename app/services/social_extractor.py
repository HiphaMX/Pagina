import html
import re
import ssl
import urllib.parse
import urllib.request
from typing import Dict, Optional, Tuple

CRAWLER_USER_AGENTS = [
    "Twitterbot/1.0",
    "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)",
    "WhatsApp/2.21.12.21 A",
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (Applebot/0.1; +http://www.apple.com/bot.html)",
]


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

    try:
        ctx = ssl.create_default_context()
    except Exception:
        ctx = ssl._create_unverified_context()

    html_content = ""
    last_error = None

    for ua in CRAWLER_USER_AGENTS:
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
                    # Si fue redirigido a login, este UA no logró ver el contenido público
                    continue
                raw_bytes = resp.read()
                raw_decoded = raw_bytes.decode("utf-8", errors="ignore")
                unescaped = html.unescape(raw_decoded)

                # Si contiene mención a seguidores o imagen de og, es una respuesta válida
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
