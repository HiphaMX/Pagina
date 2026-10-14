from sqlalchemy import Boolean, Column, DateTime, Integer, String, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base


class WebHealthAudit(Base):
    __tablename__ = "web_health_audits"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=True, index=True)
    client_name = Column(String(255), nullable=True)
    domain = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=True)
    is_up = Column(Boolean, default=True, index=True)
    response_time_ms = Column(Float, nullable=True)
    ssl_valid = Column(Boolean, default=True)
    ssl_days_remaining = Column(Integer, nullable=True)
    ssl_issuer = Column(String(255), nullable=True)
    dns_spf_status = Column(String(50), nullable=True)
    dns_spf_record = Column(Text, nullable=True)
    dns_dmarc_status = Column(String(50), nullable=True)
    dns_dmarc_record = Column(Text, nullable=True)
    smtp_status = Column(String(50), nullable=True)
    maps_status = Column(String(50), nullable=True)
    has_llms_txt = Column(Boolean, default=False)
    has_robots_txt = Column(Boolean, default=False)
    robots_allows_ai = Column(Boolean, default=False)
    overall_score = Column(Integer, default=100)
    health_level = Column(String(20), default="HEALTHY", index=True)  # HEALTHY, WARNING, CRITICAL
    issues_summary = Column(Text, nullable=True)  # JSON array as string
    details_json = Column(Text, nullable=True)  # Full JSON details
    agent_recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
