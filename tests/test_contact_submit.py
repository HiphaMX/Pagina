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

