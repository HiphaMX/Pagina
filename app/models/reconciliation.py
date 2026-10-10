from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class CFDIInvoice(Base):
    __tablename__ = "cfdi_invoices"

    uuid = Column(String(36), primary_key=True, index=True)
    account_rfc = Column(String(20), nullable=False, default="DEGF851127TK1", index=True)
    area_proyecto = Column(String(100), nullable=True)
    tipo = Column(String(20), nullable=False, index=True)  # INGRESO o EGRESO
    rfc_emisor = Column(String(20), nullable=False, index=True)
    nombre_emisor = Column(String(255), nullable=True)
    rfc_receptor = Column(String(20), nullable=False, index=True)
    nombre_receptor = Column(String(255), nullable=True)
    fecha_emision = Column(DateTime, nullable=False, index=True)
    subtotal = Column(Float, nullable=False, default=0.0)
    iva_trasladado = Column(Float, nullable=False, default=0.0)
    retencion_isr = Column(Float, nullable=False, default=0.0)
    retencion_iva = Column(Float, nullable=False, default=0.0)
    retenciones = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0, index=True)
    metodo_pago = Column(String(10), nullable=True)  # PUE / PPD
    forma_pago = Column(String(50), nullable=True)  # 01, 03, 04, etc.
    conceptos_resumen = Column(Text, nullable=True)
    conciliado = Column(Boolean, default=False, index=True)
    fuente = Column(String(50), default="DASHBOARD")  # EMAIL, DASHBOARD, HISTORICO, SAT
    xml_raw = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación inversa a transacciones bancarias
    transacciones = relationship("BankTransaction", back_populates="factura")


class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_rfc = Column(String(20), nullable=False, default="DEGF851127TK1", index=True)
    area_proyecto = Column(String(100), nullable=True)
    tipo_categoria = Column(String(50), nullable=True)
    id_transaccion = Column(String(64), unique=True, index=True, nullable=False)  # Hash SHA-256
    banco = Column(String(50), default="BBVA")
    fecha = Column(DateTime, nullable=False, index=True)
    concepto = Column(Text, nullable=False)
    monto = Column(Float, nullable=False, index=True)
    tipo = Column(String(20), nullable=False, index=True)  # INGRESO (abono) o EGRESO (cargo)
    saldo = Column(Float, nullable=True)
    uuid_cfdi = Column(String(36), ForeignKey("cfdi_invoices.uuid", ondelete="SET NULL"), nullable=True, index=True)
    status_conciliacion = Column(String(20), default="SIN_CFDI", index=True)  # CONCILIADO, POR_REVISAR, SIN_CFDI
    confianza_score = Column(Float, default=0.0)
    nota_revision = Column(Text, nullable=True)
    periodo_mes = Column(String(7), nullable=False, index=True)  # YYYY-MM
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con la factura CFDI
    factura = relationship("CFDIInvoice", back_populates="transacciones")
