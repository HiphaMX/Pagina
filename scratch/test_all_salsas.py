import os
from PIL import Image, ImageDraw

salsas_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/ChileChillon/web/Assets/Salsas"

# Map JPEG names to the target WebP names expected by the frontend
mapping = {
    "Salsa Chile de Árbol.jpeg": "de_arbol.webp",
    "Salsa Habanero.jpeg": "habanero.webp",
    "Salsa Habanero Tatemado.jpeg": "tatemado.webp",
    "Salsa Negra.jpeg": "negra.webp",
    "Salsa Serrano.jpeg": "serrano.webp"
}

for jpeg_name, webp_name in mapping.items():
    jpeg_path = os.path.join(salsas_dir, jpeg_name)
    with Image.open(jpeg_path) as img:
        img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
        img_rgba = img.convert("RGBA")
        w, h = img_rgba.size
        
        # We try threshold 65
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        for start_xy in corners:
            ImageDraw.floodfill(img_rgba, start_xy, (0, 0, 0, 0), thresh=65)
            
        img_small = img_rgba.resize((40, 40), Image.Resampling.NEAREST)
        print(f"\nGrid for {jpeg_name} at threshold 65:")
        for y in range(32, 40):
            row = ""
            for x in range(40):
                alpha = img_small.getpixel((x, y))[3]
                if alpha < 128:
                    row += "."
                else:
                    row += "#"
            print(f"y={y:02d}: {row}")
