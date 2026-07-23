import urllib.request
import ssl
import json
import re

ssl._create_default_https_context = ssl._create_unverified_context

url = "https://www.google.com/maps/preview/review/list?authuser=0&hl=es&gl=mx&pb=!1m2!1y3473898156040788318!2y1746270557456!3m1!3m2!1s0x2a77ec40183ba563:0x3035c3f7a8b2195e!2s!3e0!4e1!5m1!3s"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Accept-Language': 'es-MX,es;q=0.9'}
)

try:
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        # Google Maps preview returns a JSON-like structure prefixed with garbage )]}'
        if content.startswith(")]}'"):
            content = content[4:].strip()
            
        with open("scratch/reviews_raw.txt", "w", encoding="utf-8") as f:
            f.write(content)
        print("API Response saved to scratch/reviews_raw.txt")
        
        # Let's search for text patterns
        # We can extract text strings
        strings = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', content)
        print(f"Quoted strings count: {len(strings)}")
        
        # Print a few strings to inspect
        for i, s in enumerate(strings[:100]):
            s_clean = s.replace('\\n', ' ').replace('\\"', '"').strip()
            if len(s_clean) > 20 and len(s_clean) < 500:
                print(f"- {s_clean}")
                
except Exception as e:
    print(f"Error: {e}")
