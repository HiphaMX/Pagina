import re

with open("watchhouse_body.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's search for all element tags that have class or id containing 'menu' or 'nav' or 'drawer'
elements = re.findall(r'<[a-zA-Z0-9\-]+[^>]*?(?:class|id)="[^"]*?(?:menu|nav|drawer|header)[^"]*?"[^>]*>', html)
print(f"Found {len(elements)} matching tags:")
for el in elements[:40]:
    print(el)

# Search for toggle-button tags
toggles = re.findall(r'<toggle-button[^>]*>([\s\S]*?)</toggle-button>', html)
print(f"\nFound {len(toggles)} toggle-buttons:")
for t in toggles[:10]:
    print(t[:300].strip())
