import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.chilechillon_lead import ChileChillonLead

# Use a test SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_db():
    # Create the test DB and tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the tables after tests finish
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(setup_db):
    with TestClient(app) as c:
        yield c

def test_submit_chilechillon_form_success(client):
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

def test_submit_chilechillon_form_invalid_email(client):
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

def test_get_chile_chillon_reviews(client):
    response = client.get("/api/contact/reviews/chilechillon")
    assert response.status_code == 200
    data = response.json()
    assert "rating" in data
    assert "user_ratings_total" in data
    assert "reviews" in data
    assert isinstance(data["reviews"], list)
    assert len(data["reviews"]) > 0
    # Check fields in first review candidate
    first_review = data["reviews"][0]
    assert "name" in first_review
    assert "initials" in first_review
    assert "tag" in first_review
    assert "stars" in first_review
    assert "text" in first_review

def test_register_quiniela_lead_success(client):
    response = client.post(
        "/api/contact/chilechillon/quiniela/register",
        json={
            "nombre": "Juan Pérez",
            "email": "juan.perez@example.com",
            "telefono": "3311223344",
            "prediccion_campeon": "tat"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Registro exitoso"

    # Verify database insertion
    db = TestingSessionLocal()
    lead = db.query(ChileChillonLead).filter(ChileChillonLead.email == "juan.perez@example.com").first()
    assert lead is not None
    assert lead.nombre == "Juan Pérez"
    assert lead.telefono == "3311223344"
    assert lead.prediccion_campeon == "tat"
    db.close()

def test_register_quiniela_lead_duplicate_updates(client):
    # First request
    client.post(
        "/api/contact/chilechillon/quiniela/register",
        json={
            "nombre": "Juan Pérez",
            "email": "juan.perez@example.com",
            "telefono": "3311223344",
            "prediccion_campeon": "tat"
        }
    )
    # Second request with same email but updated name and phone
    response = client.post(
        "/api/contact/chilechillon/quiniela/register",
        json={
            "nombre": "Juan P. Modificado",
            "email": "juan.perez@example.com",
            "telefono": "3399887766",
            "prediccion_campeon": "ser"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Registro exitoso"

    # Verify database update
    db = TestingSessionLocal()
    lead = db.query(ChileChillonLead).filter(ChileChillonLead.email == "juan.perez@example.com").first()
    assert lead is not None
    assert lead.nombre == "Juan P. Modificado"
    assert lead.telefono == "3399887766"
    assert lead.prediccion_campeon == "tat"
    db.close()

def test_register_quiniela_lead_invalid_email(client):
    response = client.post(
        "/api/contact/chilechillon/quiniela/register",
        json={
            "nombre": "Juan Pérez",
            "email": "not-an-email",
            "telefono": "3311223344",
            "prediccion_campeon": "tat"
        }
    )
    assert response.status_code == 422 # Validation Error

def test_register_quiniela_lead_no_phone(client):
    response = client.post(
        "/api/contact/chilechillon/quiniela/register",
        json={
            "nombre": "Pedro Páramo",
            "email": "pedro.paramo@example.com",
            "prediccion_campeon": "neg"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Registro exitoso"

    # Verify database insertion
    db = TestingSessionLocal()
    lead = db.query(ChileChillonLead).filter(ChileChillonLead.email == "pedro.paramo@example.com").first()
    assert lead is not None
    assert lead.nombre == "Pedro Páramo"
    assert lead.telefono is None
    assert lead.prediccion_campeon == "neg"
    db.close()

def test_export_leads_unauthorized(client):
    response = client.get("/api/dashboard/chilechillon/quiniela/export")
    assert response.status_code == 401 # Unauthorized

def test_export_leads_authorized(client):
    # 1. Register a test admin user
    reg_response = client.post(
        "/api/auth/register",
        json={"email": "admin@example.com", "password": "adminpassword123"}
    )
    assert reg_response.status_code == 200

    # 2. Login to get token
    login_response = client.post(
        "/api/auth/login",
        data={"username": "admin@example.com", "password": "adminpassword123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Request export with token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/dashboard/chilechillon/quiniela/export", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    csv_data = response.text
    assert "Juan P. Modificado" in csv_data
    assert "juan.perez@example.com" in csv_data
    assert "3399887766" in csv_data
    assert "TAT" in csv_data

def test_get_quiniela_results(client):
    response = client.get("/api/contact/chilechillon/quiniela/results")
    assert response.status_code == 200
    data = response.json()
    assert "total_votes" in data
    assert "counts" in data
    assert "percentages" in data
    # Since previous tests inserted some leads:
    assert data["total_votes"] > 0
    assert "tat" in data["counts"]
    assert "neg" in data["counts"]



