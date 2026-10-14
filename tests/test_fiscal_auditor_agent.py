import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from app.models.reconciliation import BankTransaction, CFDIInvoice
from app.services.reconciliation.fiscal_auditor_agent import audit_month_fiscal_health

# SQLite en memoria con StaticPool para tests aislados
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

mock_admin = UserSchema(
    id=1,
    email="hola@hipha.mx",
    is_active=True,
    is_superuser=True,
    full_name="Administrador Hipha"
)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def test_audit_month_fiscal_health_heuristic(db_session):
    # Crear transacciones de prueba para septiembre 2026
    tx1 = BankTransaction(
        id_transaccion="TX-HASH-001",
        account_rfc="DEGF851127TK1",
        fecha=datetime(2026, 9, 5, 10, 0, 0),
        periodo_mes="2026-09",
        concepto="ABONO CLIENTE DISEÑO WEB",
        monto=11600.0,
        tipo="INGRESO",
        banco="BBVA",
        status_conciliacion="CONCILIADO",
        uuid_cfdi="UUID-ING-001"
    )
    tx2 = BankTransaction(
        id_transaccion="TX-HASH-002",
        account_rfc="DEGF851127TK1",
        fecha=datetime(2026, 9, 10, 11, 0, 0),
        periodo_mes="2026-09",
        concepto="COMPRA HARDWARE LAPTOP",
        monto=5800.0,
        tipo="EGRESO",
        banco="BBVA",
        status_conciliacion="CONCILIADO",
        uuid_cfdi="UUID-EGR-001"
    )
    tx3 = BankTransaction(
        id_transaccion="TX-HASH-003",
        account_rfc="DEGF851127TK1",
        fecha=datetime(2026, 9, 15, 12, 0, 0),
        periodo_mes="2026-09",
        concepto="COMISION BBVA RETIRO",
        monto=350.0,
        tipo="EGRESO",
        banco="BBVA",
        status_conciliacion="SIN_CFDI"
    )
    db_session.add_all([tx1, tx2, tx3])

    # Crear CFDIs asociados
    inv1 = CFDIInvoice(
        uuid="UUID-ING-001",
        account_rfc="DEGF851127TK1",
        rfc_emisor="DEGF851127TK1",
        rfc_receptor="CLIENTE123456",
        fecha_emision=datetime(2026, 9, 5, 10, 0, 0),
        total=11600.0,
        subtotal=10000.0,
        iva_trasladado=1600.0,
        tipo="INGRESO",
        conciliado=True
    )
    inv2 = CFDIInvoice(
        uuid="UUID-EGR-001",
        account_rfc="DEGF851127TK1",
        rfc_emisor="PROV999999",
        rfc_receptor="DEGF851127TK1",
        fecha_emision=datetime(2026, 9, 10, 11, 0, 0),
        total=5800.0,
        subtotal=5000.0,
        iva_trasladado=800.0,
        tipo="EGRESO",
        conciliado=True
    )
    db_session.add_all([inv1, inv2])
    db_session.commit()

    # Ejecutar auditoría fiscal (modo heurístico sin API key)
    audit = audit_month_fiscal_health(
        db=db_session,
        account_rfc="DEGF851127TK1",
        month="2026-09",
        use_ai=False
    )

    assert audit["month"] == "2026-09"
    assert audit["is_mes_completo"] is False
    assert audit["health_level"] in ("POR_REVISAR", "ALERTA_FISCAL")
    assert audit["kpis"]["count_sin_cfdi"] == 1
    assert audit["kpis"]["monto_sin_cfdi"] == 350.0
    assert audit["kpis"]["iva_trasladado"] == 1600.0
    assert audit["kpis"]["iva_acreditable"] == 800.0
    assert audit["kpis"]["balance_iva_estimado"] == 800.0  # 1600 - 800
    assert len(audit["recommendations"]) > 0
    assert "Diagnóstico Fiscal" in audit["agent_summary"]
    assert len(audit["top_pendientes"]) == 1
    assert audit["top_pendientes"][0]["monto"] == 350.0


def test_audit_month_fiscal_health_mes_completo(db_session):
    # Mes con todo conciliado o justificado
    tx1 = BankTransaction(
        id_transaccion="TX-HASH-COMPLETO-001",
        account_rfc="DEGF851127TK1",
        fecha=datetime(2026, 8, 1, 10, 0, 0),
        periodo_mes="2026-08",
        concepto="RETIRO GASTO PERSONAL",
        monto=1500.0,
        tipo="EGRESO",
        banco="BBVA",
        status_conciliacion="NO_APLICA",
        nota_revision="Gasto Personal / No Deducible"
    )
    db_session.add(tx1)
    db_session.commit()

    audit = audit_month_fiscal_health(
        db=db_session,
        account_rfc="DEGF851127TK1",
        month="2026-08",
        use_ai=False
    )

    assert audit["is_mes_completo"] is True
    assert audit["score"] == 100
    assert audit["health_level"] == "MES_COMPLETO"
    assert "Cierre Fiscal Impecable" in audit["agent_summary"]


def test_api_fiscal_agent_endpoints(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin
    client = TestClient(app)

    # 1. GET /agent-diagnosis
    res_get = client.get("/api/dashboard/reconciliation/agent-diagnosis?month=2026-09&account_rfc=DEGF851127TK1&use_ai=false")
    assert res_get.status_code == 200
    data_get = res_get.json()
    assert "agent_summary" in data_get
    assert "health_level" in data_get
    assert "kpis" in data_get

    # 2. POST /agent-audit
    res_post = client.post("/api/dashboard/reconciliation/agent-audit", json={
        "month": "2026-09",
        "account_rfc": "DEGF851127TK1",
        "use_ai": False
    })
    assert res_post.status_code == 200
    data_post = res_post.json()
    assert data_post["month"] == "2026-09"
    assert "score" in data_post

    app.dependency_overrides.clear()
