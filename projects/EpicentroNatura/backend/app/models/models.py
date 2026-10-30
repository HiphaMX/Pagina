import enum
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    JSON,
    Index
)
from sqlalchemy.orm import relationship
from app.database import Base, GUID


# --- ENUMS ---

class CommunityType(str, enum.Enum):
    COTO_NATURA = "coto_natura"
    FRACCIONAMIENTO_VECINO = "fraccionamiento_vecino"
    ESPACIO_PUBLICO = "espacio_publico"


class BusinessStatus(str, enum.Enum):
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class BusinessType(str, enum.Enum):
    LOCAL_ESTABLECIDO = "local_establecido"
    EMPRENDIMIENTO = "emprendimiento"
    SERVICIOS_PROFESIONALES = "servicios_profesionales"


class TargetAudience(str, enum.Enum):
    KIDS = "kids"
    FAMILY = "family"
    ADULTS = "adults"
    ALL = "all"


class CivicNoticeType(str, enum.Enum):
    ALERTA_ZONA = "alerta_zona"
    COMUNICADO_OFICIAL = "comunicado_oficial"
    MASCOTA_PERDIDA = "mascota_perdida"
    EMPLEO_LOCAL = "empleo_local"
    CAUSA_SOCIAL = "causa_social"


class CivicNoticeStatus(str, enum.Enum):
    PENDING_MODERATION = "pending_moderation"
    ACTIVE = "active"
    EXPIRED = "expired"
    ARCHIVED = "archived"


def get_utc_now():
    return datetime.now(timezone.utc)


def default_notice_expiration():
    return datetime.now(timezone.utc) + timedelta(days=15)


# --- MODELS ---

class Community(Base):
    __tablename__ = "communities"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False)
    slug = Column(String(120), unique=True, index=True, nullable=False)
    type = Column(SAEnum(CommunityType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    businesses = relationship("Business", back_populates="community", cascade="all, delete-orphan")
    notices = relationship("CivicNotice", back_populates="community")


class BusinessCategory(Base):
    __tablename__ = "business_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    icon_name = Column(String(50), nullable=False)

    businesses = relationship("Business", back_populates="category")


class Business(Base):
    __tablename__ = "businesses"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    community_id = Column(GUID, ForeignKey("communities.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("business_categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    business_type = Column(
        SAEnum(BusinessType, values_callable=lambda x: [e.value for e in x]),
        default=BusinessType.LOCAL_ESTABLECIDO,
        nullable=False,
        index=True
    )
    is_home_based = Column(Boolean, default=False, nullable=False, index=True)
    address_reference = Column(String(255), nullable=True)
    phone_number = Column(String(25), nullable=True)
    whatsapp_number = Column(String(25), nullable=False)
    delivery_available = Column(Boolean, default=False, nullable=False, index=True)
    delivery_scope = Column(Text, nullable=True)
    has_km0_badge = Column(Boolean, default=False, nullable=False, index=True)
    km0_reason = Column(String(255), nullable=True)
    opening_hours = Column(JSON, nullable=True)
    status = Column(
        SAEnum(BusinessStatus, values_callable=lambda x: [e.value for e in x]),
        default=BusinessStatus.PENDING_APPROVAL,
        nullable=False,
        index=True
    )
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    community = relationship("Community", back_populates="businesses")
    category = relationship("BusinessCategory", back_populates="businesses")


class CulturalEvent(Base):
    __tablename__ = "cultural_events"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    organizer = Column(String(100), default="Casa de la Cultura", nullable=False)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    location_name = Column(String(150), default="Parque Central Natura", nullable=False)
    target_audience = Column(
        SAEnum(TargetAudience, values_callable=lambda x: [e.value for e in x]),
        default=TargetAudience.ALL,
        nullable=False
    )
    capacity_limit = Column(Integer, nullable=True)
    current_rsvp_count = Column(Integer, default=0, nullable=False)
    is_cancelled = Column(Boolean, default=False, nullable=False, index=True)


class CivicNotice(Base):
    __tablename__ = "civic_notices"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    community_id = Column(GUID, ForeignKey("communities.id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(
        SAEnum(CivicNoticeType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )
    title = Column(String(150), nullable=False)
    content = Column(Text, nullable=False)
    contact_whatsapp = Column(String(25), nullable=True)
    is_official = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), default=default_notice_expiration, nullable=False, index=True)
    status = Column(
        SAEnum(CivicNoticeStatus, values_callable=lambda x: [e.value for e in x]),
        default=CivicNoticeStatus.PENDING_MODERATION,
        nullable=False,
        index=True
    )

    community = relationship("Community", back_populates="notices")


# Índices compuestos útiles para búsquedas eficientes
Index("idx_notice_active_expiry", CivicNotice.status, CivicNotice.expires_at)
Index("idx_business_status_home", Business.status, Business.is_home_based)
Index("idx_event_active_start", CulturalEvent.is_cancelled, CulturalEvent.start_datetime)
