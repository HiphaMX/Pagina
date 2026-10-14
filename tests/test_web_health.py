import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.services.monitoring.web_guardian import (
    clean_domain_string,
    audit_single_domain,
    generate_fleet_ai_summary
)
from app.models.web_health import WebHealthAudit
from app.core.database import SessionLocal

client = TestClient(app)


def test_clean_domain_string():
    assert clean_domain_string("https://www.amdi.mx/") == "amdi.mx"
    assert clean_domain_string("http://amdi.mx/contacto") == "amdi.mx"
    assert clean_domain_string("www.healthyice.mx") == "healthyice.mx"
    assert clean_domain_string("valenciaservicios.mx") == "valenciaservicios.mx"
    assert clean_domain_string("") == ""


def test_audit_single_domain_mocked():
    site_info = {
        "name": "Sitio Test",
        "domain": "test-domain.com",
        "url": "https://www.test-domain.com"
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html><head><title>Test</title></head><body><h1>Hola</h1><iframe src='https://www.google.com/maps/embed'></iframe></body></html>"
    mock_resp.headers = {"server": "cloudflare"}
    mock_resp.url = "https://www.test-domain.com/"

    def mock_doh(d):
        if "_dmarc" in d:
            return ['"v=DMARC1; p=none;"']
        return ['"v=spf1 include:mail.test.com ~all"']

    with patch("requests.get", return_value=mock_resp):
        with patch("app.services.monitoring.web_guardian.check_ssl_certificate", return_value={"valid": True, "days_remaining": 65, "issuer": "Let's Encrypt"}):
            with patch("app.services.monitoring.web_guardian.query_doh_txt_record", side_effect=mock_doh):
                res = audit_single_domain(site_info)

                assert res["domain"] == "test-domain.com"
                assert res["is_up"] is True
                assert res["ssl_valid"] is True
                assert res["ssl_days_remaining"] == 65
                assert res["dns_spf_status"] == "OK"
                assert res["dns_dmarc_status"] == "OK"
                assert res["maps_status"] == "OK"
                assert res["health_level"] in ("HEALTHY", "WARNING")
                assert res["overall_score"] >= 80


def test_generate_fleet_ai_summary_fallback():
    mock_audits = [
        {"client_name": "Cliente 1", "domain": "c1.com", "health_level": "HEALTHY", "issues_summary": []},
        {"client_name": "Cliente 2", "domain": "c2.com", "health_level": "WARNING", "issues_summary": ["Tiempo de respuesta elevado (2200 ms)"]},
    ]
    with patch("app.core.config.settings.GEMINI_API_KEY", None):
        with patch.dict("os.environ", {}, clear=True):
            summary = generate_fleet_ai_summary(mock_audits)
            assert "Guardián" in summary
            assert "sitios web" in summary.lower() or "saludables" in summary.lower()


def test_web_health_api_endpoints():
    # 1. Probar endpoint de cron (público)
    with patch("app.api.dashboard.web_health_routes.audit_all_fleet", return_value={"kpis": {"total_sites": 10}, "sites": []}):
        res_cron = client.get("/api/dashboard/web-health/cron")
        assert res_cron.status_code == 200
        assert res_cron.json()["success"] is True

    # 2. Probar endpoint de overview
    login_res = client.post("/api/auth/login", data={"username": "hola@hipha.mx", "password": "Celi@ThePug2026"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with patch("app.api.dashboard.web_health_routes.audit_all_fleet") as mock_fleet:
        mock_fleet.return_value = {
            "kpis": {
                "total_sites": 2,
                "healthy_sites": 2,
                "warning_sites": 0,
                "critical_sites": 0,
                "avg_response_time_ms": 250.0,
                "ssl_expiring_soon_count": 0,
                "smtp_ok_count": 2,
                "maps_ok_count": 2,
                "llms_txt_count": 2,
                "last_audit_time": "2026-10-14T10:00:00"
            },
            "agent_summary": "Flota 100% operativa",
            "sites": [
                {
                    "domain": "amdi.mx",
                    "client_name": "AMDI",
                    "url": "https://www.amdi.mx",
                    "is_up": True,
                    "health_level": "HEALTHY",
                    "overall_score": 98,
                    "response_time_ms": 210.0,
                    "ssl_days_remaining": 60,
                    "issues_summary": []
                }
            ],
            "last_audit_iso": "2026-10-14T10:00:00"
        }

        # overview con force_refresh=true
        res_ov = client.get("/api/dashboard/web-health/overview?force_refresh=true", headers=headers)
        assert res_ov.status_code == 200
        data = res_ov.json()
        assert "kpis" in data
        assert "agent_summary" in data
        assert len(data["sites"]) == 1

        # run-audit
        res_run = client.post("/api/dashboard/web-health/run-audit", json={"use_ai": False}, headers=headers)
        assert res_run.status_code == 200
