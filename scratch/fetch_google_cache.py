import urllib.request
import sys
import os

url_belisario = "https://webcache.googleusercontent.com/search?q=cache:https://www.urologia-avanzada.com.mx/blog/belisario-torres-alvarado-urologo"
url_adalberto = "https://webcache.googleusercontent.com/search?q=cache:https://www.urologia-avanzada.com.mx/blog/dr-adalberto-castro-alfaro-urologo"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

def fetch_cache(url, name):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            content = response.read()
        
        # Save raw cache page
        save_path = f"/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/scratch/{name}_cache.html"
        with open(save_path, "wb") as f:
            f.write(content)
        print(f"Successfully fetched cache for {name} and saved to {save_path}")
        return True
    except Exception as e:
        print(f"Error fetching cache for {name}: {e}")
        return False

if __name__ == "__main__":
    fetch_cache(url_belisario, "belisario")
    fetch_cache(url_adalberto, "adalberto")
