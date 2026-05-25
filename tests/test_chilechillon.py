import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_submit_chilechillon_form_success():
    client = TestClient(app)
    response = client.post(
        "/api/contact/chilechillon",
        json={
            "nombre": "Test User",
            "apellido": "De Prueba",
            "email": "test@elchilechillon.com.mx",
            "telefono": "+52 33 1234 5678",
            "perfil": "usuario_final",
            "mensaje": "Me encantan sus salsas gourmet!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Formulario recibido correctamente"

def test_submit_chilechillon_form_invalid_email():
    client = TestClient(app)
    response = client.post(
        "/api/contact/chilechillon",
        json={
            "nombre": "Test User",
            "apellido": "",
            "email": "invalid-email",
            "telefono": "+52 33 1234 5678",
            "perfil": "usuario_final",
            "mensaje": ""
        }
    )
    assert response.status_code == 422 # Validation Error
