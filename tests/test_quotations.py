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

    # 5. Modificar / Actualizar cotización (PUT)
    update_payload = dict(create_payload)
    update_payload["client_name"] = "Consultoría Médica Avanzada Modificada"
    update_payload["notes"] = "Nota actualizada para entrega urgente."
    update_payload["items"] = [
        {
            "name": "Plan Web (Anual)",
            "description": "Sitio web médico profesional con optimización SEO y GEO.",
            "quantity": 1,
            "unit_price": 8000.0,
        }
    ]
    res_put = client.put(f"/api/dashboard/quotations/{q_id}", json=update_payload)
    assert res_put.status_code == 200
    updated = res_put.json()
    assert updated["id"] == q_id
    assert updated["client_name"] == "Consultoría Médica Avanzada Modificada"
    assert updated["subtotal"] == 8000.0
    assert updated["tax_amount"] == 1280.0
    assert updated["total"] == 9280.0
    assert len(updated["items"]) == 1

    # Verificar que el GET refleja los cambios
    res_verify_updated = client.get(f"/api/dashboard/quotations/{q_id}")
    assert res_verify_updated.status_code == 200
    assert res_verify_updated.json()["client_name"] == "Consultoría Médica Avanzada Modificada"
    assert len(res_verify_updated.json()["items"]) == 1

    # 6. Eliminar cotización
    res_del = client.delete(f"/api/dashboard/quotations/{q_id}")
    assert res_del.status_code == 200

    # Verificar que ya no existe
    res_verify = client.get(f"/api/dashboard/quotations/{q_id}")
    assert res_verify.status_code == 404


def test_quotation_without_down_payment():
    """Prueba que una cotización con require_down_payment=False no genere anticipo ni en BD ni en PDF."""
    payload = {
        "client_name": "Corporativo Horizonte",
        "client_contact": "Ing. Sofía Morales",
        "items": [
            {
                "name": "Consultoría Estratégica",
                "description": "Sesión de planeación e implementación tecnológica.",
                "quantity": 1,
                "unit_price": 20000.0,
            }
        ],
        "apply_tax": True,
        "require_down_payment": False,
    }

    # 1. Test generate-pdf endpoint
    res_pdf = client.post("/api/dashboard/quotations/generate-pdf", json=payload)
    assert res_pdf.status_code == 200
    assert res_pdf.content.startswith(b"%PDF")

    import io
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(res_pdf.content))
    pdf_text = "\n".join(p.extract_text() for p in reader.pages)
    assert "Se requiere OC para iniciar con el trabajo y confirmar el tiempo de entrega." in pdf_text
    assert "ANTICIPO REQUERIDO" not in pdf_text

    # 2. Test CRUD create
    res_create = client.post("/api/dashboard/quotations/", json=payload)
    assert res_create.status_code == 200
    data = res_create.json()
    assert data["require_down_payment"] is False
    assert data["down_payment_rate"] == 0.0
    assert data["down_payment_amount"] == 0.0

    # 3. Direct PDF download
    q_id = data["id"]
    res_direct = client.get(f"/api/dashboard/quotations/direct-pdf/{q_id}")
    assert res_direct.status_code == 200
    assert res_direct.content.startswith(b"%PDF")
    reader_direct = PdfReader(io.BytesIO(res_direct.content))
    pdf_direct_text = "\n".join(p.extract_text() for p in reader_direct.pages)
    assert "Se requiere OC para iniciar con el trabajo y confirmar el tiempo de entrega." in pdf_direct_text

    # Cleanup
    client.delete(f"/api/dashboard/quotations/{q_id}")


def test_quotation_without_tax():
    """Prueba que una cotización con apply_tax=False no imprima 'No aplica' en el PDF."""
    payload = {
        "client_name": "Corporativo San Ángel",
        "client_contact": "Lic. Martín Domínguez",
        "items": [
            {
                "name": "Servicio de Diseño Editorial",
                "description": "Folleto corporativo y tríptico informativo.",
                "quantity": 2,
                "unit_price": 2500.0,
            }
        ],
        "apply_tax": False,
        "require_down_payment": True,
    }

    res_pdf = client.post("/api/dashboard/quotations/generate-pdf", json=payload)
    assert res_pdf.status_code == 200

    import io
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(res_pdf.content))
    pdf_text = "\n".join(p.extract_text() for p in reader.pages)

    # No debe decir 'No aplica'
    assert "No aplica" not in pdf_text
    assert "no aplica" not in pdf_text.lower()
    # Debe indicar en condiciones que los precios no incluyen IVA
    assert "Los precios mostrados no incluyen IVA" in pdf_text


def test_quotation_clients_directory_and_auto_sync():
    """Prueba que el endpoint /clients devuelva los clientes consolidados y que crear una cotización
    guarde automáticamente el contacto en AgencyClient para su reutilización futura."""
    from app.models.client import AgencyClient

    # 1. Directorio inicial de clientes
    res_clients = client.get("/api/dashboard/quotations/clients")
    assert res_clients.status_code == 200
    clients_list = res_clients.json()
    assert isinstance(clients_list, list)
    client_names = [c["name"] for c in clients_list]
    assert "AMDI" in client_names
    assert "Letrerama" in client_names

    # 2. Crear cotización con cliente y contacto nuevos
    test_client_name = "Constructora del Valle"
    test_contact = "Arq. Ricardo Morales"
    test_email = "ricardo@delvalle.com"
    test_phone = "443-111-2233"

    payload = {
        "client_name": test_client_name,
        "client_contact": test_contact,
        "client_email": test_email,
        "client_phone": test_phone,
        "items": [
            {
                "name": "Identidad Gráfica",
                "description": "Logotipo corporativo para desarrolladora inmobiliaria.",
                "quantity": 1,
                "unit_price": 3770.0,
            }
        ],
    }

    res_create = client.post("/api/dashboard/quotations/", json=payload)
    assert res_create.status_code == 200
    created = res_create.json()
    q_id = created["id"]
    assigned_client_id = created["client_id"]
    assert assigned_client_id is not None

    # 3. Verificar que se sincronizó en AgencyClient
    db = SessionLocal()
    try:
        ac = db.query(AgencyClient).filter(AgencyClient.id == assigned_client_id).first()
        assert ac is not None
        assert ac.name == test_client_name
        assert ac.contact_name == test_contact
        assert ac.contact_email == test_email
        assert ac.contact_phone == test_phone
    finally:
        db.close()

    # 4. Verificar que el directorio /clients ahora lo incluye con todos sus datos de contacto
    res_clients_after = client.get("/api/dashboard/quotations/clients")
    assert res_clients_after.status_code == 200
    after_list = res_clients_after.json()
    found = next((c for c in after_list if c["name"] == test_client_name), None)
    assert found is not None
    assert found["contact_name"] == test_contact
    assert found["contact_email"] == test_email
    assert found["contact_phone"] == test_phone

    # 5. Actualizar cotización con teléfono modificado y verificar sincronización
    update_payload = dict(payload)
    update_payload["client_phone"] = "443-999-8877"
    res_update = client.put(f"/api/dashboard/quotations/{q_id}", json=update_payload)
    assert res_update.status_code == 200

    db2 = SessionLocal()
    try:
        ac_updated = db2.query(AgencyClient).filter(AgencyClient.id == assigned_client_id).first()
        assert ac_updated.contact_phone == "443-999-8877"
    finally:
        db2.close()

    # Cleanup
    client.delete(f"/api/dashboard/quotations/{q_id}")



