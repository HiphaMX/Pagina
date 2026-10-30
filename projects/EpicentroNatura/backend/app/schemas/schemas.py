import re
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.models import (
    CommunityType,
    BusinessStatus,
    BusinessType,
    TargetAudience,
    CivicNoticeType,
    CivicNoticeStatus,
)


# --- COMUNIDAD ---

class CommunityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=2, max_length=120)
    type: CommunityType
    is_active: bool = True


class CommunityCreate(CommunityBase):
    pass


class CommunityOut(CommunityBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


# --- CATEGORÍA DE COMERCIO ---

class BusinessCategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    icon_name: str = Field(default="Store", max_length=50)


class BusinessCategoryCreate(BusinessCategoryBase):
    pass


class BusinessCategoryOut(BusinessCategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- COMERCIO / EMPRENDIMIENTO ---

class BusinessRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Nombre del negocio o emprendimiento")
    category_id: int = Field(..., description="ID de la categoría comercial")
    community_id: Optional[UUID] = Field(None, description="ID del coto si es dentro de coto")
    description: Optional[str] = Field(None, max_length=1000)
    business_type: BusinessType = Field(BusinessType.LOCAL_ESTABLECIDO, description="Tipo de oferta comercial")
    is_home_based: bool = Field(False, description="True si es emprendimiento dentro de coto")
    address_reference: Optional[str] = Field(None, max_length=255, description="Número de casa, local, interior o cruce")
    phone_number: Optional[str] = Field(None, description="Teléfono para llamadas de contacto directo")
    whatsapp_number: str = Field(..., description="Teléfono internacional en formato E.164 ej: +523312345678")
    delivery_available: bool = Field(False, description="Indica si cuenta con servicio a domicilio")
    delivery_scope: Optional[str] = Field(None, max_length=500, description="Alcance o cotos con entrega")
    has_km0_badge: bool = Field(False, description="Distintivo Sello Verde Km 0 (0 Emisiones)")
    km0_reason: Optional[str] = Field(None, max_length=255, description="Motivo del distintivo ecológico")
    opening_hours: Optional[Dict[str, Any]] = Field(
        None,
        description="Estructura JSON ej: {'mon': {'open': '09:00', 'close': '18:00'}, ...}"
    )

    @field_validator("whatsapp_number")
    @classmethod
    def validate_whatsapp(cls, v: str) -> str:
        # Validación de formato E.164 (+ seguido de 8 a 15 dígitos) o 10/12 dígitos nacionales
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?[1-9]\d{7,14}$", cleaned):
            raise ValueError("El número de WhatsApp debe tener un formato telefónico válido (ej: +523312345678 o 3312345678)")
        return cleaned


class BusinessOut(BaseModel):
    id: UUID
    community_id: Optional[UUID]
    category_id: int
    name: str
    slug: str
    description: Optional[str]
    business_type: BusinessType = BusinessType.LOCAL_ESTABLECIDO
    is_home_based: bool
    address_reference: Optional[str]
    phone_number: Optional[str] = None
    whatsapp_number: str
    delivery_available: bool
    delivery_scope: Optional[str]
    has_km0_badge: bool = False
    km0_reason: Optional[str] = None
    opening_hours: Optional[Dict[str, Any]]
    status: BusinessStatus
    created_at: datetime

    category: Optional[BusinessCategoryOut] = None
    community: Optional[CommunityOut] = None

    # Campos enriquecidos calculados en tiempo real
    is_open_now: bool = False
    opening_status_text: Optional[str] = None
    whatsapp_link: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- EVENTO CULTURAL ---

class CulturalEventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    slug: Optional[str] = None
    organizer: str = Field(default="Casa de la Cultura", max_length=100)
    description: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    location_name: str = Field(default="Parque Central Natura", max_length=150)
    target_audience: TargetAudience = TargetAudience.ALL
    capacity_limit: Optional[int] = Field(None, ge=1)


class CulturalEventCreate(CulturalEventBase):
    pass


class CulturalEventOut(BaseModel):
    id: UUID
    title: str
    slug: str
    organizer: str
    description: Optional[str]
    start_datetime: datetime
    end_datetime: datetime
    location_name: str
    target_audience: TargetAudience
    capacity_limit: Optional[int]
    current_rsvp_count: int
    is_cancelled: bool

    # Campos calculados
    is_sold_out: bool = False
    spots_remaining: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class RSVPResponse(BaseModel):
    success: bool
    message: str
    event_id: UUID
    current_rsvp_count: int
    spots_remaining: Optional[int] = None


# --- AVISOS CÍVICOS ---

class CivicNoticeSubmit(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    content: str = Field(..., min_length=10, max_length=3000)
    type: CivicNoticeType
    community_id: Optional[UUID] = None
    contact_whatsapp: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_public_type(cls, v: CivicNoticeType) -> CivicNoticeType:
        # Los envíos públicos no pueden auto-proclamarse como comunicados oficiales ni alertas de zona
        if v in [CivicNoticeType.COMUNICADO_OFICIAL, CivicNoticeType.ALERTA_ZONA]:
            raise ValueError("Las alertas de zona y comunicados oficiales sólo pueden ser publicados por administración")
        return v


class CivicNoticeOfficialCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    content: str = Field(..., min_length=10, max_length=3000)
    type: CivicNoticeType = CivicNoticeType.COMUNICADO_OFICIAL
    community_id: Optional[UUID] = None
    contact_whatsapp: Optional[str] = None
    expires_at: Optional[datetime] = None


class CivicNoticeOut(BaseModel):
    id: UUID
    community_id: Optional[UUID]
    type: CivicNoticeType
    title: str
    content: str
    contact_whatsapp: Optional[str]
    is_official: bool
    published_at: datetime
    expires_at: datetime
    status: CivicNoticeStatus

    community: Optional[CommunityOut] = None
    days_remaining: int = 0
    whatsapp_link: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
