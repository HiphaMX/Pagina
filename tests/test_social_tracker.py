from fastapi.testclient import TestClient
from app.main import app
from app.services.social_extractor import parse_follower_number, detect_platform_and_handle

client = TestClient(app)


def test_parse_follower_number():
    assert parse_follower_number("29") == 29
    assert parse_follower_number("2.558") == 2558
    assert parse_follower_number("1,250") == 1250
    assert parse_follower_number("15.4K") == 15400
    assert parse_follower_number("1.2M") == 1200000
    assert parse_follower_number("291M") == 291000000
    assert parse_follower_number("0") == 0
    assert parse_follower_number("") == 0


def test_detect_platform_and_handle():
    p1, h1, u1 = detect_platform_and_handle("https://www.instagram.com/chilechillon/")
    assert p1 == "instagram"
    assert h1 == "@chilechillon"
    assert "https://www.instagram.com/chilechillon/" in u1

    p2, h2, u2 = detect_platform_and_handle("https://facebook.com/elchilechillon")
    assert p2 == "facebook"
    assert h2 == "elchilechillon"


def test_social_endpoints_require_auth():
    r1 = client.get("/api/dashboard/social/overview")
    assert r1.status_code == 401

    r2 = client.post("/api/dashboard/social/accounts", json={"url": "https://instagram.com/test"})
    assert r2.status_code == 401

    r3 = client.post("/api/dashboard/social/accounts/1/scan")
    assert r3.status_code == 401


def test_social_observatory_with_auth():
    from app.api.deps import get_current_active_user
    from app.schemas.user import User as UserSchema
    from app.core.database import Base, engine

    Base.metadata.create_all(bind=engine)

    mock_user = UserSchema(id=1, email="admin@hipha.mx", is_active=True, is_superuser=True, full_name="Admin")
    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    try:
        response = client.get("/api/dashboard/social/overview")
        assert response.status_code == 200
        data = response.json()
        assert "total_accounts" in data
        assert "total_audience" in data
        assert "accounts" in data
        assert isinstance(data["accounts"], list)
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


def test_social_account_lifecycle(monkeypatch):
    import app.api.social_tracker as social_api
    import app.services.social_extractor as extractor
    from app.api.deps import get_current_active_user
    from app.schemas.user import User as UserSchema
    from app.core.database import Base, engine

    Base.metadata.create_all(bind=engine)

    mock_user = UserSchema(id=1, email="admin@hipha.mx", is_active=True, is_superuser=True, full_name="Admin")
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    import uuid
    random_id = uuid.uuid4().hex[:6]
    test_url = f"https://www.instagram.com/testbrand_{random_id}/"

    # Mock fetch_social_metadata to avoid external HTTP requests in tests
    def mock_fetch(url, platform):
        return {
            "platform": platform,
            "handle": f"@testbrand_{random_id}",
            "name": f"Test Brand {random_id}",
            "url": url,
            "avatar_url": "https://example.com/avatar.jpg",
            "followers": 1500,
            "raw_description": "1,500 seguidores"
        }
    monkeypatch.setattr(extractor, "fetch_social_metadata", mock_fetch)
    monkeypatch.setattr(social_api, "fetch_social_metadata", mock_fetch)

    try:
        # 1. Crear cuenta
        create_res = client.post("/api/dashboard/social/accounts", json={
            "url": test_url,
            "name": f"Test Brand IG {random_id}"
        })
        assert create_res.status_code == 200, f"Error: {create_res.text}"
        account = create_res.json()
        acc_id = account["id"]
        assert account["name"] == f"Test Brand IG {random_id}"
        assert account["current_followers"] == 1500
        assert account["platform"] == "instagram"

        # 2. Agregar snapshot manual con nuevo conteo (1600 seguidores)
        manual_res = client.post(f"/api/dashboard/social/accounts/{acc_id}/manual-snapshot", json={
            "followers": 1600
        })
        assert manual_res.status_code == 200
        updated_acc = manual_res.json()
        assert updated_acc["current_followers"] == 1600
        assert updated_acc["growth_total"] == 100

        # 3. Consultar overview y verificar métricas calculadas
        overview_res = client.get("/api/dashboard/social/overview")
        assert overview_res.status_code == 200
        ov_data = overview_res.json()
        assert ov_data["total_accounts"] >= 1
        assert ov_data["total_audience"] >= 1600
        
        target_acc = next((a for a in ov_data["accounts"] if a["id"] == acc_id), None)
        assert target_acc is not None
        assert target_acc["current_followers"] == 1600
        assert target_acc["initial_followers"] == 1500
        assert target_acc["growth_total"] == 100
        assert len(target_acc["sparkline_history"]) >= 2

        # 4. Eliminar cuenta
        del_res = client.delete(f"/api/dashboard/social/accounts/{acc_id}")
        assert del_res.status_code == 200
        assert del_res.json()["ok"] is True

        # Verificar que ya no está en el overview
        ov2 = client.get("/api/dashboard/social/overview").json()
        assert not any(a["id"] == acc_id for a in ov2["accounts"])
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)

