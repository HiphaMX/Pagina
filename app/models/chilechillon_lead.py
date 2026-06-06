from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from app.core.database import Base

class ChileChillonLead(Base):
    __tablename__ = "chilechillon_leads"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefono = Column(String, nullable=True)
    prediccion_campeon = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
