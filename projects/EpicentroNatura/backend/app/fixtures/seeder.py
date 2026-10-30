import json
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta

# Asegurar path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database import SessionLocal, init_db
from app.models.models import (
    Community,
    CommunityType,
    BusinessCategory,
    Business,
    BusinessStatus,
    BusinessType,
    CulturalEvent,
    TargetAudience,
    CivicNotice,
    CivicNoticeType,
    CivicNoticeStatus,
)


def run_seeder():
    print("🚀 [Epicentro Natura Seeder] Iniciando carga de datos...")
    init_db()
    
    fixtures_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
    if not os.path.exists(fixtures_path):
        print(f"❌ No se encontró el archivo de fixtures en: {fixtures_path}")
        return

    with open(fixtures_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    try:
        # 1. Cargar Comunidades
        community_map = {}
        for c in data.get("communities", []):
            existing = db.query(Community).filter(Community.slug == c["slug"]).first()
            if not existing:
                comm = Community(
                    id=uuid.uuid4(),
                    name=c["name"],
                    slug=c["slug"],
                    type=CommunityType(c["type"]),
                    is_active=c.get("is_active", True)
                )
                db.add(comm)
                db.flush()
                community_map[c["slug"]] = comm
            else:
                community_map[c["slug"]] = existing

        print(f"✓ Comunidades procesadas: {len(community_map)}")

        # 2. Cargar Categorías
        category_map = {}
        for cat in data.get("categories", []):
            existing = db.query(BusinessCategory).filter(BusinessCategory.slug == cat["slug"]).first()
            if not existing:
                new_cat = BusinessCategory(
                    id=cat.get("id"),
                    name=cat["name"],
                    slug=cat["slug"],
                    icon_name=cat["icon_name"]
                )
                db.add(new_cat)
                db.flush()
                category_map[cat["slug"]] = new_cat
            else:
                category_map[cat["slug"]] = existing

        print(f"✓ Categorías procesadas: {len(category_map)}")

        # 3. Cargar Negocios
        businesses_created = 0
        for b in data.get("businesses", []):
            existing = db.query(Business).filter(Business.slug == b["slug"]).first()
            if not existing:
                cat = category_map.get(b["category_slug"])
                comm = community_map.get(b["community_slug"]) if b.get("community_slug") else None
                
                new_biz = Business(
                    id=uuid.uuid4(),
                    category_id=cat.id if cat else 1,
                    community_id=comm.id if comm else None,
                    name=b["name"],
                    slug=b["slug"],
                    description=b.get("description"),
                    business_type=BusinessType(b.get("business_type", "local_establecido")),
                    is_home_based=b.get("is_home_based", False),
                    address_reference=b.get("address_reference"),
                    phone_number=b.get("phone_number"),
                    whatsapp_number=b["whatsapp_number"],
                    delivery_available=b.get("delivery_available", False),
                    delivery_scope=b.get("delivery_scope"),
                    has_km0_badge=b.get("has_km0_badge", False),
                    km0_reason=b.get("km0_reason"),
                    opening_hours=b.get("opening_hours"),
                    status=BusinessStatus(b.get("status", "active")),
                    created_at=datetime.now(timezone.utc)
                )
                db.add(new_biz)
                businesses_created += 1

        print(f"✓ Comercios nuevos agregados: {businesses_created}")

        # 4. Cargar Eventos Culturales
        events_created = 0
        now_utc = datetime.now(timezone.utc)
        for ev in data.get("cultural_events", []):
            existing = db.query(CulturalEvent).filter(CulturalEvent.slug == ev["slug"]).first()
            if not existing:
                days_ahead = ev.get("days_ahead_start", 2)
                start_dt = now_utc + timedelta(days=days_ahead, hours=10)
                end_dt = start_dt + timedelta(hours=ev.get("duration_hours", 2))

                new_event = CulturalEvent(
                    id=uuid.uuid4(),
                    title=ev["title"],
                    slug=ev["slug"],
                    organizer=ev.get("organizer", "Casa de la Cultura"),
                    description=ev.get("description"),
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    location_name=ev.get("location_name", "Parque Central Natura"),
                    target_audience=TargetAudience(ev.get("target_audience", "all")),
                    capacity_limit=ev.get("capacity_limit"),
                    current_rsvp_count=ev.get("current_rsvp_count", 0),
                    is_cancelled=ev.get("is_cancelled", False)
                )
                db.add(new_event)
                events_created += 1

        print(f"✓ Eventos culturales nuevos agregados: {events_created}")

        # 5. Cargar Avisos Cívicos
        notices_created = 0
        for n in data.get("civic_notices", []):
            comm = community_map.get(n.get("community_slug")) if n.get("community_slug") else None
            days_valid = n.get("days_valid", 15)
            expires_at = now_utc + timedelta(days=days_valid)

            new_notice = CivicNotice(
                id=uuid.uuid4(),
                community_id=comm.id if comm else None,
                type=CivicNoticeType(n["type"]),
                title=n["title"],
                content=n["content"],
                contact_whatsapp=n.get("contact_whatsapp"),
                is_official=n.get("is_official", False),
                published_at=now_utc,
                expires_at=expires_at,
                status=CivicNoticeStatus(n.get("status", "active"))
            )
            db.add(new_notice)
            notices_created += 1

        print(f"✓ Avisos cívicos nuevos agregados: {notices_created}")

        db.commit()
        print("🎉 ¡Siembra de base de datos para Epicentro Natura completada con éxito!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    run_seeder()
