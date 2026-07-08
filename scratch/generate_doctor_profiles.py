import os
import re

andropausia_path = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada/blog/andropausia.html"
target_dir = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada/blog"

# Read the template from andropausia.html
with open(andropausia_path, "r", encoding="utf-8") as f:
    template = f.read()

# Define the data for Dr. Belisario
title_belisario = "Dr. Belisario Torres Alvarado | Urólogo en Morelia"
desc_belisario = "El Dr. Belisario Torres Alvarado es médico cirujano y partero fundador del Centro de Urología Avanzada, especialista en urología en Morelia, Michoacán."
content_belisario = """<h2>Historial Académico</h2>
<ul>
  <li><strong>Médico Cirujano y Partero:</strong> Facultad de Medicina "Dr. Ignacio Chávez" (1988–1995).</li>
  <li><strong>Especialidad en Urología:</strong> Hospital Juárez de México (1996–2001).</li>
  <li><strong>Título de Subespecialidad:</strong> Cirujano Urólogo (obtenido a través de la UNAM en 2007).</li>
  <li><strong>Recertificaciones:</strong> Cuenta con cinco recertificaciones consecutivas ante el consejo correspondiente (2000–2025).</li>
</ul>
<h2>Actividad Docente y Profesional</h2>
<ul>
  <li>Médico adscrito al servicio de urología del Hospital General "Dr. Miguel Silva" en Morelia desde 2001.</li>
  <li>Speaker del laboratorio Boehringer Ingelheim Promeco (desde 2006).</li>
  <li>Coordinador de internos en el bloque de cirugía general, Hospital General "Dr. Miguel Silva" (2008–2013).</li>
  <li>Secretario Académico de la Sociedad Michoacana de Urología (2012–2013).</li>
  <li>Profesor adjunto de la subespecialidad de urología en el Hospital Regional "Dr. Valentín Gómez Farías" del ISSSTE en Guadalajara (desde 2012).</li>
  <li>Docente en el curso post-básico de especialidad en enfermería quirúrgica (asignatura de urología) y profesor asociado del PRONADAMEG (módulo de urología).</li>
</ul>"""

# Define the data for Dr. Adalberto
title_adalberto = "Dr. Adalberto Castro Alfaro | Cirugía Robótica"
desc_adalberto = "El Dr. Adalberto Castro Alfaro es urólogo especialista con alta especialidad en urología oncológica y cirugía robótica, con doble especialidad y formación en Francia."
content_adalberto = """<h2>Perfil Profesional</h2>
<ul>
  <li>Uno de los pocos urólogos en México con doble especialidad.</li>
  <li><strong>Especialidad en Urología:</strong> Hospital Regional "Dr. Valentín Gómez Farías" (ISSSTE) / Universidad de Guadalajara.</li>
  <li><strong>Alta Especialidad:</strong> Urología Oncológica en el Instituto Nacional de Cancerología (INCan), CDMX.</li>
  <li><strong>Formación Internacional:</strong> Fellowship en Cirugía Robótica y laparoscopia avanzada, Institut Mutualiste Montsouris, Universidad París Descartes, París, Francia.</li>
  <li><strong>Certificación:</strong> Certificado por el Consejo Nacional Mexicano de Urología, A.C.</li>
</ul>
<h2>Distinciones y Membresías</h2>
<ul>
  <li>Miembro de la European Urological Association (EUA).</li>
  <li>Miembro de la American Urological Association (AUA).</li>
  <li>Miembro de la Sociedad Mexicana de Urología.</li>
  <li>Miembro del Colegio Mexicano de Urología A.C.</li>
  <li>Miembro de la Sociedad Médica del Hospital Ángeles Lomas.</li>
</ul>"""

def generate_profile(filename, title, description, content):
    # Copy template
    html = template
    
    # Replace metadata
    html = re.sub(r'<title>[^<]+</title>', f'<title>{title} | Centro de Urología Avanzada</title>', html)
    
    # Replace meta description
    html = re.sub(r'<meta content="[^"]+" name="description"', f'<meta content="{description}" name="description"', html)
    html = re.sub(r'<meta content="[^"]+" property="og:description"', f'<meta content="{description}" property="og:description"', html)
    html = re.sub(r'<meta content="[^"]+" name="twitter:description"', f'<meta content="{description}" name="twitter:description"', html)
    
    # Replace meta title
    html = re.sub(r'<meta content="[^"]+" property="og:title"', f'<meta content="{title}" property="og:title"', html)
    html = re.sub(r'<meta content="[^"]+" name="twitter:title"', f'<meta content="{title}" name="twitter:title"', html)
    
    # Replace data-wf-item-slug
    html = html.replace('data-wf-item-slug="andropausia"', f'data-wf-item-slug="{filename[:-5]}"')
    
    # Replace content of the blog post
    # In template, we have: <h1 class="titulos">Andropausia</h1><div class="rich-text-block w-richtext">...</div><div class="w-dyn-list">
    # Let's target this specific block and replace it
    pattern = r'<h1 class="titulos">Andropausia</h1><div class="rich-text-block w-richtext">[\s\S]*?</div><div class="w-dyn-list">'
    replacement = f'<h1 class="titulos">{title}</h1><div class="rich-text-block w-richtext">{content}</div><div class="w-dyn-list">'
    
    html = re.sub(pattern, replacement, html)
    
    # Save file
    save_path = os.path.join(target_dir, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated profile page at {save_path}")

if __name__ == "__main__":
    generate_profile("belisario-torres-alvarado-urologo.html", title_belisario, desc_belisario, content_belisario)
    generate_profile("dr-adalberto-castro-alfaro-urologo.html", title_adalberto, desc_adalberto, content_adalberto)
