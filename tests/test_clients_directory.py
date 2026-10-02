import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from app.core.database import SessionLocal, Base, engine
from app.models.client import AgencyClient

client = TestClient(app)

mock_admin = UserSchema(
    id=1,
    email="hola@hipha.mx",
    is_active=True,
    is_superuser=True,
    full_name="Administrador Hipha"
)

@pytest.fixture(autouse=True)
def setup_db_and_auth():
    # Asegurar tablas
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin
    yield
    app.dependency_overrides.pop(get_current_active_user, None)


def test_clients_directory_crud():
    # 1. Crear nuevo cliente con requerimiento de factura e ISR
    payload = {
        "name": "Cliente Test Creativo",
        "contact_name": "Carlos Diseñador",
        "contact_email": "carlos@testcreativo.com",
        "contact_phone": "3331234567",
        "service_type": "design_subscription",
        "billing_period": "monthly",
        "billing_day": 22,
        "monthly_fee": 8500.0,
        "requires_invoice": True,
        "apply_tax_retention": True,
        "tax_retention_rate": 1.25,
        "start_date": "2024-05-15",
        "status": "active",
        "notes": "Cliente solo de diseño mensual, corte día 22"
    }

    create_resp = client.post("/api/dashboard/clients/directory", json=payload)
    assert create_resp.status_code == 200, create_resp.text
    data = create_resp.json()
    assert data["name"] == "Cliente Test Creativo"
    assert data["service_type"] == "design_subscription"
    assert data["billing_period"] == "monthly"
    assert data["billing_day"] == 22
    assert data["monthly_fee"] == 8500.0
    assert data["requires_invoice"] is True
    assert data["apply_tax_retention"] is True
    assert data["tax_retention_rate"] == 1.25
    client_id = data["id"]

    # 2. Listar clientes y verificar que aparezca
    list_resp = client.get("/api/dashboard/clients/directory")
    assert list_resp.status_code == 200
    all_clients = list_resp.json()
    names = [c["name"] for c in all_clients]
    assert "Cliente Test Creativo" in names

    # 3. Actualizar cliente a modalidad anual y sin retención
    update_payload = {
        "monthly_fee": 95000.0,
        "billing_period": "annual",
        "billing_day": 28,
        "requires_invoice": False,
        "apply_tax_retention": False
    }
    put_resp = client.put(f"/api/dashboard/clients/directory/{client_id}", json=update_payload)
    assert put_resp.status_code == 200
    updated_data = put_resp.json()
    assert updated_data["monthly_fee"] == 95000.0
    assert updated_data["billing_period"] == "annual"
    assert updated_data["billing_day"] == 28
    assert updated_data["requires_invoice"] is False
    assert updated_data["apply_tax_retention"] is False

    # 4. Eliminar cliente
    del_resp = client.delete(f"/api/dashboard/clients/directory/{client_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True


@pytest.mark.anyio
async def test_send_email_to_client_endpoint():
    with patch("app.core.mailer._send_smtp", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True

        email_payload = {
            "to_email": "prospecto@cliente.com",
            "subject": "Recordatorio de Corte Mensual - HiphaMX",
            "message": "Hola, te enviamos el recordatorio de corte mensual para la renovación de tu suscripción de diseño.",
            "client_name": "Juan Pérez"
        }

        resp = client.post("/api/dashboard/clients/send-email", json=email_payload)
        assert resp.status_code == 200, resp.text
        assert resp.json()["success"] is True
        assert "log_id" in resp.json()
        assert mock_send.called


@pytest.mark.anyio
async def test_send_email_with_pdf_attachment_and_history_logging():
    import base64
    fake_pdf = base64.b64encode(b"%PDF-1.4 Fake PDF Content").decode("utf-8")

    with patch("app.core.mailer._send_smtp", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True

        email_payload = {
            "to_email": "facturacion@cliente.com",
            "subject": "Pago recibido y Factura CFDI - HiphaMX",
            "message": "Hola, te adjuntamos tu factura CFDI en formato PDF.",
            "client_name": "Cliente CFDI Test",
            "attachments": [
                {
                    "filename": "Factura_F102.pdf",
                    "content_base64": fake_pdf,
                    "content_type": "application/pdf"
                }
            ]
        }

        # 1. Enviar correo con PDF adjunto
        resp = client.post("/api/dashboard/clients/send-email", json=email_payload)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["success"] is True
        log_id = data["log_id"]
        assert log_id is not None
        assert mock_send.called

        # 2. Consultar historial de correos
        history_resp = client.get("/api/dashboard/clients/email-history?search=Factura_F102")
        assert history_resp.status_code == 200, history_resp.text
        history_data = history_resp.json()
        assert isinstance(history_data, list)
        assert len(history_data) >= 1
        
        target_log = next((l for l in history_data if l["id"] == log_id), None)
        assert target_log is not None
        assert target_log["to_email"] == "facturacion@cliente.com"
        assert target_log["has_attachments"] is True
        assert "Factura_F102.pdf" in target_log["attachment_names"]
        assert target_log["status"] == "sent"

        # 3. Consultar detalle por ID
        detail_resp = client.get(f"/api/dashboard/clients/email-history/{log_id}")
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert detail_data["id"] == log_id
        assert detail_data["subject"] == "Pago recibido y Factura CFDI - HiphaMX"
        assert "te adjuntamos tu factura CFDI" in detail_data["message_body"]
