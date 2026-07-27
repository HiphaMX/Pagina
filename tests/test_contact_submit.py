import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_contact_submit_contract_with_plan():
    # Test contract submission with the new "plan_contratado" field
    payload = {
        "nombre": "Juan Pérez Test",
        "email": "juan.test@example.com",
        "telefono": "+52 55 1234 5678",
        "mensaje": "ACEPTACIÓN DE CONTRATO VÍA WEB.\n\nFecha de aceptación: 2026-06-15\nDía de pago comprometido: 5\nProyecto: Mi Súper Web\nPlan contratado: WEB\nForma de pago elegida: Transferencia electrónica\n\nEl cliente ha marcado la casilla aceptando los términos.",
        "firma": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", # 1x1 black pixel PNG
        "fecha": "2026-06-15",
        "fecha_pago": "5",
        "proyecto": "Mi Súper Web",
        "forma_pago": "Transferencia electrónica",
        "plan_contratado": "WEB"
    }

    response = client.post("/api/contact/submit", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

def test_format_spanish_date():
    from app.core.mailer import format_spanish_date
    assert format_spanish_date("2026-06-15") == "15 de junio de 2026"
    assert format_spanish_date("2026-01-01") == "1 de enero de 2026"
    assert format_spanish_date("15 de junio de 2026") == "15 de junio de 2026"
    assert format_spanish_date("") == "N/A"
    assert format_spanish_date(None) == "N/A"

def test_letrerama_quote_submit():
    payload = {
        "nombre": "Test Cliente",
        "telefono": "5512345678",
        "email": "test@letrerama.com",
        "empresa": "Letrerama Test Corp",
        "tiene_vector": "SI",
        "logo_base64": "data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=",
        "logo_filename": "logo.svg",
        "tecnica": "Logotipo 3D",
        "medida_ancho": 120.5,
        "medida_alto": 80.0,
        "medida_canto": 5.0,
        "iluminacion": "Retroiluminado",
        "material": "Aluminio cepillado",
        "altura_instalacion": 2.5,
        "direccion_instalacion": "Av. Reforma 123, CDMX",
        "privacidad": True
    }
    response = client.post("/api/contact/letrerama", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

def test_contact_submit_with_honeypot():
    # Test submitting Hipha contact form with honeypot field filled (bot detected)
    payload = {
        "nombre": "Bot Spammer",
        "email": "spammer@bot.com",
        "telefono": "0000000000",
        "mensaje": "I am a bot",
        "honeypot": "iamabot"
    }
    response = client.post("/api/contact/submit", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

def test_letrerama_quote_submit_with_honeypot():
    # Test Letrerama form with honeypot field filled
    payload = {
        "nombre": "Bot Letrerama",
        "telefono": "0000000000",
        "email": "spammer@bot.com",
        "tiene_vector": "NO",
        "tecnica": "Logotipo 3D",
        "medida_ancho": 10,
        "medida_alto": 10,
        "iluminacion": "Sin luz",
        "material": "Acrílico",
        "altura_instalacion": 1.0,
        "direccion_instalacion": "Internet",
        "privacidad": True,
        "honeypot": "botspammer"
    }
    response = client.post("/api/contact/letrerama", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

def test_qa_validate_smtp():
    # Test SMTP diagnostic route
    response = client.get("/api/qa/validate-smtp")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "report" in data
    assert len(data["report"]) > 0



