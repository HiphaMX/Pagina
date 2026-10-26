import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_amdi_contacto_submit_no_token():
    # Enviar formulario sin token de reCAPTCHA (debe detectarse como spam silencioso)
    payload = {
        "nombre": "Test Name",
        "apellido": "Test Surname",
        "email": "test@example.com",
        "telefono": "1234567890",
        "mensaje": "Mensaje de prueba para AMDI"
    }
    response = client.post("/api/contact/amdi/contacto", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario de contacto recibido correctamente"}

def test_amdi_contacto_submit_with_token():
    # Enviar formulario con token (debería pasar la validación y procesarse)
    payload = {
        "nombre": "Test Name",
        "apellido": "Test Surname",
        "email": "test@example.com",
        "telefono": "1234567890",
        "mensaje": "Mensaje de prueba para AMDI",
        "recaptcha_token": "dummy_valid_token"
    }
    response = client.post("/api/contact/amdi/contacto", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario de contacto recibido correctamente"}

def test_amdi_contacto_submit_with_honeypot():
    # Enviar formulario con campo honeypot lleno (debe detectarse como spam silencioso)
    payload = {
        "nombre": "Test Name",
        "apellido": "Test Surname",
        "email": "test@example.com",
        "telefono": "1234567890",
        "mensaje": "Mensaje de prueba para AMDI",
        "honeypot": "spam_bot_website",
        "recaptcha_token": "dummy_valid_token"
    }
    response = client.post("/api/contact/amdi/contacto", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario de contacto recibido correctamente"}

def test_amdi_newsletter_submit_no_token():
    payload = {
        "nombre": "Test Subscriber",
        "email": "subscriber@example.com"
    }
    response = client.post("/api/contact/amdi/newsletter", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Suscripción a newsletter recibida correctamente"}

def test_amdi_newsletter_submit_with_token():
    payload = {
        "nombre": "Test Subscriber",
        "email": "subscriber@example.com",
        "recaptcha_token": "dummy_valid_token"
    }
    response = client.post("/api/contact/amdi/newsletter", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Suscripción a newsletter recibida correctamente"}

def test_amdi_newsletter_submit_with_honeypot():
    payload = {
        "nombre": "Test Subscriber",
        "email": "subscriber@example.com",
        "honeypot": "some_value",
        "recaptcha_token": "dummy_valid_token"
    }
    response = client.post("/api/contact/amdi/newsletter", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Suscripción a newsletter recibida correctamente"}

def test_amdi_mailer_recipients_and_sender(monkeypatch):
    import asyncio
    from app.core import mailer
    from app.api.projects.amdi import AMDIContactoForm
    
    sent_messages = []
    async def mock_send_smtp(message, **kwargs):
        sent_messages.append((message, kwargs))
        return True

    monkeypatch.setattr(mailer, "_send_smtp", mock_send_smtp)
    # Ensure SMTP settings simulate configured environment
    monkeypatch.setattr(mailer.settings, "SMTP_HOST", "smtp.test.com")
    monkeypatch.setattr(mailer.settings, "SMTP_USER", "test@test.com")

    async def run_checks():
        # 1. Contact Confirmation to Customer
        form_data = AMDIContactoForm(
            nombre="Juan",
            apellido="Pérez",
            email="cliente@example.com",
            telefono="3312345678",
            mensaje="Hola proyecto"
        )
        sent_messages.clear()
        res = await mailer.send_amdi_contact_confirmation_email(form_data)
        assert res is True
        assert len(sent_messages) == 1
        msg, _ = sent_messages[0]
        assert msg["To"] == "cliente@example.com"
        assert "contacto@amdi.mx" in (msg["From"] or "") or msg["Reply-To"] == "contacto@amdi.mx"

        # 2. Contact Notification to Team
        sent_messages.clear()
        res_team = await mailer.send_amdi_contact_notification_team(form_data)
        assert res_team is True
        team_recipients = [m[0]["To"] for m in sent_messages]
        assert "contacto@amdi.mx" in team_recipients
        assert "hola@hipha.mx" in team_recipients
        for m, _ in sent_messages:
            assert m["Reply-To"] == "cliente@example.com"

        # 3. Newsletter Notification to Team
        sent_messages.clear()
        res_news = await mailer.send_amdi_newsletter_notification_team("nuevo@example.com")
        assert res_news is True
        news_recipients = [m[0]["To"] for m in sent_messages]
        assert "contacto@amdi.mx" in news_recipients
        assert "hola@hipha.mx" in news_recipients

    asyncio.run(run_checks())

def test_amdi_aviso_privacidad_content():
    with open("projects/AMDI/aviso-de-privacidad.html", "r", encoding="utf-8") as f:
        content = f.read()
    assert "www.dis-interior.com" not in content
    assert "www.amdi.mx" in content
    assert "marketing@adrianamedina.com.mx" not in content
    assert "creativo@amdi.mx" not in content
    assert "contacto@amdi.mx" in content

def test_amdi_css_animation_styles():
    with open("projects/AMDI/css/amdi-2022.webflow.shared.da6bb9481.min.css", "r", encoding="utf-8") as f:
        css = f.read()
    assert ".article-title-bg-anim{background-color:#000000 !important;background-image:none !important;" in css
    assert "color:#ffffff !important;text-decoration-color:#ffffff !important;" in css

def test_amdi_preguntas_frecuentes_accordion():
    from html.parser import HTMLParser
    with open("projects/AMDI/preguntas-frecuentes.html", "r", encoding="utf-8") as f:
        html = f.read()

    assert 'data-wf-page="63976d0ddbb87185365a14e8"' in html
    assert 'data-wf-site="62cc8b1fa4113031cfe18e42"' in html

    class AccordionChecker(HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_faq_section = False
            self.depth = 0
            self.direct_accordions = []
            self.nested_accordions = []
        def handle_starttag(self, tag, attrs):
            d = dict(attrs)
            classes = d.get("class", "").split()
            if tag == "section" and "bg-white" in classes:
                self.in_faq_section = True
                self.depth = 0
                return
            if self.in_faq_section:
                self.depth += 1
                if tag == "div" and "accordion" in classes and "w-dropdown" in classes:
                    if self.depth == 1:
                        self.direct_accordions.append(d)
                    else:
                        self.nested_accordions.append(d)
        def handle_endtag(self, tag):
            if self.in_faq_section:
                if self.depth == 0 and tag == "section":
                    self.in_faq_section = False
                else:
                    self.depth -= 1

    checker = AccordionChecker()
    checker.feed(html)
    assert len(checker.direct_accordions) == 8, f"Esperados 8 acordeones directos, encontrados {len(checker.direct_accordions)}"
    assert len(checker.nested_accordions) == 0, f"No debe haber acordeones anidados, encontrados {len(checker.nested_accordions)}"

def test_amdi_mobile_logo_centering_css():
    with open("projects/AMDI/css/amdi-2022.webflow.shared.da6bb9481.min.css", "r", encoding="utf-8") as f:
        css = f.read()
    assert "@media screen and (max-width:991px)" in css
    assert ".nav-menu-2{display:none !important}" in css
    assert "left:50% !important;top:50% !important;transform:translate(-50%,-50%) !important" in css

def test_amdi_search_page_and_handler():
    with open("projects/AMDI/search.html", "r", encoding="utf-8") as f:
        html = f.read()
    assert 'class="search-result-items"' in html
    assert 'js/search-handler.js' in html

    with open("projects/AMDI/js/search-handler.js", "r", encoding="utf-8") as f:
        js = f.read()
    assert "AMDI Search Handler Initialized." in js
    assert "siteIndex" in js
    assert "residencia-antares-areas-comunes" in js
    assert "residencia-jesus-maria-areas-comunes" in js
    assert "expo-obra-blanca-2023-cdmx" in js
    assert "luz-natural-y-artificial-el-equilibrio-perfecto" in js
    assert "normalize(str)" in js
    assert "executeSearch" in js


