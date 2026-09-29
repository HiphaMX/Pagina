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
    # 1. Crear nuevo cliente
    payload = {
        "name": "Cliente Test Creativo",
        "contact_name": "Carlos Diseñador",
        "contact_email": "carlos@testcreativo.com",
        "contact_phone": "3331234567",
        "service_type": "design",
        "billing_day": 22,
        "monthly_fee": 8500.0,
        "start_date": "2024-05-15",
        "status": "active",
        "notes": "Cliente solo de diseño mensual, corte día 22"
    }

    create_resp = client.post("/api/dashboard/clients/directory", json=payload)
    assert create_resp.status_code == 200, create_resp.text
    data = create_resp.json()
    assert data["name"] == "Cliente Test Creativo"
    assert data["billing_day"] == 22
    assert data["monthly_fee"] == 8500.0
    client_id = data["id"]

    # 2. Listar clientes y verificar que aparezca
    list_resp = client.get("/api/dashboard/clients/directory")
    assert list_resp.status_code == 200
    all_clients = list_resp.json()
    names = [c["name"] for c in all_clients]
    assert "Cliente Test Creativo" in names

    # 3. Actualizar cliente
    update_payload = {
        "monthly_fee": 9500.0,
        "billing_day": 28
    }
    put_resp = client.put(f"/api/dashboard/clients/directory/{client_id}", json=update_payload)
    assert put_resp.status_code == 200
    updated_data = put_resp.json()
    assert updated_data["monthly_fee"] == 9500.0
    assert updated_data["billing_day"] == 28

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
        assert mock_send.called
