from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class WebHealthItemSchema(BaseModel):
    id: Optional[int] = None
    client_id: Optional[int] = None
    client_name: Optional[str] = None
    domain: str
    url: str
    status_code: Optional[int] = 200
    is_up: bool = True
    response_time_ms: Optional[float] = 0.0
    ssl_valid: bool = True
    ssl_days_remaining: Optional[int] = None
    ssl_issuer: Optional[str] = None
    dns_spf_status: Optional[str] = "OK"
    dns_spf_record: Optional[str] = None
    dns_dmarc_status: Optional[str] = "OK"
    dns_dmarc_record: Optional[str] = None
    smtp_status: Optional[str] = "OK"
    maps_status: Optional[str] = "OK"
    has_llms_txt: bool = False
    has_robots_txt: bool = False
    robots_allows_ai: bool = False
    overall_score: int = 100
    health_level: str = "HEALTHY"
    issues_summary: List[str] = []
    details_json: Optional[Dict[str, Any]] = None
    agent_recommendation: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WebHealthOverviewKPIs(BaseModel):
    total_sites: int = 0
    healthy_sites: int = 0
    warning_sites: int = 0
    critical_sites: int = 0
    avg_response_time_ms: float = 0.0
    ssl_expiring_soon_count: int = 0  # < 30 days
    smtp_ok_count: int = 0
    maps_ok_count: int = 0
    llms_txt_count: int = 0
    last_audit_time: Optional[datetime] = None


class WebHealthOverviewResponse(BaseModel):
    kpis: WebHealthOverviewKPIs
    agent_summary: str
    sites: List[WebHealthItemSchema]
    last_audit_iso: Optional[str] = None


class RunAuditRequest(BaseModel):
    client_id: Optional[int] = None
    domain: Optional[str] = None
    use_ai: bool = True
