import os
from PIL import Image

salsas_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/ChileChillon/web/Assets/Salsas"
webp_name = "habanero.webp"
webp_path = os.path.join(salsas_dir, webp_name)

if os.path.exists(webp_path):
    with Image.open(webp_path) as img:
        w, h = img.size
        # Resize to 40x40 to print
        img_small = img.resize((40, 40), Image.Resampling.NEAREST)
        print("Alpha channel grid (40x40):")
        print("'.' = transparent, '#' = solid")
        for y in range(40):
            row = ""
            for x in range(40):
                alpha = img_small.getpixel((x, y))[3]
                if alpha < 128:
                    row += "."
                else:
                    row += "#"
            print(row)
else:
    print(f"{webp_name} not found!")
