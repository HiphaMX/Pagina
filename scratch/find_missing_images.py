import os
import re

target_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada"
assets_dir = os.path.join(target_dir, "assets")
blog_dir = os.path.join(target_dir, "blog")

new_files = [
    "belisario-torres-alvarado-urologo.html",
    "dr-adalberto-castro-alfaro-urologo.html"
]

def check_missing_assets():
    missing = []
    found_assets = set()
    
    for filename in new_files:
        filepath = os.path.join(blog_dir, filename)
        if not os.path.exists(filepath):
            print(f"File {filepath} does not exist!")
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find all references to assets (e.g. ../../assets/...)
        # We search for href="../../assets/..." and src="../../assets/..."
        for match in re.finditer(r'(href|src)="\.\./\.\./assets/([^"]+)"', content):
            asset_name = match.group(2)
            found_assets.add(asset_name)
            
    for asset in found_assets:
        asset_path = os.path.join(assets_dir, asset)
        if not os.path.exists(asset_path):
            missing.append(asset)
            
    return found_assets, missing

if __name__ == "__main__":
    found, missing = check_missing_assets()
    print(f"Total unique assets found in doctor profiles: {len(found)}")
    print(f"Missing assets: {len(missing)}")
    for m in missing:
        print(f"  - {m}")
