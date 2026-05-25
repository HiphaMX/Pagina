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
