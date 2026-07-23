import urllib.request
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context

url = "https://html.duckduckgo.com/html/?q=Soul+Shine+Inside+Guadalajara"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
)

try:
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', content, re.DOTALL)
        print(f"Found {len(snippets)} snippets")
        for i, snip in enumerate(snippets[:10]):
            clean_snip = re.sub('<[^<]+?>', '', snip).strip()
            print(f"{i+1}: {clean_snip}\n")
            
except Exception as e:
    print(f"Error: {e}")
