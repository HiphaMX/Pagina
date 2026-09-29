from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_endpoints_require_auth():
    """Verifica que los endpoints del dashboard requieran autenticación JWT y devuelvan 401."""
    # 1. Test /api/dashboard/clients
    response = client.get("/api/dashboard/clients")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

    # 2. Test /api/dashboard/metrics/overview
    response = client.get("/api/dashboard/metrics/overview")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

    # 3. Test /api/dashboard/metrics/client/123456789
    response = client.get("/api/dashboard/metrics/client/123456789")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_health_endpoints():
    """Verifica que los endpoints de salud respondan 200 OK."""
    r1 = client.get("/api/health")
    assert r1.status_code == 200
    assert r1.json()["status"] == "ok"

    r2 = client.get("/health")
    assert r2.status_code == 200
    assert r2.json()["status"] == "ok"

def test_dashboard_overview_graceful_without_ga4():
    """Verifica que el overview no lance 500 cuando las credenciales de GA4 no están disponibles o fallan."""
    from app.api.deps import get_current_active_user
    from app.schemas.user import User as UserSchema
    
    mock_user = UserSchema(id=1, email="admin@hipha.mx", is_active=True, is_superuser=True, full_name="Admin")
    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    try:
        response = client.get("/api/dashboard/metrics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        # Aseguramos que retorne los clientes mapeados
        assert len(data["data"]) > 0
        first_client = data["data"][0]
        assert "name" in first_client
        assert "summary" in first_client
        assert "newUsers" in first_client["summary"]
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)
