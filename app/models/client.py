from sqlalchemy import Column, DateTime, Integer, String, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base

class AgencyClient(Base):
    __tablename__ = "agency_clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    contact_name = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    service_type = Column(String, default="design")  # "design", "web_design", "seo_ads", "complete"
    billing_day = Column(Integer, nullable=True, default=1)  # 1 al 31 día de corte / pago adelantado
    monthly_fee = Column(Float, nullable=True, default=0.0)  # Monto de suscripción en MXN
    start_date = Column(String(10), nullable=True)  # YYYY-MM-DD
    status = Column(String, default="active")  # "active", "paused", "inactive"
    website_url = Column(String, nullable=True)
    ga4_property_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
