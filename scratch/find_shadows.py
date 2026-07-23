import os
from PIL import Image

salsas_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/ChileChillon/web/Assets/Salsas"
files = [f for f in os.listdir(salsas_dir) if f.lower().endswith(('.jpeg', '.jpg'))]

for f in files:
    path = os.path.join(salsas_dir, f)
    with Image.open(path) as img:
        print(f"File: {f}")
        # Sample bottom rows
        w, h = img.size
        # Get pixels from the bottom 10% of the image (from y = h-200 to h-1, at x = w//2)
        center_x = w // 2
        bottom_pixels = [img.getpixel((center_x, y)) for y in range(h - 200, h, 20)]
        print(f"  Bottom center pixels (y from h-200 to h-1): {bottom_pixels}")
