from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("agency_clients.id", ondelete="SET NULL"), nullable=True)
    platform = Column(String(20), nullable=False)  # "instagram", "facebook"
    name = Column(String(100), nullable=False)
    handle = Column(String(100), nullable=True)  # ej. "@chilechillon"
    url = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    status = Column(String(20), default="active")  # "active", "paused", "archived"
    notes = Column(Text, nullable=True)
    initial_followers = Column(Integer, nullable=True, default=0)  # Seguidores al iniciar con la agencia
    initial_date = Column(DateTime(timezone=True), nullable=True)  # Fecha/mes en que arranca el monitoreo
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    client = relationship("AgencyClient", backref="social_accounts")
    snapshots = relationship("SocialSnapshot", back_populates="account", cascade="all, delete-orphan", order_by="desc(SocialSnapshot.recorded_at)")


class SocialSnapshot(Base):
    __tablename__ = "social_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    followers = Column(Integer, nullable=False, default=0)
    growth_count = Column(Integer, nullable=True, default=0)  # Crecimiento respecto al snapshot anterior
    is_manual = Column(Boolean, default=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    account = relationship("SocialAccount", back_populates="snapshots")
