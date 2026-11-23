import uuid
from sqlalchemy import Column, DateTime, Float, Integer, String, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class EpicentroCoupon(Base):
    __tablename__ = "epicentro_coupons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(150), default="Cortesía 100% Exenta (Un solo uso)")
    discount_percent = Column(Float, default=100.0)
    max_uses = Column(Integer, default=1)
    times_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    used_by_registration_id = Column(String(36), nullable=True, index=True)
    business_name = Column(String(150), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
