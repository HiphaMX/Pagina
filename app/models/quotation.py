from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(50), unique=True, index=True, nullable=False)
    client_name = Column(String(255), nullable=False, index=True)
    client_contact = Column(String(255), nullable=True)
    client_email = Column(String(255), nullable=True)
    client_phone = Column(String(50), nullable=True)
    client_id = Column(Integer, ForeignKey("agency_clients.id", ondelete="SET NULL"), nullable=True, index=True)

    date = Column(DateTime, nullable=False, default=func.now())
    validity_days = Column(Integer, default=30)
    currency = Column(String(10), default="MXN")

    # Lista de items: [{"name": str, "description": str, "quantity": float, "unit_price": float, "subtotal": float}]
    items_json = Column(JSON, nullable=False, default=list)

    subtotal = Column(Float, nullable=False, default=0.0)
    apply_tax = Column(Boolean, default=True)
    tax_rate = Column(Float, default=0.16)
    tax_amount = Column(Float, default=0.0)
    total = Column(Float, nullable=False, default=0.0)

    require_down_payment = Column(Boolean, default=True)
    down_payment_rate = Column(Float, default=0.50)  # 50% de anticipo
    down_payment_amount = Column(Float, default=0.0)

    notes = Column(Text, nullable=True)
    status = Column(String(20), default="BORRADOR", index=True)  # BORRADOR, ENVIADA, ACEPTADA, CANCELADA

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    @property
    def items(self):
        return self.items_json or []

