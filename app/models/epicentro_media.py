import uuid
from sqlalchemy import Column, DateTime, String, Text, LargeBinary
from sqlalchemy.sql import func
from app.core.database import Base


class EpicentroMedia(Base):
    __tablename__ = "epicentro_media"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    filename = Column(String(150), nullable=True)
    content_type = Column(String(50), default="image/webp")
    data_base64 = Column(Text, nullable=False)  # WebP comprimido optimizado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
