from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, model_validator


class AgencyClientBase(BaseModel):
    name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    service_type: Optional[str] = "design_subscription"  # "design_subscription", "web_subscription", "marketing_subscription", "single_service"
    billing_period: Optional[str] = "monthly"  # "monthly", "annual"
    billing_day: Optional[int] = 1
    monthly_fee: Optional[float] = 0.0
    requires_invoice: Optional[bool] = False
    apply_tax_retention: Optional[bool] = False
    tax_retention_rate: Optional[float] = 1.25
    start_date: Optional[str] = None
    status: Optional[str] = "active"
    website_url: Optional[str] = None
    ga4_property_id: Optional[str] = None
    notes: Optional[str] = None


class AgencyClientCreate(AgencyClientBase):
    pass


class AgencyClientUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    service_type: Optional[str] = None
    billing_period: Optional[str] = None
    billing_day: Optional[int] = None
    monthly_fee: Optional[float] = None
    requires_invoice: Optional[bool] = None
    apply_tax_retention: Optional[bool] = None
    tax_retention_rate: Optional[float] = None
    start_date: Optional[str] = None
    status: Optional[str] = None
    website_url: Optional[str] = None
    ga4_property_id: Optional[str] = None
    notes: Optional[str] = None


class AgencyClient(AgencyClientBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EmailAttachmentPayload(BaseModel):
    filename: str
    content_base64: str
    content_type: Optional[str] = "application/pdf"


class SendAgencyEmailRequest(BaseModel):
    to_email: str
    subject: str
    message: Optional[str] = None
    message_body: Optional[str] = None
    client_name: Optional[str] = ""
    client_id: Optional[int] = None
    attachments: Optional[List[EmailAttachmentPayload]] = None

    @model_validator(mode="after")
    def validate_message(self):
        msg = self.message or self.message_body
        if not msg or not msg.strip():
            raise ValueError("El mensaje no puede estar vacío")
        self.message = msg
        return self


class SentEmailLogResponse(BaseModel):
    id: int
    client_id: Optional[int] = None
    client_name: Optional[str] = None
    to_email: str
    subject: str
    message_body: str
    sender_email: Optional[str] = "hola@hipha.mx"
    sent_by_user: Optional[str] = None
    has_attachments: bool = False
    attachment_names: Optional[str] = None
    status: str = "sent"
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
