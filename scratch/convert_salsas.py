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
max_size = 1000
threshold = 65
for jpeg_name, webp_name in mapping.items():
    jpeg_path = os.path.join(salsas_dir, jpeg_name)
    webp_path = os.path.join(salsas_dir, webp_name)
    
    if not os.path.exists(jpeg_path):
        print(f"Error: {jpeg_name} not found at {jpeg_path}")
        continue
        
    print(f"Processing {jpeg_name} -> {webp_name}...")
    
    with Image.open(jpeg_path) as img:
        # Resize first (maintaining aspect ratio)
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to RGBA
        img_rgba = img.convert("RGBA")
        w, h = img_rgba.size
        
        # Flood fill from the four corners to make background transparent
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        for start_xy in corners:
            # We floodfill with a transparent pixel (0, 0, 0, 0)
            # The background color is sampled from the corner itself
            ImageDraw.floodfill(img_rgba, start_xy, (0, 0, 0, 0), thresh=threshold)
            
        # Save as WebP with high quality
        img_rgba.save(webp_path, "WEBP", quality=85)
        print(f"  Saved to {webp_path} (Size: {img_rgba.size})")

print("Done conversion!")
