from PIL import Image
import sys
import os

def remove_bg(input_path, output_path, tolerance=15):
    img = Image.open(input_path).convert("RGBA")
    data = img.getdata()
    
    # Get background color from top-left pixel
    bg_color = data[0]
    
    newData = []
    for item in data:
        # Calculate distance
        if abs(item[0] - bg_color[0]) < tolerance and \
           abs(item[1] - bg_color[1]) < tolerance and \
           abs(item[2] - bg_color[2]) < tolerance:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
            
    img.putdata(newData)
    img.save(output_path, "PNG")

files = [
    "paleta_fresa.png",
    "paleta_chocolate.png",
    "paleta_cafe.png",
    "paleta_vainilla.png",
    "paleta_cookies_cream.png"
]

for f in files:
    path = os.path.join("/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/HealthyIce/public", f)
    remove_bg(path, path, tolerance=20)
    print(f"Processed {f}")

