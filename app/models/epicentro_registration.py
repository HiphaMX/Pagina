import uuid
from sqlalchemy import Column, DateTime, Float, String, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class EpicentroRegistration(Base):
    __tablename__ = "epicentro_registrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_name = Column(String(150), nullable=False, index=True)
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
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    photos = Column(Text, nullable=True)  # JSON array de hasta 10 fotos para micrositios
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
    payment_amount = Column(Float, default=99.0)
    is_verified_badge = Column(Boolean, default=False)

    # Flujo de Moderación:
    # pending_verification -> pending_approval -> active / rejected
    status = Column(String(30), default="pending_verification", index=True)
    moderation_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
