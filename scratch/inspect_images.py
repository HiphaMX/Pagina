import os
from PIL import Image

salsas_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/ChileChillon/web/Assets/Salsas"
files = [f for f in os.listdir(salsas_dir) if f.lower().endswith(('.jpeg', '.jpg'))]

for f in files:
    path = os.path.join(salsas_dir, f)
    with Image.open(path) as img:
        print(f"File: {f}")
        print(f"  Size: {img.size}")
        print(f"  Format: {img.format}")
        print(f"  Mode: {img.mode}")
        # Get corner pixels
        w, h = img.size
        corners = [
            img.getpixel((0, 0)),
            img.getpixel((w - 1, 0)),
            img.getpixel((0, h - 1)),
            img.getpixel((w - 1, h - 1))
        ]
        print(f"  Corners: {corners}")
