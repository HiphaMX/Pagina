import os
from PIL import Image

src_folder = "projects/ChileChillon/web/Assets/Salsas"
dst_folder = src_folder

# Map the filenames accurately
mapping = {
    "Salsa Chile de Árbol.jpeg": "de_arbol.jpg",
    "Salsa Habanero.jpeg": "habanero.jpg",
    "Salsa Habanero Tatemado.jpeg": "tatemado.jpg",
    "Salsa Negra.jpeg": "negra.jpg",
    "Salsa Serrano.jpeg": "serrano.jpg"
}

for src_name, dst_name in mapping.items():
    src_path = os.path.join(src_folder, src_name)
    dst_path = os.path.join(dst_folder, dst_name)
    
    if not os.path.exists(src_path):
        # Check standard name spelling if normalization is different
        normalized_name = src_name.replace("Á", "Á")
        src_path = os.path.join(src_folder, normalized_name)
        if not os.path.exists(src_path):
            print(f"Skipping {src_name}: File not found")
            continue
            
    print(f"Processing {src_path} -> {dst_path}...")
    img = Image.open(src_path)
    
    # Resize to 800x800
    img_resized = img.resize((800, 800), Image.Resampling.LANCZOS)
    
    # Save as JPEG with high quality and optimization to preserve shadows
    img_resized.save(dst_path, "JPEG", quality=90, optimize=True)
    print(f"Saved {dst_name} with size {os.path.getsize(dst_path)} bytes")

print("Done!")
