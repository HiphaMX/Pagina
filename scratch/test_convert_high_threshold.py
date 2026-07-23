import os
from PIL import Image, ImageDraw

salsas_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/ChileChillon/web/Assets/Salsas"
jpeg_name = "Salsa Habanero.jpeg"
jpeg_path = os.path.join(salsas_dir, jpeg_name)

with Image.open(jpeg_path) as img:
    img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
    w, h = img.size
    
    # Try different thresholds
    for thresh in [35, 45, 55, 65]:
        img_rgba = img.convert("RGBA")
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        for start_xy in corners:
            ImageDraw.floodfill(img_rgba, start_xy, (0, 0, 0, 0), thresh=thresh)
            
        # Get 40x40 grid representation
        img_small = img_rgba.resize((40, 40), Image.Resampling.NEAREST)
        print(f"\nGrid for threshold {thresh}:")
        for y in range(35, 40):
            row = ""
            for x in range(40):
                alpha = img_small.getpixel((x, y))[3]
                if alpha < 128:
                    row += "."
                else:
                    row += "#"
            print(f"y={y:02d}: {row}")
