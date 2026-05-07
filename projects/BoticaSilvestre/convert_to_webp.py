import os
import glob
from PIL import Image

def convert_to_webp(directory):
    for ext in ('*.jpg', '*.jpeg', '*.png', '*/*.jpg', '*/*/*.jpg', '*/*.png', '*/*/*.png'):
        for path in glob.glob(os.path.join(directory, ext)):
            if not os.path.isfile(path):
                continue
            
            webp_path = os.path.splitext(path)[0] + '.webp'
            try:
                with Image.open(path) as img:
                    # Convert to RGB if saving as webp and image is RGBA but has no transparency, 
                    # but webp supports RGBA natively!
                    img.save(webp_path, 'webp', quality=85)
                print(f"Converted {path} to {webp_path}")
                os.remove(path)
            except Exception as e:
                print(f"Error converting {path}: {e}")

if __name__ == '__main__':
    convert_to_webp('projects/BoticaSilvestre/web/assets/images')
