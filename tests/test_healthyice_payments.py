import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.healthyice_order import HealthyIceOrder
import json

# Crear base de datos SQLite en memoria para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_payments.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sobreescribir dependencia de get_db en app
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@patch("app.api.mercadopago.get_sdk_for_store")
def test_create_preference_and_webhook_workflow(mock_get_sdk):
    # Mockear el SDK de Mercado Pago
    mock_sdk_instance = MagicMock()
    mock_get_sdk.return_value = mock_sdk_instance
    
    # Mock para create preference
    mock_preference = MagicMock()
    mock_preference.create.return_value = {
        "response": {
            "id": "pref-123456",
            "init_point": "https://www.mercadopago.com.mx/checkout/v1/redirect?pref_id=pref-123456",
            "sandbox_init_point": "https://sandbox.mercadopago.com.mx/checkout/v1/redirect?pref_id=pref-123456"
        }
    }
    mock_sdk_instance.preference.return_value = mock_preference

    # 1. Petición para crear preferencia
    payload = {
        "items": [
            {
                "name": "HealthyIce - Chocolate (1 pieza)",
                "price": 60.0,
                "quantity": 2,
                "image": "http://example.com/choc.png"
            }
        ],
        "payer": {
            "name": "Pedro Perez",
            "email": "pedro@example.com",
            "phone": "3331234567",
            "address": {
                "street_name": "Av Patria 123",
                "zip_code": "45110"
            }
        },
        "store": "healthyice"
    }

    response = client.post("/api/mercadopago/create_preference", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "init_point" in data
    assert data["id"] == "pref-123456"

    # Verificar que se creó la orden en la base de datos
    db = TestingSessionLocal()
    order = db.query(HealthyIceOrder).first()
    assert order is not None
    assert order.nombre == "Pedro Perez"
    assert order.email == "pedro@example.com"
    assert order.total == 120.0
    assert order.status == "pending_payment"
    order_id = order.id
    db.close()

    # Mock para webhook (obtener el pago de mercado pago)
    mock_payment = MagicMock()
    mock_payment.get.return_value = {
        "response": {
            "id": 987654321,
            "status": "approved",
            "metadata": {
                "store": "healthyice",
                "order_id": str(order_id),
                "payer_name": "Pedro Perez",
                "payer_email": "pedro@example.com",
                "payer_phone": "3331234567",
                "address": "Av Patria 123, CP 45110",
                "cart_html": "<ul><li>2x HealthyIce - Chocolate (1 pieza) - $60.0</li></ul>",
                "total": "120.0"
            }
        }
    }
    mock_sdk_instance.payment.return_value = mock_payment

    # 2. Llamada al webhook simulando la confirmación del pago
    webhook_payload = {
        "action": "payment.created",
        "data": {
            "id": "987654321"
        }
    }
    
    # Parchear el envío de correos electrónicos para no lanzar peticiones reales de red
    with patch("asyncio.create_task") as mock_task:
        response = client.post("/api/mercadopago/webhook?store=healthyice", json=webhook_payload)
        assert response.status_code == 200
        
    # Verificar que el estado de la orden cambió a "paid"
    db = TestingSessionLocal()
    updated_order = db.query(HealthyIceOrder).filter(HealthyIceOrder.id == order_id).first()
    assert updated_order is not None
    assert updated_order.status == "paid"
    assert updated_order.mercadopago_payment_id == "987654321"
    db.close()
