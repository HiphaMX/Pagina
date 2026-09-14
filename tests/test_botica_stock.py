import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.botica_product import BoticaProduct

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_botica.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_get_stock_auto_seeds():
    client = TestClient(app)
    response = client.get("/api/botica/stock")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["items"]) >= 24
    assert "Focus - Tintura" in data["stock_map"]
    assert data["stock_map"]["Focus - Tintura"]["stock"] == 10

def test_admin_login_invalid():
    client = TestClient(app)
    response = client.post("/api/botica/admin/login", json={"password": "wrongpassword"})
    assert response.status_code == 401

def test_admin_login_valid():
    client = TestClient(app)
    response = client.post("/api/botica/admin/login", json={"password": "botica2026"})
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_admin_update_stock():
    client = TestClient(app)
    payload = {
        "password": "botica2026",
        "updates": [
            {"slug": "focus-tintura", "stock": 3, "is_active": True},
            {"slug": "focus-oleato", "stock": 0, "is_active": True}
        ]
    }
    response = client.post("/api/botica/admin/stock", json=payload)
    assert response.status_code == 200
    assert response.json()["updated_count"] == 2

    # Check updated stock
    get_res = client.get("/api/botica/stock")
    assert get_res.status_code == 200
    stock_map = get_res.json()["stock_map"]
    assert stock_map["Focus - Tintura"]["stock"] == 3
    assert stock_map["Focus - Oleato"]["stock"] == 0

def test_deduct_stock():
    from app.api.projects.botica import deduct_botica_stock
    db = TestingSessionLocal()
    try:
        cart_items = [
            {"name": "Focus - Tintura", "quantity": 2},
            {"name": "Colita de Rana - Pomada", "quantity": 1}
        ]
        result = deduct_botica_stock(db, cart_items)
        assert len(result["deducted"]) == 2

        prod = db.query(BoticaProduct).filter(BoticaProduct.slug == "focus-tintura").first()
        assert prod.stock == 1

        pomada = db.query(BoticaProduct).filter(BoticaProduct.slug == "colita-de-rana-pomada").first()
        assert pomada.stock == 9
    finally:
        db.close()

