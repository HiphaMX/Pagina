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
