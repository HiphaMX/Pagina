import urllib.request
import re
import ssl

url = "https://watchhouse.com/"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
)

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8')
    
    print("HTML length:", len(html))
    
    # Save the body content to a file to examine
    with open("watchhouse_body.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("Successfully saved html to watchhouse_body.html")
    
    # Try to extract the header or nav element
    # Look for header tag
    header_match = re.search(r'<header[^>]*>([\s\S]*?)</header>', html)
    if header_match:
        print("--- HEADER FOUND ---")
        header_content = header_match.group(0)
        # print first 1500 chars of header
        print(header_content[:1500])
        with open("watchhouse_header.html", "w", encoding="utf-8") as f:
            f.write(header_content)
    else:
        print("Header not found")
        
    # Search for nav or menu-drawer
    nav_matches = re.findall(r'<nav[^>]*>([\s\S]*?)</nav>', html)
    print(f"Found {len(nav_matches)} <nav> tags")
    for i, nav in enumerate(nav_matches):
        print(f"Nav {i+1} preview:")
        print(nav[:500])
        with open(f"watchhouse_nav_{i+1}.html", "w", encoding="utf-8") as f:
            f.write(nav)
            
except Exception as e:
    print("Error:", e)
