from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class SatAccount(Base):
    __tablename__ = "sat_accounts"

    id = Column(Integer, primary_key=True, index=True)
    rfc = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)  # Alias/Business name
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SatInvoice(Base):
    __tablename__ = "sat_invoices"

    id = Column(Integer, primary_key=True, index=True)
    account_rfc = Column(String, index=True, nullable=False)  # RFC who owns/downloaded this invoice
    uuid = Column(String, unique=True, index=True, nullable=False)
    emisor_rfc = Column(String, index=True, nullable=False)
    emisor_nombre = Column(String, nullable=True)
    receptor_rfc = Column(String, index=True, nullable=False)
    receptor_nombre = Column(String, nullable=True)
    fecha_emision = Column(DateTime(timezone=True), nullable=False)
    tipo_comprobante = Column(String, nullable=True)  # I (Ingreso), E (Egreso), T (Traslado), P (Pago), N (Nómina)
    subtotal = Column(Float, nullable=True, default=0.0)
    total = Column(Float, nullable=True, default=0.0)
    iva_trasladado = Column(Float, nullable=True, default=0.0)
    iva_retenido = Column(Float, nullable=True, default=0.0)
    isr_retenido = Column(Float, nullable=True, default=0.0)
    tipo_cfdi = Column(String, nullable=False)  # "emitida" or "recibida"
    conceptos_resumen = Column(String, nullable=True)  # Simple text description summary
    xml_content = Column(Text, nullable=True)  # Full raw XML text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SatDownloadRequest(Base):
    __tablename__ = "sat_download_requests"

    id = Column(Integer, primary_key=True, index=True)
    account_rfc = Column(String, index=True, nullable=False)
    id_solicitud = Column(String, unique=True, index=True, nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_fin = Column(DateTime(timezone=True), nullable=False)
    tipo_cfdi = Column(String, nullable=False)  # "emitidas" or "recibidas"
    status = Column(String, default="pendiente")  # pendiente, terminada, descargada, error, rechazada
    intentos = Column(Integer, default=0)
    mensaje_error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
