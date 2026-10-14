import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from app.core.database import SessionLocal, Base, engine
from app.models.quotation import Quotation

client = TestClient(app)

mock_admin = UserSchema(
    id=1,
    email="hola@hipha.mx",
    is_active=True,
    is_superuser=True,
    full_name="Administrador Hipha",
)


@pytest.fixture(autouse=True)
def setup_db_and_auth():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin
    yield
    app.dependency_overrides.pop(get_current_active_user, None)


def test_quotations_catalog():
    response = client.get("/api/dashboard/quotations/catalog")
    assert response.status_code == 200
    catalog = response.json()
    assert isinstance(catalog, list)
    assert len(catalog) >= 10

    catalog_names = [item["name"] for item in catalog]
    assert "Identidad Gráfica" in catalog_names
    assert "Plan Web (Mensual)" in catalog_names
    assert "Plan Web (Anual)" in catalog_names
    assert "Plan MKT" in catalog_names
    assert "Product Shot" in catalog_names


def test_generate_pdf_endpoint():
    payload = {
        "client_name": "Restaurante La Casona",
        "client_contact": "Chef Alejandro",
        "client_email": "contacto@lacasona.mx",
        "client_phone": "443-987-6543",
        "validity_days": 15,
        "items": [
            {
                "name": "Identidad Gráfica",
                "description": "Rediseño de logotipo y manual de marca.",
                "quantity": 1,
                "unit_price": 3770.0,
            },
            {
                "name": "Menú Digital Interactivo",
                "description": "Desarrollo a medida con código QR.",
                "quantity": 1,
                "unit_price": 4500.0,
            },
        ],
        "apply_tax": True,
        "tax_rate": 0.16,
        "down_payment_rate": 0.50,
        "notes": "Incluye capacitación inicial de 2 horas.",
    }

    response = client.post("/api/dashboard/quotations/generate-pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    content = response.content
    assert content.startswith(b"%PDF")
    assert len(content) > 10000  # PDF de alta fidelidad con vector base


def test_quotations_crud():
    # 1. Crear cotización en BD
    create_payload = {
        "client_name": "Consultoría Médica Avanzada",
        "client_contact": "Dr. Fernando Ruiz",
        "client_email": "fernando@urologia.com",
        "client_phone": "555-432-1234",
        "validity_days": 30,
        "items": [
            {
                "name": "Plan Web (Anual)",
                "description": "Sitio web médico profesional con optimización SEO y GEO.",
                "quantity": 1,
                "unit_price": 7760.0,
            },
            {
                "name": "Video IA Promocional",
                "description": "Cápsula explicativa de procedimientos clínicos.",
                "quantity": 2,
                "unit_price": 770.0,
            },
        ],
        "apply_tax": True,
        "down_payment_rate": 0.50,
        "notes": "Entrega en 10 días hábiles.",
    }

    res_create = client.post("/api/dashboard/quotations/", json=create_payload)
    assert res_create.status_code == 200
    created = res_create.json()
    q_id = created["id"]
    assert q_id is not None
    assert created["folio"].startswith("HIP-")
    assert created["client_name"] == "Consultoría Médica Avanzada"
    # Subtotal: 7760 + (2 * 770) = 7760 + 1540 = 9300
    assert created["subtotal"] == 9300.0
    # IVA 16%: 9300 * 0.16 = 1488
    assert created["tax_amount"] == 1488.0
    # Total: 9300 + 1488 = 10788
    assert created["total"] == 10788.0
    # Anticipo: 10788 * 0.5 = 5394
    assert created["down_payment_amount"] == 5394.0

    # 2. Consultar lista
    res_list = client.get("/api/dashboard/quotations/")
    assert res_list.status_code == 200
    items = res_list.json()
    assert any(q["id"] == q_id for q in items)

    # 3. Consultar detalle por ID
    res_get = client.get(f"/api/dashboard/quotations/{q_id}")
    assert res_get.status_code == 200
    detail = res_get.json()
    assert detail["client_contact"] == "Dr. Fernando Ruiz"
    assert len(detail["items"]) == 2

    # 4. Descargar PDF directo por ID
    res_pdf = client.get(f"/api/dashboard/quotations/direct-pdf/{q_id}")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content.startswith(b"%PDF")

    # 5. Eliminar cotización
    res_del = client.delete(f"/api/dashboard/quotations/{q_id}")
    assert res_del.status_code == 200

    # Verificar que ya no existe
    res_verify = client.get(f"/api/dashboard/quotations/{q_id}")
    assert res_verify.status_code == 404
