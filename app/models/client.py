from sqlalchemy import Boolean, Column, DateTime, Integer, String, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base

class AgencyClient(Base):
    __tablename__ = "agency_clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    contact_name = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    service_type = Column(String, default="design_subscription")  # "design_subscription", "web_subscription", "marketing_subscription", "single_service"
    billing_period = Column(String, default="monthly", nullable=True)  # "monthly", "annual"
    billing_day = Column(Integer, nullable=True, default=1)  # 1 al 31 día de corte / pago adelantado
    monthly_fee = Column(Float, nullable=True, default=0.0)  # Monto de suscripción en MXN (mensual o anual según billing_period)
    requires_invoice = Column(Boolean, default=False, nullable=True)  # True si requiere CFDI (+16% IVA)
    apply_tax_retention = Column(Boolean, default=False, nullable=True)  # True si es Persona Moral (retención de ISR)
    tax_retention_rate = Column(Float, default=1.25, nullable=True)  # Tasa de retención de ISR (ej. 1.25% para PM en RESICO)
    start_date = Column(String(10), nullable=True)  # YYYY-MM-DD
    status = Column(String, default="active")  # "active", "paused", "inactive"
    website_url = Column(String, nullable=True)
    ga4_property_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
