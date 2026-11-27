import uuid
from typing import Optional
from sqlalchemy import Column, DateTime, Float, String, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class EpicentroRegistration(Base):
    __tablename__ = "epicentro_registrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_name = Column(String(150), nullable=False, index=True)
    slug = Column(String(150), nullable=True, index=True)
    category_slug = Column(String(80), nullable=False, index=True)
    category_label = Column(String(100), nullable=True)
    subcategory_slug = Column(String(100), nullable=True, index=True)
    subcategory_label = Column(String(120), nullable=True)
    coto_address = Column(String(255), nullable=False)
    business_type = Column(String(50), default="local-establecido")
    space_label = Column(String(100), nullable=True)
    owner_name = Column(String(120), nullable=False)
    email = Column(String(150), nullable=False, index=True)
    phone = Column(String(30), nullable=False)
    whatsapp = Column(String(30), nullable=False)
    preferred_contact_methods = Column(String(255), nullable=True)
    schedule = Column(String(150), nullable=True)
    delivery_available = Column(Boolean, default=False)
    coto_only_delivery = Column(Boolean, default=False)
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    photos = Column(Text, nullable=True)  # JSON array de hasta 10 fotos para micrositios
    cover_photo = Column(Text, nullable=True)  # URL de foto de portada del hero
    microsite_data = Column(Text, nullable=True)  # JSON estructurado: productos destacados y hasta 4 secciones de menú sin foto
    kam_name = Column(String(100), nullable=True)
    payment_method = Column(String(50), nullable=True)

    # Paso 1 de Validación: Correo Electrónico
    email_otp = Column(String(10), nullable=True)
    email_otp_expires_at = Column(DateTime(timezone=True), nullable=True)
    email_verified = Column(Boolean, default=False, index=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)

    # Paso 2 de Validación: WhatsApp
    whatsapp_code = Column(String(20), nullable=True, index=True)
    whatsapp_verified = Column(Boolean, default=False, index=True)
    whatsapp_verified_at = Column(DateTime(timezone=True), nullable=True)

    # Pasarela de Pagos (Mercado Pago - Botica Silvestre)
    mercadopago_preference_id = Column(String(100), nullable=True, index=True)
    mercadopago_payment_id = Column(String(100), nullable=True, index=True)
    payment_status = Column(String(30), default="pending", index=True)  # pending, approved, rejected
    payment_amount = Column(Float, default=499.0)
    is_verified_badge = Column(Boolean, default=False)
    coupon_code = Column(String(50), nullable=True)

    # Token Seguro para Autoservicio de Fotos y Catálogo
    edit_token = Column(String(64), nullable=True, index=True)
    edit_token_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Flujo de Moderación:
    # pending_verification -> pending_approval -> active / rejected / suspended
    status = Column(String(30), default="pending_verification", index=True)
    moderation_notes = Column(Text, nullable=True)

    # Agente Centinela IA y Términos y Condiciones
    ai_moderation_status = Column(String(30), default="pending", index=True)  # pending, passed, flagged, violation
    ai_moderation_notes = Column(Text, nullable=True)
    ai_moderated_at = Column(DateTime(timezone=True), nullable=True)
    terms_accepted = Column(Boolean, default=True)
    terms_accepted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EpicentroBlacklist(Base):
    __tablename__ = "epicentro_blacklist"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    phone = Column(String(30), nullable=True, index=True)
    email = Column(String(150), nullable=True, index=True)
    business_name = Column(String(150), nullable=True)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def delivery_badge(self) -> Optional[str]:
        name_l = (self.business_name or "").lower()
        if "amdi" in name_l:
            return "Visitas en cotos"
        if "jessica" in name_l:
            return "Cita en domicilio"
        if "valencia" in name_l:
            return "Servicio a domicilio"
        if self.coto_only_delivery:
            return "Solo entregas en su coto"
        if self.delivery_available:
            return "Servicio a domicilio"
        return None

    @property
    def pickup_badge(self) -> Optional[str]:
        name_l = (self.business_name or "").lower()
        if "amdi" in name_l:
            return "Cita previa"
        if "jessica" in name_l:
            return "Atención coordinada"
        if "valencia" in name_l:
            return "Atención en coto"
        if self.category_slug in ("servicios-profesionales", "servicios-hogar"):
            return "Previa cita"
        if self.coto_only_delivery:
            return "Recoger en caseta"
        return "Recoger en local"
