import os
from PIL import Image, ImageDraw

salsas_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/ChileChillon/web/Assets/Salsas"
jpeg_name = "Salsa Habanero.jpeg"
jpeg_path = os.path.join(salsas_dir, jpeg_name)

for thresh in [30, 50, 70, 90]:
    with Image.open(jpeg_path) as img:
        img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
        img_rgba = img.convert("RGBA")
        w, h = img_rgba.size
        
        # Flood fill from corners
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        for start_xy in corners:
            ImageDraw.floodfill(img_rgba, start_xy, (0, 0, 0, 0), thresh=thresh)
            
        # Check bottom center pixels alpha channel
        center_x = w // 2
        bottom_alphas = [img_rgba.getpixel((center_x, y))[3] for y in range(h - 100, h, 10)]
        print(f"Threshold: {thresh} -> Bottom alphas: {bottom_alphas}")
