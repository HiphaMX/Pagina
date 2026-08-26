from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func
from app.core.database import Base

class HealthyIceOrder(Base):
    __tablename__ = "healthyice_orders"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    telefono = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    carrito_items = Column(String, nullable=False)  # Serializado en JSON
    total = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="pending_payment")
    mercadopago_payment_id = Column(String, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
