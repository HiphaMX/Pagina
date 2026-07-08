import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_amdi_contacto_submit():
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

def test_amdi_newsletter_submit():
    payload = {
        "nombre": "Test Subscriber",
        "email": "subscriber@example.com"
    }
    response = client.post("/api/contact/amdi/newsletter", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Suscripción a newsletter recibida correctamente"}
