from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class QuotationItemSchema(BaseModel):
    name: str = Field(..., description="Nombre del servicio o concepto")
    description: Optional[str] = Field("", description="Descripción detallada o entregables incluidos")
    quantity: float = Field(1.0, description="Cantidad")
    unit_price: float = Field(0.0, description="Precio unitario en MXN")
    subtotal: Optional[float] = Field(None, description="Importe total de este concepto")


class QuotationCreateSchema(BaseModel):
    folio: Optional[str] = None
    client_name: str
    client_contact: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_id: Optional[int] = None
    date: Optional[datetime] = None
    validity_days: int = 30
    currency: str = "MXN"
    items: List[QuotationItemSchema]
    apply_tax: bool = True
    tax_rate: float = 0.16
    down_payment_rate: float = 0.50
    notes: Optional[str] = None
    status: str = "BORRADOR"


class QuotationResponseSchema(BaseModel):
    id: int
    folio: str
    client_name: str
    client_contact: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_id: Optional[int] = None
    date: datetime
    validity_days: int
    currency: str
    items: List[QuotationItemSchema]
    subtotal: float
    apply_tax: bool
    tax_rate: float
    tax_amount: float
    total: float
    down_payment_rate: float
    down_payment_amount: float
    notes: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CatalogServiceItem(BaseModel):
    id: str
    name: str
    category: str  # "Suscripción" o "Servicio Adicional"
    description: str
    price: float
    unit_label: str  # "/ mes", "/ año", "x servicio", "x pieza", "x video"
    is_custom: bool = False
