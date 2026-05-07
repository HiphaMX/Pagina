import os
import glob

def replace_in_files():
    directory = 'projects/BoticaSilvestre/web'
    
    # Files to check
    extensions = ('*.html', 'css/*.css', 'js/*.js')
    files_to_process = []
    for ext in extensions:
        files_to_process.extend(glob.glob(os.path.join(directory, ext)))
        
    for filepath in files_to_process:
        if not os.path.isfile(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replace image extensions
        # We need to be careful not to replace random occurrences, but since we converted all jpg/jpeg/png
        # inside assets/images, replacing .jpg, .jpeg, .png with .webp is mostly safe.
        
        # We will do case-insensitive replace? No, just the common ones.
        new_content = content.replace('.jpg', '.webp')
        new_content = new_content.replace('.jpeg', '.webp')
        new_content = new_content.replace('.png', '.webp')
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated references in {filepath}")

if __name__ == '__main__':
    replace_in_files()
