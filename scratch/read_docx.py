import zipfile
import xml.etree.ElementTree as ET

def get_docx_text(path):
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    try:
        with zipfile.ZipFile(path) as docx:
            tree = ET.fromstring(docx.read('word/document.xml'))
            paragraphs = []
            for paragraph in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                texts = [node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
                if texts:
                    paragraphs.append("".join(texts))
            return "\n".join(paragraphs)
    except Exception as e:
        return f"Error reading {path}: {str(e)}"

# Save Belisario CV
with open("/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/scratch/Dr_Belisario_CV.txt", "w", encoding="utf-8") as f:
    f.write(get_docx_text("/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada/assets/CV/Dr. Belizario CV.docx"))

# Save Adalberto CV
with open("/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/scratch/Dr_Adalberto_CV.txt", "w", encoding="utf-8") as f:
    f.write(get_docx_text("/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada/assets/CV/Dr. Adalberto CV.docx"))

print("Saved both CVs as txt files in scratch directory.")
