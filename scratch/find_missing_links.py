import os
import re
import urllib.parse
import urllib.request

base_url = "https://www.urologia-avanzada.com.mx"
target_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada"
blog_dir = os.path.join(target_dir, "blog")

def scan_local_html_for_links():
    links = set()
    # Find all html files in target_dir and its subdirectories
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # Find all href="..."
                for match in re.finditer(r'href="([^"]+)"', content):
                    href = match.group(1)
                    # Resolve if absolute or relative
                    full_url = urllib.parse.urljoin(base_url, href)
                    if full_url.startswith(base_url):
                        path = urllib.parse.urlparse(full_url).path
                        path = '/' + path.strip('/')
                        if path != '/':
                            links.add(path)
    return links

def get_existing_pages():
    pages = set()
    # Top level files (without extension)
    for file in os.listdir(target_dir):
        if file.endswith(".html"):
            pages.add("/" + file[:-5])
    # Blog level files
    if os.path.exists(blog_dir):
        for file in os.listdir(blog_dir):
            if file.endswith(".html"):
                pages.add("/blog/" + file[:-5])
    return pages

if __name__ == "__main__":
    found_links = scan_local_html_for_links()
    existing_pages = get_existing_pages()
    
    missing = found_links - existing_pages
    # Filter out empty paths or common static assets that ended up in href (if any)
    missing = {m for m in missing if not m.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'))}
    
    print("EXISTING PAGES:")
    for p in sorted(existing_pages):
        print(f"  {p}")
        
    print("\nFOUND LINKS IN HTML:")
    for l in sorted(found_links):
        print(f"  {l}")
        
    print("\nMISSING PAGES TO DOWNLOAD:")
    for m in sorted(missing):
        print(f"  {m}")
