from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# --- SAT Account Schemas ---
class SatAccountBase(BaseModel):
    rfc: str
    name: str
    is_active: Optional[bool] = True


class SatAccountCreate(SatAccountBase):
    pass


class SatAccountUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class SatAccount(SatAccountBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- SAT Invoice Schemas ---
class SatInvoiceBase(BaseModel):
    account_rfc: str
    uuid: str
    emisor_rfc: str
    emisor_nombre: Optional[str] = None
    receptor_rfc: str
    receptor_nombre: Optional[str] = None
    fecha_emision: datetime
    tipo_comprobante: Optional[str] = None
    subtotal: Optional[float] = 0.0
    total: Optional[float] = 0.0
    iva_trasladado: Optional[float] = 0.0
    iva_retenido: Optional[float] = 0.0
    isr_retenido: Optional[float] = 0.0
    tipo_cfdi: str  # "emitida" o "recibida"
    conceptos_resumen: Optional[str] = None


class SatInvoice(SatInvoiceBase):
    id: int
    xml_content: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- SAT Download Request Schemas ---
class SatDownloadRequestBase(BaseModel):
    account_rfc: str
    id_solicitud: str
    fecha_inicio: datetime
    fecha_fin: datetime
    tipo_cfdi: str  # "emitidas" o "recibidas"
    status: str
    intentos: int
    mensaje_error: Optional[str] = None


class SatDownloadRequest(SatDownloadRequestBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- API Request/Response Schemas ---
class SatSyncRequest(BaseModel):
    rfc: str
    fecha_inicio: str  # YYYY-MM-DD
    fecha_fin: str     # YYYY-MM-DD
    tipo: str          # "emitidas", "recibidas" o "ambas"
