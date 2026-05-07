import os
import glob

def bump_cache():
    directory = 'projects/BoticaSilvestre/web'
    
    # Files to check
    extensions = ('*.html',)
    files_to_process = []
    for ext in extensions:
        files_to_process.extend(glob.glob(os.path.join(directory, ext)))
        
    for filepath in files_to_process:
        if not os.path.isfile(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content.replace('?v=8', '?v=9')
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Bumped cache in {filepath}")

if __name__ == '__main__':
    bump_cache()
