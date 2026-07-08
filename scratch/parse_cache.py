import os
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser

base_url = "https://www.urologia-avanzada.com.mx"
target_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada"
assets_dir = os.path.join(target_dir, "assets")

# Cache of downloaded assets (filename -> true)
downloaded_assets = {}

# Populate downloaded assets cache from existing files in assets directory
if os.path.exists(assets_dir):
    for f in os.listdir(assets_dir):
        downloaded_assets[f] = True

def download_file(url, local_path):
    if os.path.exists(local_path):
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
        print(f"Error downloading {url}: {e}")
        return False

def get_filename_from_url(url):
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    filename = os.path.basename(path)
    if not filename:
        filename = "index.html"
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
        
    filename = get_filename_from_url(full_url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) >= 2:
        prefix = path_parts[-2]
        if prefix != "js" and prefix != "css" and len(prefix) > 5:
            filename = f"{prefix}_{filename}"
            
    local_path = os.path.join(assets_dir, filename)
    success = download_file(full_url, local_path)
    
    if success:
        rel_prefix = "../" * page_depth
        return f"{rel_prefix}assets/{filename}"
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

def parse_and_save(cache_path, page_path, save_filename):
    print(f"\nProcessing {cache_path}...")
    with open(cache_path, "r", encoding="utf-8", errors="ignore") as f:
        cache_content = f.read()
        
    # Extract original HTML
    # We find the first <!DOCTYPE html> or <html
    doc_type_pos = cache_content.find("<!DOCTYPE html>")
    if doc_type_pos == -1:
        doc_type_pos = cache_content.find("<html")
        
    if doc_type_pos == -1:
        print(f"Error: Original HTML not found in {cache_path}")
        return
        
    original_html = cache_content[doc_type_pos:]
    
    # Strip any google cache elements injected at the end (like scripts or comment blocks if any)
    # Usually Google cache ends with </html>
    html_end_pos = original_html.rfind("</html>")
    if html_end_pos != -1:
        original_html = original_html[:html_end_pos + 7]
        
    # Remove google cache notification bar at the top if it is inside <body>
    # The cache notification bar is inside a div container at the top of body.
    # It has text: "Esta es una copia de seguridad en caché de Google de"
    # Or "This is Google's cache of"
    # Let's search for this div pattern and remove it.
    original_html = re.sub(r'<div style="background:#fff;border:1px solid #999;margin:-1px -1px 0;padding:0;">[\s\S]*?</div></div>', '', original_html, 1)
    
    # Process assets
    rewritten_html = rewrite_html_content(original_html, page_path)
    
    # Save path
    save_path = os.path.join(target_dir, "blog", save_filename)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(rewritten_html)
    print(f"Saved rewritten HTML to {save_path}")

if __name__ == "__main__":
    parse_and_save(
        "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/scratch/belisario_cache.html", 
        "/blog/belisario-torres-alvarado-urologo", 
        "belisario-torres-alvarado-urologo.html"
    )
    parse_and_save(
        "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/scratch/adalberto_cache.html", 
        "/blog/dr-adalberto-castro-alfaro-urologo", 
        "dr-adalberto-castro-alfaro-urologo.html"
    )
