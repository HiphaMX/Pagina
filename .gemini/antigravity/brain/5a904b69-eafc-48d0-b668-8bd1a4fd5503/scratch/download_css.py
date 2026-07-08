import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

urls = [
    "https://watchhouse.com/cdn/shop/t/221/assets/base.css?v=2380172752660189731778837152",
    "https://watchhouse.com/cdn/shop/t/221/assets/layout.css?v=72783052856876201201763138484"
]

for i, url in enumerate(urls):
    filename = f"watchhouse_style_{i+1}.css"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            css = response.read().decode('utf-8')
        with open(filename, "w", encoding="utf-8") as f:
            f.write(css)
        print(f"Downloaded {url} to {filename}, length: {len(css)}")
        
        # Search for header-menu classes
        classes = re.findall(r'(\.[a-zA-Z0-9\-\_]+header-menu[\s\S]*?\{[\s\S]*?\})', css)
        print(f"Found {len(classes)} classes containing header-menu:")
        for c in classes[:10]:
            print(c[:400])
            print("-" * 40)
    except Exception as e:
        print("Error downloading:", url, e)
