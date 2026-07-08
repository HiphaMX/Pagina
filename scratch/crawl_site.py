import os
import sys
import urllib.request
import urllib.parse
import re
from html.parser import HTMLParser

base_url = "https://www.urologia-avanzada.com.mx"
target_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada"
assets_dir = os.path.join(target_dir, "assets")

paths = [
    "/",
    "/aviso-de-privacidad-centro-de-urologia-avanzada",
    "/blog",
    "/blog/andropausia",
    "/blog/belisario-torres-alvarado-urologo",
    "/blog/dr-adalberto-castro-alfaro-urologo",
    "/blog/cancer-de-pene",
    "/blog/cancer-de-prostata",
    "/blog/cancer-renal",
    "/blog/cancer-testicular",
    "/blog/cancer-vesical",
    "/blog/cirugia-endourologica",
    "/blog/cirugia-laparoscopica",
    "/blog/cirugia-robotica",
    "/blog/disfuncion-erectil",
    "/blog/enfermedades-de-transmision-sexual",
    "/blog/hiperplasia-prostatica-benigna",
    "/blog/infeccion-en-vias-urinarias",
    "/blog/litiasis-renal",
    "/blog/prostatitis",
    "/blog/virus-del-papiloma-humano",
    "/diagnostico",
    "/equipo-medico",
    "/pacientes",
    "/preguntas-frecuentes-centro-de-urologia-avanzada",
    "/tipos-de-cirugia"
]

os.makedirs(assets_dir, exist_ok=True)
os.makedirs(os.path.join(target_dir, "blog"), exist_ok=True)

# Cache of downloaded assets: remote_url -> filename
downloaded_assets = {}

def download_file(url, local_path):
    if os.path.exists(local_path):
        # We still want to return True so we register it in the cache
        return True
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        print(f"Downloading {url} to {local_path}...")
        with urllib.request.urlopen(req) as response:
            content = response.read()
        with open(local_path, "wb") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return False

def get_filename_from_url(url):
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    filename = os.path.basename(path)
    if not filename:
        filename = "index.html"
    # remove query parameters
    filename = filename.split("?")[0]
    return filename

def process_asset_url(url, page_depth):
    # Resolve relative URL if needed
    full_url = urllib.parse.urljoin(base_url, url)
    
    parsed = urllib.parse.urlparse(full_url)
    
    is_asset = False
    if "website-files.com" in parsed.netloc or "cloudfront.net" in parsed.netloc or "ajax.googleapis.com" in parsed.netloc:
        is_asset = True
    elif parsed.path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf')):
        is_asset = True
        
    if not is_asset:
        return url
        
    if full_url in downloaded_assets:
        filename = downloaded_assets[full_url]
        rel_prefix = "../" * page_depth
        return f"{rel_prefix}assets/{filename}"
        
    filename = get_filename_from_url(full_url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) >= 2:
        prefix = path_parts[-2]
        if prefix != "js" and prefix != "css" and len(prefix) > 5:
            filename = f"{prefix}_{filename}"
            
    local_path = os.path.join(assets_dir, filename)
    success = download_file(full_url, local_path)
    
    if success:
        downloaded_assets[full_url] = filename
        rel_prefix = "../" * page_depth
        rel_path = f"{rel_prefix}assets/{filename}"
        return rel_path
    else:
        return url

def rewrite_html_content(html, page_path):
    parts = [p for p in page_path.split("/") if p]
    depth = len(parts)
    
    def replace_src_href(match):
        attr = match.group(1)
        url = match.group(2)
        if url.startswith(('tel:', 'mailto:', 'javascript:', '#')):
            return match.group(0)
            
        parsed = urllib.parse.urlparse(url)
        if (parsed.netloc == "" or parsed.netloc == "www.urologia-avanzada.com.mx" or parsed.netloc == "urologia-avanzada.com.mx") and not parsed.path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf')):
            return match.group(0)
            
        new_url = process_asset_url(url, depth)
        return f'{attr}="{new_url}"'

    html = re.sub(r'(src|href)="([^"]+)"', replace_src_href, html)
    
    def replace_srcset(match):
        srcset = match.group(1)
        parts = []
        for item in srcset.split(','):
            item = item.strip()
            if not item:
                continue
            subparts = item.split()
            if len(subparts) >= 1:
                url = subparts[0]
                new_url = process_asset_url(url, depth)
                if len(subparts) > 1:
                    parts.append(f"{new_url} {subparts[1]}")
                else:
                    parts.append(new_url)
        return f'srcset="{", ".join(parts)}"'
        
    html = re.sub(r'srcset="([^"]+)"', replace_srcset, html)
    
    def replace_style_url(match):
        prefix = match.group(1)
        url = match.group(2).strip("'\"")
        new_url = process_asset_url(url, depth)
        return f'{prefix}url("{new_url}")'
        
    html = re.sub(r'(background-image:\s*url\()([^\)]+)\)', replace_style_url, html)
    html = re.sub(r'(background:\s*url\()([^\)]+)\)', replace_style_url, html)
    
    return html

def crawl():
    for path in paths:
        url = base_url + path
        print(f"\nFetching page: {url}")
        
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')
        except Exception as e:
            print(f"Error fetching page {url}: {e}", file=sys.stderr)
            continue
            
        rewritten_html = rewrite_html_content(html, path)
        
        if path == "/":
            save_path = os.path.join(target_dir, "index.html")
        else:
            rel_path = path.strip("/") + ".html"
            save_path = os.path.join(target_dir, rel_path)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
        print(f"Saving to {save_path}")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(rewritten_html)
            
    print("\nCrawling and asset downloading completed successfully!")

if __name__ == "__main__":
    crawl()
