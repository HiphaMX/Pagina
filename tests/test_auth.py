import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

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

def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "testuser@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

def test_register_existing_user(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "testuser@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "The user with this username already exists in the system."

def test_login_success(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "nobody@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 401
