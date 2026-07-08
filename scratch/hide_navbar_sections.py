import os
import re

target_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada"

def modify_navbar_in_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    modified = content
    
    # 1. Match "Pacientes" link with any classes, current state, or attributes
    pacientes_pattern = r'<a\s+[^>]*href="[^"]*pacientes[^"]*"[^>]*>Pacientes</a>'
    modified, count_pacientes = re.subn(pacientes_pattern, '', modified, flags=re.IGNORECASE)
    
    # 2. Match "Blog" link with any classes, current state, or attributes
    blog_pattern = r'<a\s+[^>]*href="[^"]*blog[^"]*"[^>]*>Blog</a>'
    modified, count_blog = re.subn(blog_pattern, '', modified, flags=re.IGNORECASE)
    
    if count_pacientes > 0 or count_blog > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(modified)
        print(f"Modified {os.path.basename(filepath)}: removed {count_pacientes} Pacientes links, {count_blog} Blog links.")
        return True
    return False

if __name__ == "__main__":
    count = 0
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                if modify_navbar_in_file(filepath):
                    count += 1
    print(f"\nTotal modified HTML files: {count}")
