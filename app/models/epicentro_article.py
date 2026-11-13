import uuid
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func
from app.core.database import Base


class EpicentroArticle(Base):
    __tablename__ = "epicentro_articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    slug = Column(String(160), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(String(350), nullable=False)
    content_html = Column(Text, nullable=False)
    cover_image_url = Column(Text, nullable=False)
    gallery_images = Column(Text, nullable=True)  # JSON array de URLs adicionales
    category = Column(String(50), default="cronica", index=True)  # cronica, evento, comunicado, editorial
    author_name = Column(String(120), nullable=False)
    author_role = Column(String(120), nullable=True)
    author_avatar = Column(Text, nullable=True)
    author_id = Column(String(50), nullable=True, index=True)  # identificador del redactor (ej. editor_1, editor_2)
    status = Column(String(20), default="published", index=True)  # draft, published, archived
    views_count = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
