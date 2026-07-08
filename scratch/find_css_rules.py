import re

css_path = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada/assets/assets_urologia-avanzada.webflow.shared.c04e52d57.min.css"

with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# Search for column class definitions
# e.g. .column{...} or .column-2{...} or .column-3{...}
for cls in [".column", ".column-2", ".column-3"]:
    # Find all matches of this class in the CSS
    pattern = re.escape(cls) + r'\b[^}]*}'
    matches = re.findall(pattern, css)
    print(f"Matches for {cls}:")
    for m in matches:
        print(f"  {m}")
