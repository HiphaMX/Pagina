import os
from PIL import Image

salsas_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/ChileChillon/web/Assets/Salsas"
jpeg_name = "Salsa Habanero.jpeg"
jpeg_path = os.path.join(salsas_dir, jpeg_name)

with Image.open(jpeg_path) as img:
    img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
    w, h = img.size
    print(f"Image size: {w}x{h}")
    # Sample pixels at y = 925 (which corresponds to row 37 in 40x40 grid)
    # across x from 200 to 800 in steps of 50
    y = int(h * 37 / 40)
    print(f"Sampling colors at y = {y}:")
    for x in range(200, 800, 50):
        color = img.getpixel((x, y))
        print(f"  x={x} -> {color}")
