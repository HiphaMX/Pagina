with open("watchhouse_style_1.css", "r", encoding="utf-8") as f:
    css1 = f.read()
with open("watchhouse_style_2.css", "r", encoding="utf-8") as f:
    css2 = f.read()

import re

# Look for header-menu, header-submenu, or toggle-element rules
for i, css in enumerate([css1, css2]):
    print(f"\n=== CSS {i+1} ANALYSIS ===")
    matches = re.finditer(r'([^\}\{]*header\-(?:menu|submenu|toolbar|announce)[^\}\{]*\{[\s\S]*?\})', css)
    count = 0
    for m in matches:
        count += 1
        print(f"Match {count}:")
        print(m.group(0).strip())
        print("-" * 50)
        if count >= 30:
            print("Truncated...")
            break
