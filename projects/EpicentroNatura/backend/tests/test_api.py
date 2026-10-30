import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

# Asegurar path para imports
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.models import (
    Community,
    CommunityType,
    BusinessCategory,
    Business,
    BusinessStatus,
    CulturalEvent,
    TargetAudience,
    CivicNotice,
    CivicNoticeType,
    CivicNoticeStatus,
)
from app.utils.whatsapp import build_whatsapp_link, sanitize_whatsapp_number
from app.utils.opening_hours import check_is_open_now
from app.tasks.auto_expiry import expire_outdated_notices

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Inicializa la base de datos para pruebas."""
    Base.metadata.create_all(bind=engine)
    yield


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Natura" in data["service"]


def test_whatsapp_helpers():
    cleaned = sanitize_whatsapp_number("+52 (33) 1234-5678")
    assert cleaned == "523312345678"

    link = build_whatsapp_link("+523312345678", "Dulce Bosque", "pedir un pastel")
    assert "https://wa.me/523312345678" in link
    assert "Dulce%20Bosque" in link


def test_opening_hours_evaluator():
    schedule = {
        "mon": {"open": "09:00", "close": "18:00"},
        "tue": {"open": "09:00", "close": "18:00"}
    }
    # Lunes a las 18:00 UTC (12:00 hora local Zapopan UTC-6)
    open_dt = datetime(2026, 10, 26, 18, 0, tzinfo=timezone.utc)
    is_open, msg = check_is_open_now(schedule, open_dt)
    assert is_open is True
    assert "Abierto" in msg

    # Lunes a las 04:00 UTC del martes (22:00 hora local Zapopan UTC-6)
    closed_dt = datetime(2026, 10, 27, 4, 0, tzinfo=timezone.utc)
    is_open, msg = check_is_open_now(schedule, closed_dt)
    assert is_open is False


def test_list_communities_and_categories():
    res_comm = client.get("/api/v1/communities")
    assert res_comm.status_code == 200
    communities = res_comm.json()
    assert len(communities) >= 1

    res_cat = client.get("/api/v1/categories")
    assert res_cat.status_code == 200
    categories = res_cat.json()
    assert len(categories) >= 1


def test_commercial_engine():
    # 1. Listar comercios
    res = client.get("/api/v1/businesses")
    assert res.status_code == 200
    businesses = res.json()
    assert len(businesses) >= 1
    sample = businesses[0]
    assert "whatsapp_link" in sample
    assert "is_open_now" in sample

    # 2. Filtrar emprendimientos en coto
    res_coto = client.get("/api/v1/businesses?is_home_based=true")
    assert res_coto.status_code == 200
    for b in res_coto.json():
        assert b["is_home_based"] is True

    # 3. Filtrar por business_type
    res_type = client.get("/api/v1/businesses?business_type=local_establecido")
    assert res_type.status_code == 200
    for b in res_type.json():
        assert b["business_type"] == "local_establecido"

    # 4. Filtrar por Sello Verde Km 0 (0 Emisiones)
    res_km0 = client.get("/api/v1/businesses?has_km0_badge=true")
    assert res_km0.status_code == 200
    for b in res_km0.json():
        assert b["has_km0_badge"] is True

    # 5. Filtrar por delivery
    res_deliv = client.get("/api/v1/businesses?delivery_available=true")
    assert res_deliv.status_code == 200
    for b in res_deliv.json():
        assert b["delivery_available"] is True

    # 6. Detalle por slug
    slug = sample["slug"]
    res_slug = client.get(f"/api/v1/businesses/{slug}")
    assert res_slug.status_code == 200
    assert res_slug.json()["slug"] == slug

    # 7. Registro de nuevo comercio (debe quedar en pending_approval)
    cat_id = sample["category_id"]
    new_reg = {
        "name": "Bicicletas y Taller Natura",
        "category_id": cat_id,
        "business_type": "emprendimiento",
        "is_home_based": True,
        "whatsapp_number": "+523319998877",
        "phone_number": "33 1999 8877",
        "description": "Reparación y ajuste de bicicletas para niños y montaña en Coto Roble.",
        "delivery_available": True,
        "has_km0_badge": True,
        "km0_reason": "Taller dentro de coto, entrega y recogida en bicicleta"
    }
    res_reg = client.post("/api/v1/businesses/register", json=new_reg)
    assert res_reg.status_code == 201
    created = res_reg.json()
    assert created["status"] == "pending_approval"
    assert created["slug"].startswith("bicicletas-y-taller-natura")


def test_cultural_events_and_atomic_rsvp():
    db = SessionLocal()
    try:
        now_utc = datetime.now(timezone.utc)
        # Crear evento de prueba con cupo limitado de 2
        test_event = CulturalEvent(
            id=uuid.uuid4(),
            title="Taller Exclusivo de Bonsái",
            slug=f"taller-bonsai-{uuid.uuid4().hex[:6]}",
            organizer="Casa de la Cultura",
            start_datetime=now_utc + timedelta(days=3),
            end_datetime=now_utc + timedelta(days=3, hours=2),
            location_name="Jardín Botánico Natura",
            target_audience=TargetAudience.ADULTS,
            capacity_limit=2,
            current_rsvp_count=0
        )
        db.add(test_event)
        db.commit()
        event_id = str(test_event.id)
    finally:
        db.close()

    # 1. Primer RSVP exitoso
    res1 = client.post(f"/api/v1/events/{event_id}/rsvp")
    assert res1.status_code == 200
    assert res1.json()["current_rsvp_count"] == 1
    assert res1.json()["spots_remaining"] == 1

    # 2. Segundo RSVP exitoso (se llena el cupo)
    res2 = client.post(f"/api/v1/events/{event_id}/rsvp")
    assert res2.status_code == 200
    assert res2.json()["current_rsvp_count"] == 2
    assert res2.json()["spots_remaining"] == 0

    # 3. Tercer RSVP debe fallar por cupo agotado (HTTP 400)
    res3 = client.post(f"/api/v1/events/{event_id}/rsvp")
    assert res3.status_code == 400
    assert "agotado" in res3.json()["detail"].lower()


def test_civic_notices_and_priority_ordering():
    # 1. Listado de avisos debe traer alertas de zona primero
    res = client.get("/api/v1/notices")
    assert res.status_code == 200
    notices = res.json()
    assert len(notices) >= 1
    
    # El primer aviso en la lista debe ser tipo alerta_zona si existe
    has_alerta = any(n["type"] == "alerta_zona" for n in notices)
    if has_alerta:
        assert notices[0]["type"] == "alerta_zona"

    # 2. Envío público de aviso válido (mascota perdida)
    public_notice = {
        "title": "Gatita siamesa extraviada",
        "content": "Se extravió esta tarde en Coto Ceiba. Lleva cascabel rosa.",
        "type": "mascota_perdida",
        "contact_whatsapp": "+523315559090"
    }
    res_pub = client.post("/api/v1/notices/submit", json=public_notice)
    assert res_pub.status_code == 201
    created = res_pub.json()
    assert created["status"] == "pending_moderation"
    assert created["is_official"] is False

    # 3. Envío público con tipo prohibido (alerta_zona) debe ser rechazado
    forbidden_notice = {
        "title": "Alerta falsa de corte de agua",
        "content": "Habrá corte en todo el fraccionamiento sin previo aviso.",
        "type": "alerta_zona"
    }
    res_forb = client.post("/api/v1/notices/submit", json=forbidden_notice)
    assert res_forb.status_code == 422


def test_official_notice_admin_protection():
    # 1. Intento sin token debe ser 401
    payload = {
        "title": "Cierre de vialidad por maratón vecinal",
        "content": "Se cerrará el circuito interior de 07:00 a 10:00 hrs este domingo.",
        "type": "comunicado_oficial"
    }
    res_unauth = client.post("/api/v1/admin/notices/official", json=payload)
    assert res_unauth.status_code == 401

    # 2. Con token válido de administrador
    headers = {"X-Admin-Token": "natura_admin_secret_2026"}
    res_auth = client.post("/api/v1/admin/notices/official", json=payload, headers=headers)
    assert res_auth.status_code == 201
    official = res_auth.json()
    assert official["is_official"] is True
    assert official["status"] == "active"


def test_auto_expiry_task():
    db = SessionLocal()
    try:
        past_time = datetime.now(timezone.utc) - timedelta(hours=2)
        expired_notice = CivicNotice(
            id=uuid.uuid4(),
            type=CivicNoticeType.MASCOTA_PERDIDA,
            title="Aviso de prueba vencido",
            content="Este aviso ya expiró en el pasado.",
            expires_at=past_time,
            status=CivicNoticeStatus.ACTIVE
        )
        db.add(expired_notice)
        db.commit()
        notice_id = expired_notice.id
    finally:
        db.close()

    # Ejecutar la tarea de auto-expiración
    expired_count = expire_outdated_notices()
    assert expired_count >= 1

    # Verificar que el registro ahora tenga status == expired
    db = SessionLocal()
    try:
        updated = db.query(CivicNotice).filter(CivicNotice.id == notice_id).first()
        assert updated.status == CivicNoticeStatus.EXPIRED
    finally:
        db.close()
