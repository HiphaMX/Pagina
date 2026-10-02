from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from app.core.database import Base


class SentEmailLog(Base):
    __tablename__ = "sent_email_logs"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("agency_clients.id", ondelete="SET NULL"), nullable=True, index=True)
    client_name = Column(String(150), nullable=True)
    to_email = Column(String(255), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    message_body = Column(Text, nullable=False)
    sender_email = Column(String(255), default="hola@hipha.mx")
    sent_by_user = Column(String(255), nullable=True)
    has_attachments = Column(Boolean, default=False)
    attachment_names = Column(Text, nullable=True)
    status = Column(String(50), default="sent", index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
