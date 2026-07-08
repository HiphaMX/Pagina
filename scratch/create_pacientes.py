import re

diagnostico_path = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada/diagnostico.html"
pacientes_path = "/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/urologia-avanzada/pacientes.html"

with open(diagnostico_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Let's extract everything from <!DOCTYPE html> up to <div id="centro-de-urologia-avanzad">
head_match = re.search(r'([\s\S]*?<div id="centro-de-urologia-avanzad">)', html)
if not head_match:
    head_match = re.search(r'([\s\S]*?<div class="blog-cuerpo">)', html)

# Let's extract the footer: from <div id="footer" class="footer"> to the end of the file
footer_match = re.search(r'(<div id="footer" class="footer">[\s\S]*)', html)

if head_match and footer_match:
    head = head_match.group(1)
    footer = footer_match.group(1)
    
    # We want to change the active tab in the navbar.
    # In diagnostico.html:
    # <a href="/diagnostico" aria-current="page" class="nav-link w-nav-link w--current">Diagnóstico</a>
    # <a href="/pacientes" class="nav-link w-nav-link">Pacientes</a>
    # Let's swap the current status:
    head = head.replace('href="/diagnostico" aria-current="page" class="nav-link w-nav-link w--current"', 'href="/diagnostico" class="nav-link w-nav-link"')
    head = head.replace('href="/pacientes" class="nav-link w-nav-link"', 'href="/pacientes" aria-current="page" class="nav-link w-nav-link w--current"')
    
    # Let's change the title in head
    head = re.sub(r'<title>[^<]+</title>', '<title>Pacientes | Centro de Urología Avanzada</title>', head)
    
    # Custom content for Patients page
    middle = """
        <div class="container-3 w-container">
            <h1 class="titulos">Área de Pacientes</h1>
            <p class="txto-web">Esta sección se encuentra restringida temporalmente o en proceso de mantenimiento.</p>
            <div style="max-width: 500px; margin: 50px auto; padding: 30px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; text-align: center;">
                <h3 class="titulos-2" style="margin-bottom: 20px;">Acceso Protegido</h3>
                <p class="txto-web-2" style="font-size: 14px; margin-bottom: 20px;">Para acceder a sus resultados o información de paciente, por favor contacte directamente al consultorio.</p>
                <a href="https://api.whatsapp.com/send?phone=524432019937" target="_blank" class="contacto0 w-button" style="display: inline-block; position: static;">CONTACTAR POR WHATSAPP</a>
            </div>
        </div>
    </div>
    """
    
    pacientes_html = head + middle + footer
    with open(pacientes_path, 'w', encoding='utf-8') as f:
        f.write(pacientes_html)
    print("pacientes.html created successfully!")
else:
    print("Could not find head/footer in diagnostico.html")
