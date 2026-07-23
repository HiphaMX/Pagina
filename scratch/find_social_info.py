import json
import re

log_path = "/Users/fanssimarketingdigital/.gemini/antigravity/brain/611629f3-2d18-479a-9cfd-c2607d95d7fc/.system_generated/logs/transcript.jsonl"
print(f"Reading logs from: {log_path}")

whatsapp_numbers = set()
instagram_links = set()
facebook_links = set()

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get("content", "")
            if not content and "tool_calls" in data:
                content = str(data["tool_calls"])
            
            # Look for whatsapp numbers or api.whatsapp.com/send or wa.me
            wa_matches = re.findall(r'(?:wa\.me|api\.whatsapp\.com/send\S*|whatsapp\S*|whatsapp\s+de\s+\S+|whatsapp\s*:\s*\S+)', content, re.IGNORECASE)
            for m in wa_matches:
                whatsapp_numbers.add(m)
                
            inst_matches = re.findall(r'(?:instagram\.com/\S+|instagram\S*)', content, re.IGNORECASE)
            for m in inst_matches:
                instagram_links.add(m)
                
            fb_matches = re.findall(r'(?:facebook\.com/\S+|facebook\S*)', content, re.IGNORECASE)
            for m in fb_matches:
                facebook_links.add(m)
                
        except Exception as e:
            pass

print("WhatsApp info found:")
for item in whatsapp_numbers:
    print("  ", item)
    
print("\nInstagram info found:")
for item in instagram_links:
    print("  ", item)
    
print("\nFacebook info found:")
for item in facebook_links:
    print("  ", item)
