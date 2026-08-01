import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ----------------- Chile Chillón -----------------
def test_chilechillon_contacto_submit():
    # Enviar formulario sin token de reCAPTCHA (spam silencioso / fallback exitoso)
    payload = {
        "nombre": "Test",
        "apellido": "User",
        "email": "test@chilechillon.com",
        "telefono": "3312345678",
        "perfil": "consumidor",
        "mensaje": "Mensaje de prueba"
    }
    response = client.post("/api/contact/chilechillon", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

    # Enviar con honeypot (spam silencioso)
    payload["honeypot"] = "bot_val"
    response = client.post("/api/contact/chilechillon", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

def test_chilechillon_quiniela_register():
    payload = {
        "nombre": "Test Quiniela",
        "email": "quiniela@chilechillon.com",
        "telefono": "3312345678",
        "prediccion_campeon": "México"
    }
    response = client.post("/api/contact/chilechillon/quiniela/register", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Participante registrado exitosamente"}

# ----------------- Grupo Gari -----------------
def test_grupogari_submit():
    payload = {
        "nombre": "Gari Test",
        "apellido": "Test",
        "email": "test@grupogari.com",
        "telefono": "1234567890",
        "rol": "hr",
        "empleados": "1-50",
        "industria": "manufactura",
        "servicio": "Proteccion Civil",
        "mensaje": "Prueba"
    }
    response = client.post("/api/contact/grupogari", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

    # Enviar con honeypot
    payload["honeypot"] = "gari_bot"
    response = client.post("/api/contact/grupogari", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

# ----------------- HealthyIce -----------------
def test_healthyice_submit():
    payload = {
        "nombre": "Ice Test",
        "email": "test@healthyice.com",
        "telefono": "1234567890",
        "mensaje": "Prueba de helados"
    }
    response = client.post("/api/contact/healthyice", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

# ----------------- Jessica Mendoza -----------------
def test_jessica_mendoza_submit():
    payload = {
        "nombre": "Jessica Test",
        "apellido": "Test",
        "email": "test@jessicamendoza.com",
        "telefono": "1234567890",
        "intencion": "comprar",
        "propiedad": "casa",
        "mensaje": "Prueba de bienes raices"
    }
    response = client.post("/api/contact/jessica-mendoza", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

# ----------------- Valencia Servicios -----------------
def test_valencia_servicios_submit():
    payload = {
        "nombre_completo": "Valencia Test",
        "telefono": "1234567890",
        "servicio_requerido": "aire acondicionado",
        "direccion": "Direccion de prueba",
        "horario_preferido": "matutino"
    }
    response = client.post("/api/contact/valencia-servicios", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

# ----------------- WhiteClean -----------------
def test_whiteclean_submit():
    payload = {
        "nombre": "White Test",
        "apellido": "Test",
        "email": "test@whiteclean.com",
        "telefono": "1234567890",
        "servicio": "limpieza alfombras",
        "ubicacion": "Zapopan",
        "mensaje": "Prueba de limpieza"
    }
    response = client.post("/api/contact/whiteclean", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

# ----------------- Central HiphaMX -----------------
def test_hiphamx_submit():
    payload = {
        "nombre": "Hipha Test",
        "email": "test@hipha.mx",
        "telefono": "1234567890",
        "mensaje": "Prueba central Hipha"
    }
    response = client.post("/api/contact/submit", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}

def test_hiphamx_newsletter():
    payload = {
        "email": "newsletter@hipha.mx"
    }
    response = client.post("/api/contact/newsletter", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Suscripción exitosa"}

# ----------------- Letrerama -----------------
def test_letrerama_submit():
    payload = {
        "nombre": "Letrerama Test",
        "telefono": "1234567890",
        "email": "test@letrerama.com",
        "tiene_vector": "SI",
        "tecnica": "acrilico",
        "medida_ancho": 100.0,
        "medida_alto": 50.0,
        "iluminacion": "neon",
        "material": "PVC",
        "altura_instalacion": 2.5,
        "direccion_instalacion": "Direccion letrero",
        "privacidad": True
    }
    response = client.post("/api/contact/letrerama", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Formulario recibido correctamente"}
