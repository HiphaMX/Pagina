import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from app.core.database import SessionLocal, Base, engine
from app.models.reconciliation import CFDIInvoice, BankTransaction
from app.services.reconciliation.cfdi_parser import parse_cfdi_xml
from app.services.reconciliation.bbva_parser import parse_bbva_statement
from app.services.reconciliation.matching_engine import conciliar_movimientos
from app.services.reconciliation.excel_exporter import export_reconciliation_excel
from app.services.reconciliation.pdf_reporter import generate_discrepancies_pdf
from app.services.reconciliation.backfill import import_historical_excel

client = TestClient(app)

mock_admin = UserSchema(
    id=1,
    email="hola@hipha.mx",
    is_active=True,
    is_superuser=True,
    full_name="Administrador Hipha"
)

SAMPLE_CFDI_XML = b"""<?xml version="1.0" encoding="utf-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
    Fecha="2026-05-10T12:00:00" Total="1160.00" SubTotal="1000.00" MetodoPago="PUE" FormaPago="03" TipoDeComprobante="I">
    <cfdi:Emisor Rfc="PROV123456ABC" Nombre="PROVEEDORA DIGITAL SA DE CV" />
    <cfdi:Receptor Rfc="HMA1803098A3" Nombre="HIPHA MARKETING DIGITAL" />
    <cfdi:Conceptos>
        <cfdi:Concepto ClaveProdServ="81111500" Cantidad="1" Descripcion="Licencia Cloud Hosting" Importe="1000.00" />
    </cfdi:Conceptos>
    <cfdi:Impuestos TotalImpuestosTrasladados="160.00">
        <cfdi:Traslados>
            <cfdi:Traslado Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="160.00" />
        </cfdi:Traslados>
    </cfdi:Impuestos>
    <cfdi:Complemento>
        <tfd:TimbreFiscalDigital UUID="AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE" FechaTimbrado="2026-05-10T12:05:00" />
    </cfdi:Complemento>
</cfdi:Comprobante>
"""

SAMPLE_BBVA_CSV = b"""Fecha,Concepto,Cargo,Abono,Saldo
12/05/2026,SPEI PAGO PROVEEDORA DIGITAL REF 49201,1160.00,,45000.00
14/05/2026,COMISION POR TRANSFERENCIA INTERBANCARIA,5.80,,44994.20
15/05/2026,DEPOSITO EN EFECTIVO,,5000.00,49994.20
"""

@pytest.fixture(autouse=True)
def setup_db_and_auth():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin
    yield
    app.dependency_overrides.pop(get_current_active_user, None)


def test_cfdi_parser():
    # Probar como EGRESO (Receptor es Hipha)
    parsed = parse_cfdi_xml(SAMPLE_CFDI_XML, mi_rfc="HMA1803098A3")
    assert parsed["uuid"] == "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
    assert parsed["tipo"] == "EGRESO"
    assert parsed["total"] == 1160.00
    assert parsed["subtotal"] == 1000.00
    assert parsed["iva_trasladado"] == 160.00
    assert parsed["rfc_emisor"] == "PROV123456ABC"
    assert "PROVEEDORA DIGITAL" in parsed["nombre_emisor"]

    # Probar como INGRESO si el emisor fuera Hipha
    parsed_ingreso = parse_cfdi_xml(SAMPLE_CFDI_XML, mi_rfc="PROV123456ABC")
    assert parsed_ingreso["tipo"] == "INGRESO"


def test_bbva_parser():
    txs = parse_bbva_statement(SAMPLE_BBVA_CSV, "movimientos_mayo.csv")
    assert len(txs) == 3

    # Primera tx: Cargo 1160
    assert txs[0]["monto"] == 1160.00
    assert txs[0]["tipo"] == "EGRESO"
    assert "PROVEEDORA DIGITAL" in txs[0]["concepto"]
    assert txs[0]["periodo_mes"] == "2026-05"
    assert len(txs[0]["id_transaccion"]) == 64  # SHA-256

    # Segunda tx: Comisión 5.80
    assert txs[1]["monto"] == 5.80
    assert txs[1]["tipo"] == "EGRESO"

    # Tercera tx: Abono 5000
    assert txs[2]["monto"] == 5000.00
    assert txs[2]["tipo"] == "INGRESO"


def test_bbva_parser_spanish_months_and_agosto():
    bbva_agosto_csv = b"""Fecha,Concepto / Referencia,Cargo,Abono,Saldo
01/AGO/2026,PAGO PROVEEDOR SERVICIOS CLOUD,2500.00,,42500.00
15-AGO-26,DEPOSITO CLIENTE HONORARIOS,,15000.00,57500.00
28/Ago/2026,COMISION MANEJO DE CUENTA,150.00,,57350.00
"""
    txs = parse_bbva_statement(bbva_agosto_csv, "movimientos_agosto.csv")
    assert len(txs) == 3

    assert txs[0]["periodo_mes"] == "2026-08"
    assert txs[0]["monto"] == 2500.00
    assert txs[0]["tipo"] == "EGRESO"

    assert txs[1]["periodo_mes"] == "2026-08"
    assert txs[1]["monto"] == 15000.00
    assert txs[1]["tipo"] == "INGRESO"

    assert txs[2]["periodo_mes"] == "2026-08"
    assert txs[2]["monto"] == 150.00
    assert txs[2]["tipo"] == "EGRESO"


def test_bbva_parser_semicolon_and_preamble():
    bbva_semi_csv = """BBVA Bancomer S.A.
Cuenta: 0123456789
Periodo consultado: 01/08/2026 al 31/08/2026

Fecha de operacion;Concepto;Retiro;Deposito;Saldo
05/08/2026;COMPRA SUPERMERCADO;(1.250,50);;38749,50
10/08/2026;TRANSFERENCIA SPEI ENTRADA;;5.000,00;43749,50
TOTAL DE MOVIMIENTOS: 2
""".encode("latin-1")

    txs = parse_bbva_statement(bbva_semi_csv, "bbva_export_netcash.csv")
    assert len(txs) == 2

    # Retiro con parentesis y formato decimal europeo
    assert txs[0]["monto"] == 1250.50
    assert txs[0]["tipo"] == "EGRESO"
    assert txs[0]["periodo_mes"] == "2026-08"

    # Deposito
    assert txs[1]["monto"] == 5000.00
    assert txs[1]["tipo"] == "INGRESO"
    assert txs[1]["periodo_mes"] == "2026-08"


def test_matching_engine():
    parsed_cfdi = parse_cfdi_xml(SAMPLE_CFDI_XML, mi_rfc="HMA1803098A3")
    txs = parse_bbva_statement(SAMPLE_BBVA_CSV, "movimientos_mayo.csv")

    facturas_pool = [parsed_cfdi]
    reconciled = conciliar_movimientos(txs, facturas_pool)

    assert len(reconciled) == 3

    # El cargo de 1160 debe ser Nivel 1 (CONCILIADO 100%) porque el monto coincide (1160),
    # fecha está en ventana (10 a 12 mayo = +2 días) y el nombre 'PROVEEDORA DIGITAL' está en el concepto bancario.
    tx_1160 = next(t for t in reconciled if t["monto"] == 1160.00)
    assert tx_1160["status_conciliacion"] in ("CONCILIADO", "CONCILIADO_POR_REGLA")
    assert tx_1160["uuid_cfdi"] == "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
    assert tx_1160["confianza_score"] in (0.95, 1.0)

    # La comisión de 5.80 debe ser SIN_CFDI
    tx_comision = next(t for t in reconciled if t["monto"] == 5.80)
    assert tx_comision["status_conciliacion"] == "SIN_CFDI"
    assert "comisión" in tx_comision["nota_revision"].lower() or "bancario" in tx_comision["nota_revision"].lower()


def test_exporters():
    txs = parse_bbva_statement(SAMPLE_BBVA_CSV, "movimientos_mayo.csv")
    parsed_cfdi = parse_cfdi_xml(SAMPLE_CFDI_XML, mi_rfc="HMA1803098A3")
    reconciled = conciliar_movimientos(txs, [parsed_cfdi])

    # Excel
    xlsx_bytes = export_reconciliation_excel(reconciled, mes_label="2026-05")
    assert len(xlsx_bytes) > 1000

    # PDF Faltantes
    pdf_bytes = generate_discrepancies_pdf(reconciled, mes_label="2026-05")
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


def test_api_reconciliation_endpoints():
    # 1. Overview
    res = client.get("/api/dashboard/reconciliation/overview?account_rfc=DEGF851127TK1")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "selected_month" in data
    assert data["entity_name"] == "HIPHA"

    k = data["kpis"]
    assert "subtotal_ingresos_facturados" in k
    assert "iva_trasladado_ingresos" in k
    assert "total_ingresos_facturados" in k
    assert "count_ingresos_facturados" in k
    assert "subtotal_egresos_comprobados" in k
    assert "iva_acreditable_egresos" in k
    assert "total_egresos_comprobados" in k
    assert "count_egresos_comprobados" in k
    assert "balance_iva_estimado" in k
    assert "total_xml_mes" in k
    assert "count_xml_ingresos" in k
    assert "count_xml_egresos" in k
    assert "has_bank_statement" in k
    assert "count_bank_statement_txs" in k

    # AMDI Overview
    res_amdi = client.get("/api/dashboard/reconciliation/overview?account_rfc=MEHA850118Q96")
    assert res_amdi.status_code == 200
    assert res_amdi.json()["entity_name"] == "AMDI"

    # 2. Transactions
    res_tx = client.get("/api/dashboard/reconciliation/transactions?account_rfc=DEGF851127TK1")
    assert res_tx.status_code == 200
    assert isinstance(res_tx.json(), list)

    # 3. Pending invoices
    res_inv = client.get("/api/dashboard/reconciliation/pending-invoices?account_rfc=DEGF851127TK1")
    assert res_inv.status_code == 200
    assert isinstance(res_inv.json(), list)


def test_tax_kpis_calculation_and_balance():
    db = SessionLocal()
    uuid_ing = "CFDI-TEST-TAX-ING-001"
    uuid_egr = "CFDI-TEST-TAX-EGR-002"
    month_test = "2026-11"
    try:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_([uuid_ing, uuid_egr])).delete()
        db.commit()

        # 1. Factura de Ingreso emitida
        cfdi_ing = CFDIInvoice(
            uuid=uuid_ing,
            account_rfc="DEGF851127TK1",
            tipo="INGRESO",
            rfc_emisor="DEGF851127TK1",
            nombre_emisor="FRANCISCO DE JESUS DELGADILLO GARCIA",
            rfc_receptor="CLI999999XYZ",
            nombre_receptor="CLIENTE TEST IVA SA",
            fecha_emision=datetime(2026, 11, 10, 10, 0),
            subtotal=10000.00,
            iva_trasladado=1600.00,
            retenciones=0.0,
            total=11600.00,
            metodo_pago="PUE",
            conciliado=False,
            comprobado=False,
            area_proyecto="HIPHA"
        )

        # 2. Factura de Egreso comprobada vía TC externa
        cfdi_egr = CFDIInvoice(
            uuid=uuid_egr,
            account_rfc="DEGF851127TK1",
            tipo="EGRESO",
            rfc_emisor="PROV888888XYZ",
            nombre_emisor="PROVEEDOR COMPROBADO TC",
            rfc_receptor="DEGF851127TK1",
            nombre_receptor="FRANCISCO DE JESUS DELGADILLO GARCIA",
            fecha_emision=datetime(2026, 11, 15, 14, 0),
            subtotal=5000.00,
            iva_trasladado=800.00,
            retenciones=0.0,
            total=5800.00,
            metodo_pago="PUE",
            conciliado=False,
            comprobado=True,
            motivo_comprobacion="TC Mercado Libre",
            area_proyecto="HIPHA"
        )

        db.add(cfdi_ing)
        db.add(cfdi_egr)
        db.commit()

        # 3. Consultar overview para el mes mientras la factura de ingreso está pendiente de pago (NO cobrada)
        res_unpaid = client.get(f"/api/dashboard/reconciliation/overview?month={month_test}&account_rfc=DEGF851127TK1")
        assert res_unpaid.status_code == 200
        kpis_unpaid = res_unpaid.json()["kpis"]
        # Al no estar cobrada en banco, NO genera IVA Trasladado en el mes (LIVA Art. 1-B)
        assert kpis_unpaid["subtotal_ingresos_facturados"] == 0.00
        assert kpis_unpaid["iva_trasladado_ingresos"] == 0.00
        assert kpis_unpaid["count_ingresos_facturados"] == 0
        assert kpis_unpaid["iva_acreditable_egresos"] == 800.00
        # Balance a favor de egresos comprobados (-800.00)
        assert kpis_unpaid["balance_iva_estimado"] == -800.00

        # 4. Ahora simular que se realiza la operación bancaria y se concilia la factura de ingreso
        cfdi_ing.conciliado = True
        db.commit()

        res_paid = client.get(f"/api/dashboard/reconciliation/overview?month={month_test}&account_rfc=DEGF851127TK1")
        assert res_paid.status_code == 200
        kpis = res_paid.json()["kpis"]

        assert kpis["subtotal_ingresos_facturados"] == 10000.00
        assert kpis["iva_trasladado_ingresos"] == 1600.00
        assert kpis["total_ingresos_facturados"] == 11600.00
        assert kpis["count_ingresos_facturados"] == 1

        assert kpis["subtotal_egresos_comprobados"] == 5000.00
        assert kpis["iva_acreditable_egresos"] == 800.00
        assert kpis["total_egresos_comprobados"] == 5800.00
        assert kpis["count_egresos_comprobados"] == 1

        # Balance = 1600 - 800 = 800
        assert kpis["balance_iva_estimado"] == 800.00

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_([uuid_ing, uuid_egr])).delete()
        db.commit()
        db.close()


def test_multi_entity_isolation():
    db = SessionLocal()
    try:
        # Create one transaction for HIPHA and one for AMDI
        tx_hipha = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion="tx_test_hipha_001",
            fecha=datetime(2026, 5, 20),
            periodo_mes="2026-05",
            concepto="PAGO SERVICIO HIPHA DOMINIO",
            monto=500.0,
            tipo="EGRESO",
            saldo=10000.0,
            status_conciliacion="SIN_CFDI",
            area_proyecto="HIPHA"
        )
        tx_amdi = BankTransaction(
            account_rfc="MEHA850118Q96",
            id_transaccion="tx_test_amdi_001",
            fecha=datetime(2026, 5, 21),
            periodo_mes="2026-05",
            concepto="COMPRA INSUMOS AMDI FABRICA",
            monto=1200.0,
            tipo="EGRESO",
            saldo=25000.0,
            status_conciliacion="SIN_CFDI",
            area_proyecto="AMDI"
        )
        db.add(tx_hipha)
        db.add(tx_amdi)
        db.commit()

        # Query HIPHA transactions
        res_h = client.get("/api/dashboard/reconciliation/transactions?account_rfc=DEGF851127TK1&month=2026-05")
        assert res_h.status_code == 200
        txs_h = res_h.json()
        assert any(t["id_transaccion"] == "tx_test_hipha_001" for t in txs_h)
        assert not any(t["id_transaccion"] == "tx_test_amdi_001" for t in txs_h)

        # Query AMDI transactions
        res_a = client.get("/api/dashboard/reconciliation/transactions?account_rfc=MEHA850118Q96&month=2026-05")
        assert res_a.status_code == 200
        txs_a = res_a.json()
        assert any(t["id_transaccion"] == "tx_test_amdi_001" for t in txs_a)
        assert not any(t["id_transaccion"] == "tx_test_hipha_001" for t in txs_a)

    finally:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(["tx_test_hipha_001", "tx_test_amdi_001"])).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_14_column_excel_export_structure():
    import io
    import openpyxl

    sample_txs = [
        {
            "fecha": "2026-05-15",
            "area_proyecto": "AMDI Producción",
            "uuid_cfdi": "11111111-2222-3333-4444-555555555555",
            "contraparte": "ACEROS DE MEXICO SA",
            "concepto": "PAGO LAMINA GALVANIZADA",
            "metodo_pago": "PUE",
            "monto": 1160.0,
            "tipo": "EGRESO",
            "status_conciliacion": "CONCILIADO",
            "subtotal": 1000.0,
            "iva_egresos": 160.0,
            "retencion_isr": 12.5,
            "tipo_categoria": "GASTO"
        }
    ]

    xlsx_bytes = export_reconciliation_excel(sample_txs, mes_label="2026-05", account_rfc="MEHA850118Q96")
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
    ws = wb.active

    # Check Title
    assert "AMDI" in ws["A1"].value

    # Check 14 Headers on row 3
    expected_headers = [
        "FECHA",
        "ÁREA / PROYECTO",
        "FOLIO FISCAL",
        "CLIENTE / PROVEEDOR",
        "CONCEPTO",
        "MÉTODO DE PAGO",
        "INGRESOS",
        "EGRESOS",
        "CFDI",
        "TIPO",
        "SUBTOTAL",
        "IVA INGRESOS",
        "RETENCIÓN ISR",
        "IVA EGRESOS"
    ]

    actual_headers = [ws.cell(row=3, column=c).value for c in range(1, 15)]
    assert actual_headers == expected_headers

    # Check Data on row 4
    assert ws.cell(row=4, column=1).value == "2026-05-15"
    assert ws.cell(row=4, column=2).value == "AMDI Producción"
    assert ws.cell(row=4, column=3).value == "11111111-2222-3333-4444-555555555555"
    assert ws.cell(row=4, column=4).value == "ACEROS DE MEXICO SA"
    assert ws.cell(row=4, column=8).value == 1160.0  # EGRESOS
    assert ws.cell(row=4, column=11).value == 1000.0 # SUBTOTAL
    assert ws.cell(row=4, column=13).value == 12.5   # RETENCIÓN ISR
    assert ws.cell(row=4, column=14).value == 160.0  # IVA EGRESOS

    # Check Formulas on totals row (row 5)
    assert ws.cell(row=5, column=5).value == "TOTALES"
    assert "=SUM(" in str(ws.cell(row=5, column=7).value)
    assert "=SUM(" in str(ws.cell(row=5, column=8).value)
    assert "=SUM(" in str(ws.cell(row=5, column=11).value)
    assert "=SUM(" in str(ws.cell(row=5, column=13).value)
    assert "=SUM(" in str(ws.cell(row=5, column=14).value)


def test_cfdi_retention_isr_iva_separation():
    xml_with_retentions = b"""<?xml version="1.0" encoding="utf-8"?>
    <cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
        Fecha="2026-05-18T10:00:00" Total="1025.00" SubTotal="1000.00" MetodoPago="PUE" FormaPago="03" TipoDeComprobante="I">
        <cfdi:Emisor Rfc="PROF123456XYZ" Nombre="SERVICIOS PROFESIONALES SC" />
        <cfdi:Receptor Rfc="MEHA850118Q96" Nombre="AMDI DECORACION" />
        <cfdi:Impuestos TotalImpuestosTrasladados="160.00" TotalImpuestosRetenidos="135.00">
            <cfdi:Traslados>
                <cfdi:Traslado Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="160.00" />
            </cfdi:Traslados>
            <cfdi:Retenciones>
                <cfdi:Retencion Impuesto="001" Importe="100.00" />
                <cfdi:Retencion Impuesto="002" Importe="35.00" />
            </cfdi:Retenciones>
        </cfdi:Impuestos>
        <cfdi:Complemento>
            <tfd:TimbreFiscalDigital UUID="99999999-8888-7777-6666-555555555555" />
        </cfdi:Complemento>
    </cfdi:Comprobante>
    """
    parsed = parse_cfdi_xml(xml_with_retentions, mi_rfc="MEHA850118Q96")
    assert parsed["uuid"] == "99999999-8888-7777-6666-555555555555"
    assert parsed["subtotal"] == 1000.0
    assert parsed["iva_trasladado"] == 160.0
    assert parsed["retencion_isr"] == 100.0
    assert parsed["retencion_iva"] == 35.0
    assert parsed["retenciones"] == 135.0


def test_historical_backfill_csv_14_columns():
    db = SessionLocal()
    sample_csv = (
        b"FECHA,\xc1REA / PROYECTO,FOLIO FISCAL,CLIENTE / PROVEEDOR,CONCEPTO,M\xc9TODO DE PAGO,INGRESOS,EGRESOS,CFDI,TIPO,SUBTOTAL,IVA INGRESOS,RETENCI\xd3N ISR,IVA EGRESOS\n"
        b"15/01/2026,HIPHA MKT,12345678-1234-1234-1234-123456789012,CLIENTE ABC,CAMPANA DIGITAL GOOGLE,PUE,11600.00,,I,INGRESO,10000.00,1600.00,0.00,0.00\n"
        b"18/01/2026,HIPHA MKT,,BBVA COMISIONES,COMISION MENSUAL CUENTA,PUE,,232.00,,GASTO,200.00,0.00,0.00,32.00\n"
    )

    try:
        res = import_historical_excel(
            sample_csv,
            "ENero.csv",
            db,
            mi_rfc="DEGF851127TK1",
            account_rfc="DEGF851127TK1"
        )
        assert res["success"] is True
        assert res["imported_transactions"] == 2
        assert res["imported_invoices"] == 1

        # Check that the invoice was registered as CONCILIADO
        inv = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == "12345678-1234-1234-1234-123456789012").first()
        assert inv is not None
        assert inv.conciliado is True
        assert inv.total == 11600.00

        # Check transactions
        txs = db.query(BankTransaction).filter(BankTransaction.account_rfc == "DEGF851127TK1", BankTransaction.periodo_mes == "2026-01").all()
        assert len(txs) == 2
        conciliated_tx = next(t for t in txs if t.uuid_cfdi == "12345678-1234-1234-1234-123456789012")
        assert conciliated_tx.status_conciliacion == "CONCILIADO"
        assert conciliated_tx.monto == 11600.00
    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == "12345678-1234-1234-1234-123456789012").delete()
        db.query(BankTransaction).filter(BankTransaction.account_rfc == "DEGF851127TK1", BankTransaction.periodo_mes == "2026-01").delete()
        db.commit()
        db.close()


def test_delete_transaction():
    db = SessionLocal()
    try:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion == "tx_test_del_001").delete()
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == "TEST-DEL-UUID-001").delete()
        db.commit()

        inv = CFDIInvoice(
            uuid="TEST-DEL-UUID-001",
            account_rfc="DEGF851127TK1",
            tipo="EGRESO",
            rfc_emisor="PROV123",
            rfc_receptor="DEGF851127TK1",
            fecha_emision=datetime(2026, 7, 10),
            total=500.0,
            conciliado=True
        )
        db.add(inv)
        db.commit()

        tx = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion="tx_test_del_001",
            fecha=datetime(2026, 7, 10),
            periodo_mes="2026-07",
            concepto="CARGO DE PRUEBA A ELIMINAR",
            monto=500.0,
            tipo="EGRESO",
            uuid_cfdi="TEST-DEL-UUID-001",
            status_conciliacion="CONCILIADO"
        )
        db.add(tx)
        db.commit()
        tx_id = tx.id

        res = client.delete(f"/api/dashboard/reconciliation/transactions/{tx_id}")
        assert res.status_code == 200
        assert res.json()["success"] is True

        # Verificar que la transacción fue borrada
        deleted = db.query(BankTransaction).filter(BankTransaction.id == tx_id).first()
        assert deleted is None

        # Verificar que la factura quedó liberada
        inv_updated = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == "TEST-DEL-UUID-001").first()
        assert inv_updated is not None
        assert inv_updated.conciliado is False
    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == "TEST-DEL-UUID-001").delete()
        db.commit()
        db.close()


def test_deduplicate_transactions():
    db = SessionLocal()
    try:
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.periodo_mes == "2026-07",
            BankTransaction.monto == 22605.75
        ).delete()
        db.commit()

        tx1 = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion="tx_dup_001",
            fecha=datetime(2026, 7, 22),
            periodo_mes="2026-07",
            concepto="ABONO",
            monto=22605.75,
            tipo="INGRESO",
            area_proyecto="DAM",
            status_conciliacion="SIN_CFDI"
        )
        tx2 = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion="tx_dup_002",
            fecha=datetime(2026, 7, 22),
            periodo_mes="2026-07",
            concepto="ABONO",
            monto=22605.75,
            tipo="INGRESO",
            area_proyecto="DAM",
            status_conciliacion="SIN_CFDI"
        )
        db.add(tx1)
        db.add(tx2)
        db.commit()

        # Debe haber 2 duplicados antes
        dups_before = db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.periodo_mes == "2026-07",
            BankTransaction.monto == 22605.75
        ).all()
        assert len(dups_before) == 2

        res = client.post("/api/dashboard/reconciliation/deduplicate?account_rfc=DEGF851127TK1&month=2026-07")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["deleted_count"] >= 1

        # Debe quedar solo 1
        dups_after = db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.periodo_mes == "2026-07",
            BankTransaction.monto == 22605.75
        ).all()
        assert len(dups_after) == 1
    finally:
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.periodo_mes == "2026-07",
            BankTransaction.monto == 22605.75
        ).delete()
        db.commit()
        db.close()


def test_cron_sync_mailbox(monkeypatch):
    calls = []

    def mock_sync(db, account_rfc, lookback_days=60):
        calls.append((account_rfc, lookback_days))
        return {
            "success": True,
            "connected": True,
            "message": f"Sincronizado {account_rfc}",
            "processed_xmls": 1,
            "processed_statements": 0
        }

    monkeypatch.setattr("app.api.dashboard.reconciliation_routes.sync_mailbox_invoices", mock_sync)

    res = client.get("/api/dashboard/reconciliation/cron-sync")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "hipha" in data
    assert "amdi" in data
    assert len(calls) == 2
    assert calls[0][0] == "DEGF851127TK1"
    assert calls[1][0] == "MEHA850118Q96"


def test_backfill_agosto_declared_month_and_concept_synthesis():
    with open("tests/fixtures/agosto.csv", "rb") as f:
        content = f.read()

    db = SessionLocal()
    try:
        res = import_historical_excel(content, "agosto.csv", db, mi_rfc="DEGF851127TK1")
        assert res["success"] is True
        assert res["imported_transactions"] == 3
        assert res["transacciones_importadas"] == 3
        assert "2026-07" in res["meses_afectados"]

        txs = db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.periodo_mes == "2026-07"
        ).all()
        assert len(txs) >= 3

        # Conceptos no deben estar vacíos
        for t in txs:
            assert t.concepto and len(t.concepto) > 3
            assert t.periodo_mes == "2026-07"

        # Verificar montos de las 3 transacciones importadas
        montos_subset = sorted([float(t.monto) for t in txs if float(t.monto) in [383.88, 4361.60, 22605.75]])
        assert 383.88 in montos_subset
        assert 4361.60 in montos_subset
        assert 22605.75 in montos_subset

        # Verificar endpoint de upload con archivo agosto.csv
        files = [("files", ("agosto.csv", content, "text/csv"))]
        upload_res = client.post("/api/dashboard/reconciliation/upload-files", files=files, data={"account_rfc": "DEGF851127TK1"})
        assert upload_res.status_code == 200
        data_up = upload_res.json()
        assert data_up["success"] is True
        assert data_up["processed_statements"] == 3
        assert "2026-07" in data_up["detected_months"]
    finally:
        db.close()


def test_parse_bank_pdf_statement_bbva_comprobante():
    from app.services.reconciliation.pdf_parser import parse_bank_pdf_statement

    with open("tests/fixtures/BBVA.pdf", "rb") as f:
        pdf_bytes = f.read()

    txs = parse_bank_pdf_statement(pdf_bytes, "BBVA.pdf", account_rfc="MEHA850118Q96")
    assert len(txs) == 1
    t = txs[0]
    assert t["monto"] == 2000.00
    assert t["tipo"] == "EGRESO"
    assert t["periodo_mes"] == "2026-10"
    assert "JAIME OMAR RODRIGUEZ ALCALA" in t["concepto"]
    assert "DESINSTALACION LETRERO DAM" in t["concepto"]
    assert t["area_proyecto"] == "DAM"
    assert t["referencia_rastreo"] == "BNET01002610090025425885"


def test_upload_bank_pdf_statement_endpoint():
    with open("tests/fixtures/BBVA.pdf", "rb") as f:
        pdf_bytes = f.read()

    db = SessionLocal()
    try:
        files = [("files", ("BBVA.pdf", pdf_bytes, "application/pdf"))]
        upload_res = client.post(
            "/api/dashboard/reconciliation/upload-files",
            files=files,
            data={"account_rfc": "MEHA850118Q96"}
        )
        assert upload_res.status_code == 200
        data_up = upload_res.json()
        assert data_up["success"] is True
        assert data_up["processed_statements"] >= 1
        assert "2026-10" in data_up["detected_months"]

        tx = db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "MEHA850118Q96",
            BankTransaction.periodo_mes == "2026-10",
            BankTransaction.monto == 2000.00
        ).first()
        assert tx is not None
        assert tx.tipo == "EGRESO"
        assert tx.area_proyecto == "DAM"
        assert "JAIME OMAR RODRIGUEZ ALCALA" in tx.concepto
    finally:
        db.close()


def test_parse_bank_pdf_statement_bbva_pyme_julio():
    from app.services.reconciliation.pdf_parser import parse_bank_pdf_statement

    with open("tests/fixtures/Julio_FDG.pdf", "rb") as f:
        pdf_bytes = f.read()

    txs = parse_bank_pdf_statement(pdf_bytes, "Julio FDG.pdf", account_rfc="DEGF851127TK1")
    assert len(txs) == 5

    # Validar periodos y RFC
    for t in txs:
        assert t["periodo_mes"] == "2026-07"
        assert t["account_rfc"] == "DEGF851127TK1"
        assert t["banco"] == "BBVA"

    ingresos = [t for t in txs if t["tipo"] == "INGRESO"]
    egresos = [t for t in txs if t["tipo"] == "EGRESO"]

    assert len(ingresos) == 2
    assert len(egresos) == 3

    assert sum(t["monto"] for t in ingresos) == pytest.approx(26967.35, 0.01)
    assert sum(t["monto"] for t in egresos) == pytest.approx(26967.35, 0.01)

    # Validar detección de proyectos (ej. Axis -> HEALTHYICE)
    axis_tx = next(t for t in ingresos if "Axis" in t["concepto"])
    assert axis_tx["area_proyecto"] == "HEALTHYICE"
    assert axis_tx["monto"] == 4361.60


def test_upload_bank_pdf_julio_endpoint():
    with open("tests/fixtures/Julio_FDG.pdf", "rb") as f:
        pdf_bytes = f.read()

    db = SessionLocal()
    try:
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.periodo_mes == "2026-07"
        ).delete()
        db.commit()

        files = [("files", ("Julio FDG.pdf", pdf_bytes, "application/pdf"))]
        upload_res = client.post(
            "/api/dashboard/reconciliation/upload-files",
            files=files,
            data={"account_rfc": "DEGF851127TK1"}
        )
        assert upload_res.status_code == 200
        data_up = upload_res.json()
        assert data_up["success"] is True
        assert data_up["processed_statements"] == 5
        assert "2026-07" in data_up["detected_months"]

        txs = db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.periodo_mes == "2026-07"
        ).all()
        assert len(txs) == 5
    finally:
        db.close()


def test_parse_bank_pdf_statement_bbva_pyme_febrero():
    from app.services.reconciliation.pdf_parser import parse_bank_pdf_statement

    with open("tests/fixtures/Febrero_FDG.pdf", "rb") as f:
        pdf_bytes = f.read()

    txs = parse_bank_pdf_statement(pdf_bytes, "Febrero FDG.pdf", account_rfc="DEGF851127TK1")
    assert len(txs) == 7

    for t in txs:
        assert t["periodo_mes"] == "2026-02"
        assert t["account_rfc"] == "DEGF851127TK1"
        assert t["banco"] == "BBVA"

    ingresos = [t for t in txs if t["tipo"] == "INGRESO"]
    egresos = [t for t in txs if t["tipo"] == "EGRESO"]

    # 3 Abonos ($23,945.75) y 4 Cargos ($12,783.91)
    assert len(ingresos) == 3
    assert len(egresos) == 4
    assert sum(t["monto"] for t in ingresos) == pytest.approx(23945.75, 0.01)
    assert sum(t["monto"] for t in egresos) == pytest.approx(12783.91, 0.01)

    # 01/FEB: Cargo $11,433.91 (PAGO CUENTA DE TERCERO - Entre cuentas)
    tx_01_feb = next(t for t in egresos if t["monto"] == 11433.91)
    assert "Entre cuentas" in tx_01_feb["concepto"]
    assert tx_01_feb["status_conciliacion"] == "NO_APLICA"
    assert tx_01_feb["area_proyecto"] == "DELGADILLO MEDINA"

    # 03/FEB: Abono $820.00 (SPEI Mercado Pago - entre cuentas)
    tx_03_feb_ing = next(t for t in ingresos if t["monto"] == 820.00)
    assert tx_03_feb_ing["status_conciliacion"] == "NO_APLICA"
    assert tx_03_feb_ing["nota_revision"] == "Traspaso entre Cuentas Propias"
    assert tx_03_feb_ing["area_proyecto"] == "DELGADILLO MEDINA"

    # 07/FEB: Abono $520.00 (SPEI Mercado Pago - Francisco Delgadillo García)
    tx_07_feb_ing = next(t for t in ingresos if t["monto"] == 520.00)
    assert tx_07_feb_ing["status_conciliacion"] == "NO_APLICA"
    assert tx_07_feb_ing["nota_revision"] == "Traspaso entre Cuentas Propias"

    # 26/FEB: Abono $22,605.75 (DEPOSITO DE TERCERO - PAGO DE DAM BMRCASH)
    tx_26_feb_ing = next(t for t in ingresos if t["monto"] == 22605.75)
    assert "DAM" in tx_26_feb_ing["concepto"]
    assert tx_26_feb_ing["status_conciliacion"] == "SIN_CFDI"


def test_upload_bank_pdf_febrero_endpoint_and_income_exclusion():
    with open("tests/fixtures/Febrero_FDG.pdf", "rb") as f:
        pdf_bytes = f.read()

    db = SessionLocal()
    try:
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.periodo_mes == "2026-02"
        ).delete()
        db.commit()

        # 1. Subir estado de cuenta de Febrero
        files = [("files", ("Febrero FDG.pdf", pdf_bytes, "application/pdf"))]
        upload_res = client.post(
            "/api/dashboard/reconciliation/upload-files",
            files=files,
            data={"account_rfc": "DEGF851127TK1"}
        )
        assert upload_res.status_code == 200
        data_up = upload_res.json()
        assert data_up["success"] is True
        assert data_up["processed_statements"] == 7
        assert "2026-02" in data_up["detected_months"]

        # 2. Consultar Overview de Febrero
        res_ov = client.get("/api/dashboard/reconciliation/overview?month=2026-02&account_rfc=DEGF851127TK1")
        assert res_ov.status_code == 200
        kpis = res_ov.json()["kpis"]

        # Validar que los ingresos comerciales reflejen SOLO $22,605.75 (depósito de DAM)
        # y NO incluyan los traspasos entre cuentas propias de $820.00 y $520.00 ($1,340.00)
        assert kpis["total_ingresos_banco"] == pytest.approx(22605.75, 0.01)
        assert kpis["count_ingresos_banco"] == 1
        assert kpis["total_traspasos_ingresos"] == pytest.approx(1340.00, 0.01)
        assert kpis["count_traspasos_ingresos"] == 2
        assert kpis["total_ingresos_bruto"] == pytest.approx(23945.75, 0.01)

        # Validar egresos operativos ($1,350.00) excluyendo traspaso propio ($11,433.91)
        assert kpis["total_egresos_banco"] == pytest.approx(1350.00, 0.01)
        assert kpis["count_egresos_banco"] == 3
        assert kpis["total_traspasos_egresos"] == pytest.approx(11433.91, 0.01)
        assert kpis["count_traspasos_egresos"] == 1
        assert kpis["total_egresos_bruto"] == pytest.approx(12783.91, 0.01)
    finally:
        db.close()


def test_parse_bank_pdf_statement_mercadopago_credit_card():
    from app.services.reconciliation.pdf_parser import parse_bank_pdf_statement

    with open("tests/fixtures/ML_agosto_2026.pdf", "rb") as f:
        pdf_bytes = f.read()

    txs = parse_bank_pdf_statement(pdf_bytes, "ML_agosto_2026.pdf", account_rfc="DEGF851127TK1")
    assert len(txs) == 6

    # Todas las compras con tarjeta son EGRESOS del periodo 2026-08
    for t in txs:
        assert t["tipo"] == "EGRESO"
        assert t["banco"] == "TC MERCADO PAGO"
        assert t["periodo_mes"] == "2026-08"
        assert t["account_rfc"] == "DEGF851127TK1"

    # La suma de las compras debe ser exactamente el total a pagar del periodo: $4,421.29
    total_compras = sum(t["monto"] for t in txs)
    assert total_compras == pytest.approx(4421.29, 0.01)

    # Validar comercios individuales
    conceptos = [t["concepto"] for t in txs]
    assert any("Google One" in c for c in conceptos)
    assert any("GOOGLE CLOUD" in c for c in conceptos)
    assert any("WALMART" in c for c in conceptos)
    assert any("NEUBOX" in c for c in conceptos)
    assert any("MERCADOLIBRE" in c for c in conceptos)
    assert any("MP ECOMMERCE" in c for c in conceptos)

    # Validar que gastos de terminales MP se asignan a DELGADILLO MEDINA por defecto
    tx_mp = next(t for t in txs if "MP ECOMMERCE" in t["concepto"])
    assert tx_mp["area_proyecto"] == "DELGADILLO MEDINA"
    assert "DELGADILLO MEDINA" in tx_mp["nota_revision"]

    tx_ml = next(t for t in txs if "MERCADOLIBRE" in t["concepto"])
    assert tx_ml["area_proyecto"] == "DELGADILLO MEDINA"
    assert "DELGADILLO MEDINA" in tx_ml["nota_revision"]

    # Compras de proveedores reconocidos no deben asignarse a Delgadillo Medina
    tx_google = next(t for t in txs if "Google One" in t["concepto"])
    assert tx_google["area_proyecto"] != "DELGADILLO MEDINA"

    # Asegurar que saldos anteriores y pagos de la tarjeta no se extraen como transacciones
    assert not any("Saldo al corte" in c for c in conceptos)
    assert not any("Pago del resumen" in c for c in conceptos)


def test_upload_bank_pdf_mercadopago_and_cross_match():
    with open("tests/fixtures/ML_agosto_2026.pdf", "rb") as f:
        pdf_bytes = f.read()

    db = SessionLocal()
    try:
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.periodo_mes == "2026-08"
        ).delete()
        db.query(CFDIInvoice).filter(
            CFDIInvoice.uuid.in_(["CFDI-GCLOUD-TEST-0001", "CFDI-WALMART-TEST-0002"])
        ).delete()
        db.commit()

        # 1. Crear facturas CFDI de gastos para cruzar con las compras de la tarjeta
        cfdi_gcloud = CFDIInvoice(
            uuid="CFDI-GCLOUD-TEST-0001",
            account_rfc="DEGF851127TK1",
            area_proyecto="HIPHA",
            tipo="EGRESO",
            rfc_emisor="GCM150101XYZ",
            nombre_emisor="GOOGLE CLOUD MEXICO S DE RL DE CV",
            rfc_receptor="DEGF851127TK1",
            nombre_receptor="FRANCISCO DE JESUS DELGADILLO GARCIA",
            fecha_emision=datetime(2026, 8, 1, 10, 0),
            subtotal=260.12,
            iva_trasladado=41.62,
            retenciones=0.0,
            total=301.74,
            metodo_pago="PUE",
            conceptos_resumen="Consumo Cloud Hosting GCP",
            conciliado=False,
            comprobado=False
        )
        cfdi_walmart = CFDIInvoice(
            uuid="CFDI-WALMART-TEST-0002",
            account_rfc="DEGF851127TK1",
            area_proyecto="HIPHA",
            tipo="EGRESO",
            rfc_emisor="NWM9709244W4",
            nombre_emisor="NUEVA WAL MART DE MEXICO S DE RL DE CV",
            rfc_receptor="DEGF851127TK1",
            nombre_receptor="FRANCISCO DE JESUS DELGADILLO GARCIA",
            fecha_emision=datetime(2026, 8, 4, 18, 30),
            subtotal=1197.41,
            iva_trasladado=191.59,
            retenciones=0.0,
            total=1389.00,
            metodo_pago="PUE",
            conceptos_resumen="Insumos Oficina Walmart",
            conciliado=False,
            comprobado=False
        )
        db.merge(cfdi_gcloud)
        db.merge(cfdi_walmart)
        db.commit()

        # 2. Subir estado de cuenta de Mercado Pago
        files = [("files", ("ML_agosto_2026.pdf", pdf_bytes, "application/pdf"))]
        upload_res = client.post(
            "/api/dashboard/reconciliation/upload-files",
            files=files,
            data={"account_rfc": "DEGF851127TK1"}
        )
        assert upload_res.status_code == 200
        data_up = upload_res.json()
        assert data_up["success"] is True
        assert data_up["processed_statements"] == 6
        assert "2026-08" in data_up["detected_months"]

        # 3. Validar que las transacciones de Google Cloud y Walmart se conciliaron automáticamente
        tx_gcloud = db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.monto == 301.74
        ).first()
        assert tx_gcloud is not None
        assert tx_gcloud.status_conciliacion in ("CONCILIADO", "CONCILIADO_POR_REGLA")
        assert tx_gcloud.uuid_cfdi == "CFDI-GCLOUD-TEST-0001"
        assert tx_gcloud.banco == "TC MERCADO PAGO"

        tx_walmart = db.query(BankTransaction).filter(
            BankTransaction.account_rfc == "DEGF851127TK1",
            BankTransaction.monto == 1389.00
        ).first()
        assert tx_walmart is not None
        assert tx_walmart.status_conciliacion in ("CONCILIADO", "CONCILIADO_POR_REGLA")
        assert tx_walmart.uuid_cfdi == "CFDI-WALMART-TEST-0002"
    finally:
        db.close()


def test_pending_invoices_month_filter_and_multi_payment():
    db = SessionLocal()
    try:
        uuid_tukipa = "CFDI-TUKIPA-MULTI-PAY-001"
        db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(["tx-tukipa-pago1", "tx-tukipa-pago2"])).delete()
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_tukipa).delete()
        db.commit()

        # 1. Crear factura CFDI emitida (INGRESO) de $3,213.20 en agosto 2026
        cfdi = CFDIInvoice(
            uuid=uuid_tukipa,
            account_rfc="DEGF851127TK1",
            tipo="INGRESO",
            rfc_emisor="DEGF851127TK1",
            nombre_emisor="FRANCISCO DE JESUS DELGADILLO GARCIA",
            rfc_receptor="MEHA870222DY4",
            nombre_receptor="ABEL ALEJANDRO MEDINA HERNANDEZ",
            fecha_emision=datetime(2026, 8, 28, 10, 0),
            subtotal=2770.00,
            iva_trasladado=443.20,
            retenciones=0.0,
            total=3213.20,
            metodo_pago="PPD",
            conceptos_resumen="Diseño gráfico y publicidad",
            conciliado=False
        )
        db.merge(cfdi)

        # 2. Crear dos transacciones bancarias en BBVA
        tx1 = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion="tx-tukipa-pago1",
            banco="BBVA",
            fecha=datetime(2026, 8, 28),
            concepto="PAGO CUENTA DE TERCERO - Tukipa Marqueting",
            monto=2770.00,
            tipo="EGRESO",  # Clasificado inicialmente como EGRESO por BBVA
            status_conciliacion="SIN_CFDI",
            periodo_mes="2026-08"
        )
        tx2 = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion="tx-tukipa-pago2",
            banco="BBVA",
            fecha=datetime(2026, 8, 28),
            concepto="PAGO CUENTA DE TERCERO - iva tukipa marketi",
            monto=443.20,
            tipo="EGRESO",
            status_conciliacion="SIN_CFDI",
            periodo_mes="2026-08"
        )
        db.merge(tx1)
        db.merge(tx2)
        db.commit()

        db_tx1 = db.query(BankTransaction).filter(BankTransaction.id_transaccion == "tx-tukipa-pago1").first()
        db_tx2 = db.query(BankTransaction).filter(BankTransaction.id_transaccion == "tx-tukipa-pago2").first()

        # 3. Probar endpoint /pending-invoices con filtro de mes
        res_aug = client.get("/api/dashboard/reconciliation/pending-invoices?month=2026-08&account_rfc=DEGF851127TK1")
        assert res_aug.status_code == 200
        invs_aug = res_aug.json()
        target = next((i for i in invs_aug if i["uuid"] == uuid_tukipa), None)
        assert target is not None
        assert target["total"] == 3213.20
        assert target["tipo"] == "INGRESO"
        assert target["saldo_pendiente"] == 3213.20

        # Verificar que si se filtra por otro mes (ej. 2026-09), no aparece
        res_sep = client.get("/api/dashboard/reconciliation/pending-invoices?month=2026-09&account_rfc=DEGF851127TK1")
        assert not any(i["uuid"] == uuid_tukipa for i in res_sep.json())

        # 4. Vincular el primer pago ($2,770.00)
        match1 = client.post("/api/dashboard/reconciliation/match-manual", data={
            "transaction_id": db_tx1.id,
            "uuid_cfdi": uuid_tukipa
        })
        assert match1.status_code == 200

        # Validar alineación de flujo: tx1 debe haber cambiado a INGRESO
        db.refresh(db_tx1)
        assert db_tx1.tipo == "INGRESO"
        assert db_tx1.status_conciliacion == "CONCILIADO"
        assert db_tx1.uuid_cfdi == uuid_tukipa

        # 5. Consultar /pending-invoices sin include_reconciled: ya no debe salir porque conciliado=True
        res_norec = client.get("/api/dashboard/reconciliation/pending-invoices?month=2026-08&account_rfc=DEGF851127TK1")
        assert not any(i["uuid"] == uuid_tukipa for i in res_norec.json())

        # Consultar /pending-invoices CON include_reconciled=True: debe salir mostrando el monto vinculado y saldo restante
        res_rec = client.get("/api/dashboard/reconciliation/pending-invoices?month=2026-08&include_reconciled=true&account_rfc=DEGF851127TK1")
        assert res_rec.status_code == 200
        target_rec = next((i for i in res_rec.json() if i["uuid"] == uuid_tukipa), None)
        assert target_rec is not None
        assert target_rec["pagos_vinculados_count"] == 1
        assert target_rec["monto_vinculado"] == 2770.00
        assert target_rec["saldo_pendiente"] == 443.20

        # 6. Vincular el segundo pago ($443.20) a la misma factura
        match2 = client.post("/api/dashboard/reconciliation/match-manual", data={
            "transaction_id": db_tx2.id,
            "uuid_cfdi": uuid_tukipa
        })
        assert match2.status_code == 200

        db.refresh(db_tx2)
        assert db_tx2.tipo == "INGRESO"
        assert db_tx2.status_conciliacion == "CONCILIADO"
        assert db_tx2.uuid_cfdi == uuid_tukipa

        # Verificar saldo pendiente actualizado a 0.0
        res_final = client.get("/api/dashboard/reconciliation/pending-invoices?month=2026-08&include_reconciled=true&account_rfc=DEGF851127TK1")
        target_final = next(i for i in res_final.json() if i["uuid"] == uuid_tukipa)
        assert target_final["pagos_vinculados_count"] == 2
        assert target_final["monto_vinculado"] == 3213.20
        assert target_final["saldo_pendiente"] == 0.0
    finally:
        db.close()


def test_update_transaction_project():
    client = TestClient(app)
    db = SessionLocal()
    try:
        uuid_proj = "CFDI-TEST-PROJECT-UPDATE"
        tx_id = "tx-test-proj-001"
        db.query(BankTransaction).filter(BankTransaction.id_transaccion == tx_id).delete()
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_proj).delete()
        db.commit()

        cfdi = CFDIInvoice(
            uuid=uuid_proj,
            account_rfc="DEGF851127TK1",
            area_proyecto="GENERAL",
            tipo="EGRESO",
            rfc_emisor="PROV990101XYZ",
            nombre_emisor="PROVEEDOR PRUEBA",
            rfc_receptor="DEGF851127TK1",
            nombre_receptor="HIPHA",
            fecha_emision=datetime(2026, 8, 15),
            total=1500.00,
            conciliado=True
        )
        db.add(cfdi)

        tx = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion=tx_id,
            banco="BBVA",
            fecha=datetime(2026, 8, 15),
            concepto="COMPRA MATERIALES PUBLICITARIOS",
            monto=1500.00,
            tipo="EGRESO",
            uuid_cfdi=uuid_proj,
            status_conciliacion="CONCILIADO",
            area_proyecto="GENERAL",
            periodo_mes="2026-08"
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)

        # 1. Actualizar a 'DAM'
        res = client.patch(
            f"/api/dashboard/reconciliation/transactions/{tx.id}/project",
            json={"area_proyecto": "DAM", "update_cfdi": True}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["area_proyecto"] == "DAM"

        # Verificar en base de datos tanto transacción como CFDI
        db.refresh(tx)
        db.refresh(cfdi)
        assert tx.area_proyecto == "DAM"
        assert cfdi.area_proyecto == "DAM"

        # 2. Actualizar solo la transacción sin CFDI
        res2 = client.patch(
            f"/api/dashboard/reconciliation/transactions/{tx.id}/project",
            json={"area_proyecto": "HEALTHYICE", "update_cfdi": False}
        )
        assert res2.status_code == 200
        db.refresh(tx)
        db.refresh(cfdi)
        assert tx.area_proyecto == "HEALTHYICE"
        assert cfdi.area_proyecto == "DAM"
    finally:
        db.close()


def test_update_transaction_status_and_mes_completo():
    client = TestClient(app)
    db = SessionLocal()
    try:
        tx_sat_id = "tx-test-sat-001"
        db.query(BankTransaction).filter(BankTransaction.id_transaccion == tx_sat_id).delete()
        db.commit()

        # 1. Crear egreso representativo de pago SAT sin CFDI
        tx_sat = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion=tx_sat_id,
            banco="BBVA",
            fecha=datetime(2026, 9, 17),
            concepto="PAGO DE IMPUESTOS AL SAT",
            monto=4271.00,
            tipo="EGRESO",
            status_conciliacion="SIN_CFDI",
            periodo_mes="2026-09"
        )
        db.add(tx_sat)
        db.commit()
        db.refresh(tx_sat)

        # Overview antes: count_sin_cfdi >= 1, mes_completo == False
        res_pre = client.get("/api/dashboard/reconciliation/overview?month=2026-09&account_rfc=DEGF851127TK1")
        assert res_pre.status_code == 200
        kpis_pre = res_pre.json()["kpis"]
        assert kpis_pre["count_sin_cfdi"] >= 1
        assert kpis_pre["mes_completo"] is False

        # 2. Marcar como NO_APLICA (Impuestos SAT)
        res_mark = client.patch(
            f"/api/dashboard/reconciliation/transactions/{tx_sat.id}/status",
            json={"status_conciliacion": "NO_APLICA", "motivo": "Impuestos SAT"}
        )
        assert res_mark.status_code == 200
        assert res_mark.json()["status_conciliacion"] == "NO_APLICA"

        # Overview después: count_sin_cfdi debe ser 0 si no hay otros, y count_no_aplica >= 1
        res_post = client.get("/api/dashboard/reconciliation/overview?month=2026-09&account_rfc=DEGF851127TK1")
        kpis_post = res_post.json()["kpis"]
        assert kpis_post["count_no_aplica"] >= 1

        # Si tx_sat era el único en 2026-09, mes_completo pasa a True
        if kpis_post["count_sin_cfdi"] == 0:
            assert kpis_post["mes_completo"] is True

        # 3. Revertir a SIN_CFDI
        res_rev = client.patch(
            f"/api/dashboard/reconciliation/transactions/{tx_sat.id}/status",
            json={"status_conciliacion": "SIN_CFDI"}
        )
        assert res_rev.status_code == 200
        assert res_rev.json()["status_conciliacion"] == "SIN_CFDI"
    finally:
        db.close()


def test_delgadillo_medina_tc_heuristic():
    from app.services.reconciliation.pdf_parser import is_delgadillo_medina_tc_expense

    # 1. Compras en terminales Mercado Pago con TC -> DELGADILLO MEDINA
    assert is_delgadillo_medina_tc_expense("Compra en MP ECOMMERCE 10 de 12", banco="TC MERCADO PAGO") is True
    assert is_delgadillo_medina_tc_expense("Compra en merpago*MERCADOLIBRE 1 de 4", banco="TC MERCADO PAGO") is True
    assert is_delgadillo_medina_tc_expense("MP*RESTAURANTE LOCAL", banco="TC MERCADO PAGO") is True
    assert is_delgadillo_medina_tc_expense("CLIP*FARMACIA DE LA ESQUINA", banco="TC BBVA") is True

    # 2. Compras en comercios no corporativos con TC -> DELGADILLO MEDINA
    assert is_delgadillo_medina_tc_expense("FARMACIA GUADALAJARA SUC 42", banco="TC MERCADO PAGO") is True
    assert is_delgadillo_medina_tc_expense("TIENDA DE ABARROTES DON JUAN", banco="TC MERCADO PAGO") is True

    # 3. Proveedores corporativos reconocidos con TC -> NO es Delgadillo Medina (permanece HIPHA)
    assert is_delgadillo_medina_tc_expense("Compra en Google One", banco="TC MERCADO PAGO") is False
    assert is_delgadillo_medina_tc_expense("PAYU *GOOGLE CLOUD", banco="TC MERCADO PAGO") is False
    assert is_delgadillo_medina_tc_expense("PAYPAL *NEUBOX US$ 23.62", banco="TC MERCADO PAGO") is False
    assert is_delgadillo_medina_tc_expense("WALMART SUPER 1", banco="TC MERCADO PAGO") is False
    assert is_delgadillo_medina_tc_expense("VERCEL INC CLOUD", banco="TC MERCADO PAGO") is False
    assert is_delgadillo_medina_tc_expense("CFE SUMINISTRADOR", banco="TC MERCADO PAGO") is False

    # 4. Proyectos explícitos de clientes con TC -> NO es Delgadillo Medina (se respeta el cliente)
    assert is_delgadillo_medina_tc_expense("COMPRA MATERIALES DAM", banco="TC MERCADO PAGO") is False
    assert is_delgadillo_medina_tc_expense("INSUMOS HEALTHYICE", banco="TC MERCADO PAGO") is False

    # 5. Gastos que NO son de tarjeta de crédito (ej. BBVA cuenta fiscal) -> NUNCA aplica Delgadillo Medina
    assert is_delgadillo_medina_tc_expense("Compra en MP ECOMMERCE 10 de 12", banco="BBVA") is False
    assert is_delgadillo_medina_tc_expense("TIENDA DE ABARROTES DON JUAN", banco="BBVA") is False
    assert is_delgadillo_medina_tc_expense("PAGO DE IMPUESTOS AL SAT", banco="BBVA") is False


def test_batch_update_status_personal_expense():
    client = TestClient(app)
    db = SessionLocal()
    tx_ids = ["tx-batch-test-01", "tx-batch-test-02", "tx-batch-test-03"]
    try:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(tx_ids)).delete()
        db.commit()

        # Crear 3 transacciones de egreso sin CFDI
        for idx, tid in enumerate(tx_ids):
            tx = BankTransaction(
                account_rfc="DEGF851127TK1",
                id_transaccion=tid,
                banco="TC MERCADO PAGO",
                fecha=datetime(2026, 9, 10 + idx),
                concepto=f"COMPRA PERSONAL {idx + 1}",
                monto=250.0 * (idx + 1),
                tipo="EGRESO",
                status_conciliacion="SIN_CFDI",
                area_proyecto="HIPHA",
                periodo_mes="2026-09"
            )
            db.add(tx)
        db.commit()

        created_txs = db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(tx_ids)).all()
        assert len(created_txs) == 3
        numeric_ids = [t.id for t in created_txs]

        # Llamar al endpoint por lote
        res = client.post(
            "/api/dashboard/reconciliation/transactions/batch-status",
            json={
                "transaction_ids": numeric_ids,
                "status_conciliacion": "NO_APLICA",
                "motivo": "Gasto Personal / No Deducible (DELGADILLO MEDINA)",
                "area_proyecto": "DELGADILLO MEDINA"
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["updated_count"] == 3
        assert data["status_conciliacion"] == "NO_APLICA"
        assert data["area_proyecto"] == "DELGADILLO MEDINA"

        # Verificar en base de datos
        db.expire_all()
        db_txs = db.query(BankTransaction).filter(BankTransaction.id.in_(numeric_ids)).all()
        for t in db_txs:
            assert t.status_conciliacion == "NO_APLICA"
            assert t.area_proyecto == "DELGADILLO MEDINA"
            assert "DELGADILLO MEDINA" in t.nota_revision
    finally:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(tx_ids)).delete()
        db.commit()
        db.close()


def test_batch_update_project():
    client = TestClient(app)
    db = SessionLocal()
    tx_ids = ["tx-batch-proj-01", "tx-batch-proj-02"]
    cfdi_uuids = ["CFDI-BATCH-PROJ-01", "CFDI-BATCH-PROJ-02"]
    try:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(tx_ids)).delete()
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_(cfdi_uuids)).delete()
        db.commit()

        for idx, (tid, cuuid) in enumerate(zip(tx_ids, cfdi_uuids)):
            inv = CFDIInvoice(
                uuid=cuuid,
                account_rfc="DEGF851127TK1",
                area_proyecto="GENERAL",
                tipo="EGRESO",
                rfc_emisor="EMISOR123",
                nombre_emisor="EMISOR PRUEBA",
                rfc_receptor="DEGF851127TK1",
                nombre_receptor="HIPHA",
                fecha_emision=datetime(2026, 9, 5),
                total=500.0,
                conciliado=True
            )
            db.add(inv)

            tx = BankTransaction(
                account_rfc="DEGF851127TK1",
                id_transaccion=tid,
                banco="BBVA",
                fecha=datetime(2026, 9, 5),
                concepto=f"COMPRA INSUMOS {idx}",
                monto=500.0,
                tipo="EGRESO",
                uuid_cfdi=cuuid,
                status_conciliacion="CONCILIADO",
                area_proyecto="GENERAL",
                periodo_mes="2026-09"
            )
            db.add(tx)
        db.commit()

        created_txs = db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(tx_ids)).all()
        numeric_ids = [t.id for t in created_txs]

        # Llamar al endpoint batch-project actualizando a "DAM" y propagando a CFDIs
        res = client.post(
            "/api/dashboard/reconciliation/transactions/batch-project",
            json={
                "transaction_ids": numeric_ids,
                "area_proyecto": "DAM",
                "update_cfdi": True
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["updated_count"] == 2
        assert data["area_proyecto"] == "DAM"

        # Validar en base de datos
        db.expire_all()
        db_txs = db.query(BankTransaction).filter(BankTransaction.id.in_(numeric_ids)).all()
        for t in db_txs:
            assert t.area_proyecto == "DAM"

        db_invs = db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_(cfdi_uuids)).all()
        for inv in db_invs:
            assert inv.area_proyecto == "DAM"
    finally:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(tx_ids)).delete()
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_(cfdi_uuids)).delete()
        db.commit()
        db.close()


def test_filter_by_amount_and_duplicates():
    client = TestClient(app)
    db = SessionLocal()
    test_ids = ["tx-dup-amt-01", "tx-dup-amt-02", "tx-dup-amt-03"]
    try:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(test_ids)).delete()
        db.commit()

        # Dos transacciones con mismo monto (1234.50) y una con monto único (500.00)
        tx1 = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion="tx-dup-amt-01",
            banco="BBVA",
            fecha=datetime(2026, 6, 10),
            concepto="SUSCRIPCION SOFTWARE DUPLICADA 1",
            monto=1234.50,
            tipo="EGRESO",
            status_conciliacion="SIN_CFDI",
            area_proyecto="HIPHA",
            periodo_mes="2026-06"
        )
        tx2 = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion="tx-dup-amt-02",
            banco="BBVA",
            fecha=datetime(2026, 6, 10),
            concepto="SUSCRIPCION SOFTWARE DUPLICADA 2",
            monto=1234.50,
            tipo="EGRESO",
            status_conciliacion="SIN_CFDI",
            area_proyecto="HIPHA",
            periodo_mes="2026-06"
        )
        tx3 = BankTransaction(
            account_rfc="DEGF851127TK1",
            id_transaccion="tx-dup-amt-03",
            banco="BBVA",
            fecha=datetime(2026, 6, 12),
            concepto="PAGO SERVICIO UNICO",
            monto=500.00,
            tipo="EGRESO",
            status_conciliacion="SIN_CFDI",
            area_proyecto="HIPHA",
            periodo_mes="2026-06"
        )
        db.add_all([tx1, tx2, tx3])
        db.commit()

        # 1. Validar KPIs en Overview
        res_ov = client.get("/api/dashboard/reconciliation/overview?month=2026-06&account_rfc=DEGF851127TK1")
        assert res_ov.status_code == 200
        kpis = res_ov.json()["kpis"]
        assert kpis["count_posibles_duplicados"] == 2
        assert kpis["monto_posibles_duplicados"] == pytest.approx(2469.00, 0.01)

        # 2. Filtrar por monto exacto ($1,234.50)
        res_amt = client.get("/api/dashboard/reconciliation/transactions?month=2026-06&account_rfc=DEGF851127TK1&amount=1234.50")
        assert res_amt.status_code == 200
        items_amt = res_amt.json()
        assert len(items_amt) == 2
        for it in items_amt:
            assert it["monto"] == 1234.50
            assert it["duplicate_count"] == 2
            assert it["is_possible_duplicate"] is True

        # 3. Filtrar por monto único ($500.00)
        res_single = client.get("/api/dashboard/reconciliation/transactions?month=2026-06&account_rfc=DEGF851127TK1&amount=500.00")
        assert res_single.status_code == 200
        items_single = res_single.json()
        assert len(items_single) == 1
        assert items_single[0]["monto"] == 500.00
        assert items_single[0]["duplicate_count"] == 1
        assert items_single[0]["is_possible_duplicate"] is False

        # 4. Filtrar solo duplicados (only_duplicates=true)
        res_dups = client.get("/api/dashboard/reconciliation/transactions?month=2026-06&account_rfc=DEGF851127TK1&only_duplicates=true")
        assert res_dups.status_code == 200
        items_dups = res_dups.json()
        assert len(items_dups) == 2
        assert all(it["monto"] == 1234.50 for it in items_dups)

    finally:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(test_ids)).delete()
        db.commit()
        db.close()


def test_comprobar_invoice_endpoints():
    db = SessionLocal()
    test_uuid = "CFDI-COMPROBAR-TEST-001"
    try:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == test_uuid).delete()
        db.commit()

        test_inv = CFDIInvoice(
            uuid=test_uuid,
            account_rfc="DEGF851127TK1",
            rfc_emisor="PROV999999XYZ",
            nombre_emisor="SERVICIOS HIPOTECARES SA DE CV",
            rfc_receptor="DEGF851127TK1",
            nombre_receptor="FRANCISCO DEGOLLADO",
            fecha_emision=datetime(2026, 7, 10, 10, 0, 0),
            total=4500.00,
            subtotal=4500.00,
            tipo="EGRESO",
            conciliado=False,
            comprobado=False,
            motivo_comprobacion=None,
            area_proyecto="HIPHA"
        )
        db.add(test_inv)
        db.commit()

        # 1. Comprobar la factura con motivo "Hipoteca"
        res_comp = client.post(
            f"/api/dashboard/reconciliation/invoices/{test_uuid}/comprobar",
            json={"motivo": "Hipoteca"}
        )
        assert res_comp.status_code == 200
        data_comp = res_comp.json()
        assert data_comp["success"] is True
        assert data_comp["comprobado"] is True
        assert data_comp["motivo_comprobacion"] == "Hipoteca"

        # Verificar en base de datos
        db_inv = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == test_uuid).first()
        assert db_inv.comprobado is True
        assert db_inv.motivo_comprobacion == "Hipoteca"

        # 2. Validar que /pending-invoices NO la incluya si include_comprobados=False
        res_pend = client.get("/api/dashboard/reconciliation/pending-invoices?account_rfc=DEGF851127TK1")
        assert res_pend.status_code == 200
        uuids_pend = [i["uuid"] for i in res_pend.json()]
        assert test_uuid not in uuids_pend

        # 3. Validar que /pending-invoices SÍ la incluya si include_comprobados=True
        res_inc = client.get("/api/dashboard/reconciliation/pending-invoices?account_rfc=DEGF851127TK1&include_comprobados=true")
        assert res_inc.status_code == 200
        items_inc = [i for i in res_inc.json() if i["uuid"] == test_uuid]
        assert len(items_inc) == 1
        assert items_inc[0]["comprobado"] is True
        assert items_inc[0]["motivo_comprobacion"] == "Hipoteca"

        # 4. Validar filtro comprobado_status=COMPROBADO vs PENDIENTE
        res_status_comp = client.get("/api/dashboard/reconciliation/pending-invoices?account_rfc=DEGF851127TK1&comprobado_status=COMPROBADO")
        assert res_status_comp.status_code == 200
        assert any(i["uuid"] == test_uuid for i in res_status_comp.json())

        res_status_pend = client.get("/api/dashboard/reconciliation/pending-invoices?account_rfc=DEGF851127TK1&comprobado_status=PENDIENTE")
        assert res_status_pend.status_code == 200
        assert not any(i["uuid"] == test_uuid for i in res_status_pend.json())

        # 5. Cambiar motivo a "Pago efectivo"
        res_comp2 = client.post(
            f"/api/dashboard/reconciliation/invoices/{test_uuid}/comprobar",
            json={"motivo": "Pago efectivo"}
        )
        assert res_comp2.status_code == 200
        assert res_comp2.json()["motivo_comprobacion"] == "Pago efectivo"

        # 6. Revertir comprobación
        res_rev = client.post(f"/api/dashboard/reconciliation/invoices/{test_uuid}/revert-comprobar")
        assert res_rev.status_code == 200
        data_rev = res_rev.json()
        assert data_rev["success"] is True
        assert data_rev["comprobado"] is False
        assert data_rev["motivo_comprobacion"] is None

        # Verificar en DB que se desmarcó
        db.refresh(db_inv)
        assert db_inv.comprobado is False
        assert db_inv.motivo_comprobacion is None

        # Ahora debe volver a aparecer en /pending-invoices normal
        res_pend_after = client.get("/api/dashboard/reconciliation/pending-invoices?account_rfc=DEGF851127TK1")
        assert res_pend_after.status_code == 200
        assert any(i["uuid"] == test_uuid for i in res_pend_after.json())

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == test_uuid).delete()
        db.commit()
        db.close()


def test_purge_credit_card_transactions():
    db = SessionLocal()
    test_uuid = "CFDI-TC-PURGE-TEST-001"
    test_tx_id = "test-tc-purge-tx-001"
    try:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion == test_tx_id).delete()
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == test_uuid).delete()
        db.commit()

        # 1. Crear una factura CFDI y una transacción de TC vinculada
        test_inv = CFDIInvoice(
            uuid=test_uuid,
            account_rfc="DEGF851127TK1",
            rfc_emisor="PROV888888XYZ",
            nombre_emisor="PROVEEDOR TC TEST SA",
            rfc_receptor="DEGF851127TK1",
            fecha_emision=datetime(2026, 7, 5),
            total=1250.00,
            subtotal=1250.00,
            tipo="EGRESO",
            conciliado=True,
            comprobado=False,
            motivo_comprobacion=None,
            area_proyecto="HIPHA"
        )
        db.add(test_inv)

        test_tx = BankTransaction(
            id_transaccion=test_tx_id,
            account_rfc="DEGF851127TK1",
            fecha=datetime(2026, 7, 5),
            monto=1250.00,
            tipo="EGRESO",
            banco="TC MERCADO PAGO",
            concepto="Compra en PROVEEDOR TC TEST",
            status_conciliacion="CONCILIADO",
            uuid_cfdi=test_uuid,
            periodo_mes="2026-07"
        )
        db.add(test_tx)
        db.commit()

        # 2. Ejecutar la purga
        res_purge = client.post("/api/dashboard/reconciliation/purge-credit-card-transactions?account_rfc=DEGF851127TK1")
        assert res_purge.status_code == 200
        data_purge = res_purge.json()
        assert data_purge["success"] is True
        assert data_purge["deleted_transactions_count"] >= 1
        assert test_uuid in data_purge["migrated_cfdi_uuids"]

        # 3. Validar que la transacción de TC fue eliminada
        db_tx = db.query(BankTransaction).filter(BankTransaction.id_transaccion == test_tx_id).first()
        assert db_tx is None

        # 4. Validar que la factura CFDI ahora está comprobada como 'TC Mercado Libre'
        db_inv = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == test_uuid).first()
        assert db_inv is not None
        assert db_inv.comprobado is True
        assert db_inv.motivo_comprobacion == "TC Mercado Libre"
        assert db_inv.conciliado is False

    finally:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion == test_tx_id).delete()
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == test_uuid).delete()
        db.commit()
        db.close()


def test_parse_complemento_de_pago():
    rep_xml = b"""<?xml version="1.0" encoding="utf-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
    xmlns:pago20="http://www.sat.gob.mx/Pagos20"
    xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
    Version="4.0" Fecha="2026-06-15T10:00:00" Total="0" SubTotal="0" Moneda="XXX" TipoDeComprobante="P">
    <cfdi:Emisor Rfc="MEHA850118Q96" Nombre="ADRIANA MEDINA HERNANDEZ" />
    <cfdi:Receptor Rfc="DME950316G28" Nombre="DAL-TILE MEXICO S DE RL DE CV" />
    <cfdi:Complemento>
        <pago20:Pagos Version="2.0">
            <pago20:Totales MontoTotalPagos="55200.50" TotalTrasladosBaseIVA16="47586.64" TotalTrasladosImpuestoIVA16="7613.86" />
            <pago20:Pago FechaPago="2026-06-14T12:00:00" FormaDePagoP="03" MonedaP="MXN" Monto="55200.50">
                <pago20:DoctoRelacionado IdDocumento="11111111-2222-3333-4444-555555555555" ImpPagado="55200.50" ImpSaldoAnt="55200.50" ImpSaldoInsoluto="0.00" NumParcialidad="1" />
            </pago20:Pago>
        </pago20:Pagos>
        <tfd:TimbreFiscalDigital UUID="REP-TEST-UUID-1234-5678" FechaTimbrado="2026-06-15T10:05:00" />
    </cfdi:Complemento>
</cfdi:Comprobante>"""

    parsed = parse_cfdi_xml(rep_xml, mi_rfc="MEHA850118Q96")
    assert parsed["uuid"] == "REP-TEST-UUID-1234-5678"
    assert parsed["tipo"] == "INGRESO"
    assert parsed["total"] == 55200.50
    assert parsed["metodo_pago"] == "PAGO"
    assert parsed["es_pago"] is True
    assert len(parsed["doctos_relacionados"]) == 1
    assert parsed["doctos_relacionados"][0]["uuid"] == "11111111-2222-3333-4444-555555555555"
    assert parsed["doctos_relacionados"][0]["imp_pagado"] == 55200.50


def test_parse_cfdi_nomina():
    nomina_xml = """<?xml version="1.0" encoding="utf-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
    xmlns:nomina12="http://www.sat.gob.mx/nomina12"
    xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
    Version="4.0" Fecha="2026-04-15T18:00:00" Total="8500.00" SubTotal="9000.00" TipoDeComprobante="N">
    <cfdi:Emisor Rfc="MEHA850118Q96" Nombre="ADRIANA MEDINA HERNANDEZ" />
    <cfdi:Receptor Rfc="EMPLEADO123" Nombre="JUAN PEREZ LOPEZ" />
    <cfdi:Conceptos>
        <cfdi:Concepto Descripcion="Pago de nómina quincenal" Importe="9000.00" />
    </cfdi:Conceptos>
    <cfdi:Complemento>
        <nomina12:Nomina Version="1.2" TipoNomina="O" FechaPago="2026-04-15" />
        <tfd:TimbreFiscalDigital UUID="NOMINA-UUID-TEST-9999" FechaTimbrado="2026-04-15T18:05:00" />
    </cfdi:Complemento>
</cfdi:Comprobante>""".encode("utf-8")

    parsed = parse_cfdi_xml(nomina_xml, mi_rfc="MEHA850118Q96")
    assert parsed["uuid"] == "NOMINA-UUID-TEST-9999"
    assert parsed["tipo"] == "EGRESO"
    assert parsed["es_nomina"] is True
    assert parsed["total"] == 8500.00


def test_matching_consolidated_invoices():
    facturas = [
        {
            "uuid": "INV-DALTILE-01",
            "tipo": "INGRESO",
            "rfc_emisor": "MEHA850118Q96",
            "rfc_receptor": "DME950316G28",
            "nombre_receptor": "DAL-TILE MEXICO S DE RL DE CV",
            "fecha_emision": "2026-03-01",
            "total": 100000.00,
            "metodo_pago": "PPD",
            "conceptos_resumen": "Suministro e instalacion"
        },
        {
            "uuid": "INV-DALTILE-02",
            "tipo": "INGRESO",
            "rfc_emisor": "MEHA850118Q96",
            "rfc_receptor": "DME950316G28",
            "nombre_receptor": "DAL-TILE MEXICO S DE RL DE CV",
            "fecha_emision": "2026-03-02",
            "total": 50000.00,
            "metodo_pago": "PPD",
            "conceptos_resumen": "Mantenimiento canceleria"
        }
    ]

    transacciones = [
        {
            "id": 101,
            "id_transaccion": "TX-CONSOLIDATED-01",
            "fecha": datetime(2026, 3, 10),
            "concepto": "DEPOSITO POR SPEI DAL-TILE MEXICO SA FACT 101 Y 102",
            "monto": 150000.00,
            "tipo": "INGRESO",
            "banco": "BBVA"
        }
    ]

    resultados = conciliar_movimientos(transacciones, facturas)
    assert len(resultados) == 1
    res = resultados[0]
    assert res["status_conciliacion"] == "CONCILIADO"
    assert res["confianza_score"] == 1.0
    assert set(res["related_cfdi_uuids"]) == {"INV-DALTILE-01", "INV-DALTILE-02"}


def test_matching_complemento_de_pago():
    facturas = [
        {
            "uuid": "REP-UUID-900",
            "tipo": "INGRESO",
            "rfc_emisor": "MEHA850118Q96",
            "rfc_receptor": "DME950316G28",
            "nombre_receptor": "DAL-TILE MEXICO S DE RL DE CV",
            "fecha_emision": "2026-04-12",
            "total": 45000.00,
            "metodo_pago": "PAGO",
            "conceptos_resumen": "Complemento de Pago ampara INV-01",
            "doctos_relacionados": [{"uuid": "INV-PPD-ORIGINAL-01", "imp_pagado": 45000.00}]
        }
    ]

    transacciones = [
        {
            "id": 102,
            "id_transaccion": "TX-REP-01",
            "fecha": datetime(2026, 4, 12),
            "concepto": "SPEI RECIBIDO DE DAL TILE REF 9920",
            "monto": 45000.00,
            "tipo": "INGRESO",
            "banco": "BBVA"
        }
    ]

    resultados = conciliar_movimientos(transacciones, facturas)
    assert len(resultados) == 1
    res = resultados[0]
    assert res["status_conciliacion"] in ("CONCILIADO", "CONCILIADO_POR_REGLA")
    assert res["uuid_cfdi"] == "REP-UUID-900"
    assert "INV-PPD-ORIGINAL-01" in res["related_cfdi_uuids"]


def test_reprocess_endpoint():
    res = client.post("/api/dashboard/reconciliation/reprocess?account_rfc=MEHA850118Q96")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "invoices_reparsed" in data
    assert "matches_creados" in data
    assert data["entity"]["rfc"] == "MEHA850118Q96"


def test_upload_idempotency_and_distinct_date_duplicates():
    from app.api.dashboard.reconciliation_routes import _find_existing_transaction
    db = SessionLocal()
    test_ids = ["TX-IDEM-01", "TX-IDEM-02", "TX-IDEM-03"]
    try:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(test_ids)).delete()
        db.commit()

        # 1. Validar idempotencia con _find_existing_transaction
        tx1 = BankTransaction(
            account_rfc="MEHA850118Q96",
            id_transaccion="TX-IDEM-01",
            banco="BBVA",
            fecha=datetime(2026, 5, 15, 10, 30),
            concepto="PAGO RENTA OFICINAS BBVA",
            monto=3000.00,
            tipo="EGRESO",
            saldo=50000.00,
            status_conciliacion="SIN_CFDI",
            area_proyecto="AMDI",
            periodo_mes="2026-05"
        )
        db.add(tx1)
        db.commit()

        # Simular candidato proveniente de otro parser (ej. PDF vs Excel) con distinto hash_seed
        candidate = {
            "id_transaccion": "TX-IDEM-CANDIDATE-DIFF-HASH",
            "fecha": datetime(2026, 5, 15, 0, 0),
            "concepto": "PAGO RENTA OFICINAS",
            "monto": 3000.00,
            "tipo": "EGRESO",
            "saldo": 50000.00
        }
        found = _find_existing_transaction(db, candidate, "MEHA850118Q96")
        assert found is not None
        assert found.id_transaccion == "TX-IDEM-01"

        # 2. Agregar movimiento recurrente en OTRA fecha (20 de mayo)
        tx2 = BankTransaction(
            account_rfc="MEHA850118Q96",
            id_transaccion="TX-IDEM-02",
            banco="BBVA",
            fecha=datetime(2026, 5, 20, 14, 0),
            concepto="PAGO SUMINISTROS DIVERSOS",
            monto=3000.00,
            tipo="EGRESO",
            saldo=47000.00,
            status_conciliacion="SIN_CFDI",
            area_proyecto="AMDI",
            periodo_mes="2026-05"
        )
        db.add(tx2)
        db.commit()

        # Como están en fechas diferentes (15 de mayo vs 20 de mayo), NO deben marcarse como duplicados
        res_ov1 = client.get("/api/dashboard/reconciliation/overview?month=2026-05&account_rfc=MEHA850118Q96")
        assert res_ov1.status_code == 200
        assert res_ov1.json()["kpis"]["count_posibles_duplicados"] == 0

        # 3. Agregar movimiento duplicado en la MISMA fecha (15 de mayo)
        tx3 = BankTransaction(
            account_rfc="MEHA850118Q96",
            id_transaccion="TX-IDEM-03",
            banco="BBVA",
            fecha=datetime(2026, 5, 15, 18, 0),
            concepto="PAGO RENTA OFICINAS CARGO DOBLE",
            monto=3000.00,
            tipo="EGRESO",
            saldo=44000.00,
            status_conciliacion="SIN_CFDI",
            area_proyecto="AMDI",
            periodo_mes="2026-05"
        )
        db.add(tx3)
        db.commit()

        # Ahora sí debe detectar 2 movimientos duplicados en el 15 de mayo
        res_ov2 = client.get("/api/dashboard/reconciliation/overview?month=2026-05&account_rfc=MEHA850118Q96")
        assert res_ov2.status_code == 200
        assert res_ov2.json()["kpis"]["count_posibles_duplicados"] == 2

        # Filtrar solo duplicados en /transactions
        res_dups = client.get("/api/dashboard/reconciliation/transactions?month=2026-05&account_rfc=MEHA850118Q96&only_duplicates=true")
        assert res_dups.status_code == 200
        dups_data = res_dups.json()
        assert len(dups_data) == 2
        returned_ids = {d["id_transaccion"] for d in dups_data}
        assert returned_ids == {"TX-IDEM-01", "TX-IDEM-03"}

    finally:
        db.query(BankTransaction).filter(BankTransaction.id_transaccion.in_(test_ids)).delete()
        db.commit()
        db.close()


def test_sabana_deduplication_and_enrichment():
    db = SessionLocal()
    test_rfc = "MEHA850118Q96"
    test_month = "2026-01"
    uuid_test = "99999999-8888-7777-6666-555555555555"

    try:
        # Limpiar datos previos de prueba
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == test_rfc,
            BankTransaction.periodo_mes == test_month
        ).delete()
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_test).delete()
        db.commit()

        # 1. Simular transacción existente proveniente del extracto BBVA (con saldo y concepto técnico)
        bbva_tx = BankTransaction(
            account_rfc=test_rfc,
            id_transaccion="BBVA-JAN-001",
            banco="BBVA",
            fecha=datetime(2026, 1, 5, 12, 0),
            concepto="SPEI ENVIADO INBURSA REF 12345678 CUENTA 9876543210",
            monto=60000.00,
            tipo="EGRESO",
            saldo=145230.50,
            status_conciliacion="SIN_CFDI",
            area_proyecto="AMDI",
            periodo_mes=test_month
        )
        db.add(bbva_tx)
        db.commit()

        # 2. Simular importación de la sábana Excel que contiene el mismo movimiento pero con descripción humana y área específica
        sample_sabana_csv = (
            b"FECHA,\xc1REA / PROYECTO,FOLIO FISCAL,CLIENTE / PROVEEDOR,CONCEPTO,M\xc9TODO DE PAGO,INGRESOS,EGRESOS,CFDI,TIPO,SUBTOTAL,IVA INGRESOS,RETENCI\xd3N ISR,IVA EGRESOS\n"
            b"05/01/2026,DELGADILLO MEDINA,99999999-8888-7777-6666-555555555555,PRESTAMISTA SA,PRESTAMO CORPORATIVO,PUE,,60000.00,E,EGRESO,60000.00,0.00,0.00,0.00\n"
        )

        res = import_historical_excel(
            sample_sabana_csv,
            "sabana_enero.csv",
            db,
            mi_rfc=test_rfc,
            account_rfc=test_rfc
        )
        assert res["success"] is True

        # 3. Verificar que NO se duplicó el registro en la base de datos
        all_txs = db.query(BankTransaction).filter(
            BankTransaction.account_rfc == test_rfc,
            BankTransaction.periodo_mes == test_month
        ).all()
        assert len(all_txs) == 1, f"Se esperaba 1 transacción pero se encontraron {len(all_txs)}"

        enriched_tx = all_txs[0]
        # Debe haber preservado el saldo bancario real y el hash original de BBVA
        assert enriched_tx.id_transaccion == "BBVA-JAN-001"
        assert enriched_tx.saldo == 145230.50
        # Debe haberse enriquecido con el área y el UUID de la sábana
        assert enriched_tx.area_proyecto == "DELGADILLO MEDINA"
        assert enriched_tx.uuid_cfdi == uuid_test
        assert enriched_tx.status_conciliacion == "CONCILIADO"

    finally:
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == test_rfc,
            BankTransaction.periodo_mes == test_month
        ).delete()
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_test).delete()
        db.commit()
        db.close()


def test_deduplicate_cross_source_bank_and_sabana():
    db = SessionLocal()
    test_rfc = "MEHA850118Q96"
    test_month = "2026-01"

    try:
        # Limpiar
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == test_rfc,
            BankTransaction.periodo_mes == test_month
        ).delete()
        db.commit()

        # 1. Movimiento BBVA oficial (con saldo)
        tx_bank = BankTransaction(
            account_rfc=test_rfc,
            id_transaccion="TX-BANK-01",
            banco="BBVA",
            fecha=datetime(2026, 1, 7, 10, 30),
            concepto="COMISION BBVA PAQUETE PYME",
            monto=104.00,
            tipo="EGRESO",
            saldo=145126.50,
            status_conciliacion="SIN_CFDI",
            area_proyecto="AMDI",
            periodo_mes=test_month
        )
        # 2. Movimiento Sábana (sin saldo, área específica)
        tx_sabana = BankTransaction(
            account_rfc=test_rfc,
            id_transaccion="TX-SABANA-01",
            banco="BBVA",
            fecha=datetime(2026, 1, 7, 0, 0),
            concepto="COMISION BBVA",
            monto=104.00,
            tipo="EGRESO",
            saldo=None,
            status_conciliacion="SIN_CFDI",
            area_proyecto="DELGADILLO MEDINA",
            periodo_mes=test_month
        )
        db.add(tx_bank)
        db.add(tx_sabana)
        db.commit()

        # Verificar que inicialmente hay 2 posibles duplicados
        res_ov = client.get(f"/api/dashboard/reconciliation/overview?month={test_month}&account_rfc={test_rfc}")
        assert res_ov.status_code == 200
        assert res_ov.json()["kpis"]["count_posibles_duplicados"] == 2

        # Llamar a /deduplicate
        res_dedup = client.post(f"/api/dashboard/reconciliation/deduplicate?account_rfc={test_rfc}&month={test_month}")
        assert res_dedup.status_code == 200
        data_dedup = res_dedup.json()
        assert data_dedup["success"] is True
        assert data_dedup["deleted_count"] == 1

        # Verificar que quedó únicamente la transacción bancaria oficial con el área de la sábana
        remaining_txs = db.query(BankTransaction).filter(
            BankTransaction.account_rfc == test_rfc,
            BankTransaction.periodo_mes == test_month
        ).all()
        assert len(remaining_txs) == 1
        rem = remaining_txs[0]
        assert rem.id_transaccion == "TX-BANK-01"
        assert rem.saldo == 145126.50
        assert rem.area_proyecto == "DELGADILLO MEDINA"
        assert "Sábana: COMISION BBVA" in (rem.nota_revision or "")

        # Verificar que los posibles duplicados ahora son 0
        res_ov_after = client.get(f"/api/dashboard/reconciliation/overview?month={test_month}&account_rfc={test_rfc}")
        assert res_ov_after.status_code == 200
        assert res_ov_after.json()["kpis"]["count_posibles_duplicados"] == 0

    finally:
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == test_rfc,
            BankTransaction.periodo_mes == test_month
        ).delete()
        db.commit()
        db.close()


def test_egresos_own_accounts_exclusion_overview():
    """
    Verifica que los retiros en cajero y traspasos entre cuentas propias en egresos
    sean debidamente excluidos de 'total_egresos_banco' y 'count_egresos_banco',
    y se expongan en 'total_traspasos_egresos' y 'total_egresos_bruto'.
    """
    db = SessionLocal()
    test_rfc = "DEGF851127TK1"
    test_month = "2026-03"

    try:
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == test_rfc,
            BankTransaction.periodo_mes == test_month
        ).delete()
        db.commit()

        # 1. Traspaso entre cuentas propias
        t1 = BankTransaction(
            id_transaccion="TX-EGR-01",
            account_rfc=test_rfc,
            banco="BBVA",
            fecha=datetime(2026, 3, 21),
            concepto="PAGO CUENTA DE TERCERO - 0008727337  BNET 1184465733 Entre cuentas",
            monto=19452.75,
            tipo="EGRESO",
            periodo_mes=test_month,
            status_conciliacion="NO_APLICA",
            nota_revision="Traspaso entre Cuentas Propias"
        )
        # 2. Retiro en cajero automático
        t2 = BankTransaction(
            id_transaccion="TX-EGR-02",
            account_rfc=test_rfc,
            banco="BBVA",
            fecha=datetime(2026, 3, 12),
            concepto="RETIRO CAJERO AUTOMATICO - ******7842  MAR12 13:02 BBVA A312",
            monto=5000.00,
            tipo="EGRESO",
            periodo_mes=test_month,
            status_conciliacion="NO_APLICA",
            nota_revision="Traspaso entre Cuentas Propias"
        )
        # 3. Gasto operativo comercial con CFDI
        t3 = BankTransaction(
            id_transaccion="TX-EGR-03",
            account_rfc=test_rfc,
            banco="BBVA",
            fecha=datetime(2026, 3, 10),
            concepto="NEUBOX INTERNET SA DE CV",
            monto=301.48,
            tipo="EGRESO",
            periodo_mes=test_month,
            status_conciliacion="CONCILIADO",
            uuid_cfdi="UUID-NEUBOX-123"
        )
        # 4. Gasto operativo comercial sin CFDI pendiente
        t4 = BankTransaction(
            id_transaccion="TX-EGR-04",
            account_rfc=test_rfc,
            banco="BBVA",
            fecha=datetime(2026, 3, 15),
            concepto="COMPRA EN HOME DEPOT",
            monto=674.00,
            tipo="EGRESO",
            periodo_mes=test_month,
            status_conciliacion="SIN_CFDI"
        )
        # 5. Pago de impuestos al SAT (exento/no aplica pero es gasto operativo del negocio)
        t5 = BankTransaction(
            id_transaccion="TX-EGR-05",
            account_rfc=test_rfc,
            banco="BBVA",
            fecha=datetime(2026, 3, 18),
            concepto="PAGO DE IMPUESTOS SAT TESORERIA DE LA FEDERACION",
            monto=3228.00,
            tipo="EGRESO",
            periodo_mes=test_month,
            status_conciliacion="NO_APLICA",
            nota_revision="Impuestos SAT"
        )
        db.add_all([t1, t2, t3, t4, t5])
        db.commit()

        # Consultar overview
        res = client.get(f"/api/dashboard/reconciliation/overview?month={test_month}&account_rfc={test_rfc}")
        assert res.status_code == 200
        kpis = res.json()["kpis"]

        # Traspasos/retiros propios excluidos: $19,452.75 + $5,000.00 = $24,452.75 (2 movimientos)
        assert kpis["count_traspasos_egresos"] == 2
        assert kpis["total_traspasos_egresos"] == pytest.approx(24452.75, 0.01)

        # Egresos brutos totales: 19,452.75 + 5,000 + 301.48 + 674.00 + 3,228.00 = $28,656.23
        assert kpis["total_egresos_bruto"] == pytest.approx(28656.23, 0.01)

        # Egresos banco (operativos del negocio): 301.48 + 674.00 + 3,228.00 = $4,203.48 (3 movimientos)
        assert kpis["count_egresos_banco"] == 3
        assert kpis["total_egresos_banco"] == pytest.approx(4203.48, 0.01)

        # Sin CFDI pendientes (solo t4): $674.00
        assert kpis["count_sin_cfdi"] == 1
        assert kpis["monto_sin_cfdi"] == pytest.approx(674.00, 0.01)

        # No aplica operativos (solo SAT t5): $3,228.00
        assert kpis["count_no_aplica"] == 1
        assert kpis["monto_no_aplica"] == pytest.approx(3228.00, 0.01)

    finally:
        db.query(BankTransaction).filter(
            BankTransaction.account_rfc == test_rfc,
            BankTransaction.periodo_mes == test_month
        ).delete()
        db.commit()
        db.close()


def test_sabana_cash_invoices_marked_comprobado_and_no_bank_pollution():
    """
    Verifica que al importar una sábana con gastos en efectivo o tarjetas fuera de banco:
    1. Las facturas con UUID se marcan como comprobadas (comprobado=True, motivo='Efectivo', forma_pago='01').
    2. NO se inyectan transacciones fantasma en BankTransaction(banco="BBVA") para no inflar cargos operativos.
    """
    db = SessionLocal()
    test_rfc = "TEST_RFC_CASH_SABANA"
    test_month = "2026-05"

    try:
        # Sábana CSV con 2 filas: 1 en EFECTIVO con UUID, 1 en TC con UUID, y 1 transferencia oficial
        csv_content = (
            "FECHA,AREA,FOLIO FISCAL,PROVEEDOR,CONCEPTO,METODO,EGRESOS,SUBTOTAL,IVA\n"
            "2026-05-15,VENTAS,11111111-2222-3333-4444-555555555555,WALMART,COMPRA DESPENSA,EFECTIVO,555.00,478.45,76.55\n"
            "2026-05-16,PROYECTO A,66666666-7777-8888-9999-000000000000,MERCADO LIBRE,EQUIPO COMPUTO,T- CRÉDITO,1200.00,1034.48,165.52\n"
        ).encode("utf-8")

        res = import_historical_excel(csv_content, "sabana_mayo.csv", db, account_rfc=test_rfc)
        assert res["success"] is True

        # Verificar que NO se crearon transacciones bancarias BBVA para los pagos fuera de banco
        txs = db.query(BankTransaction).filter(BankTransaction.account_rfc == test_rfc).all()
        assert len(txs) == 0

        # Verificar que los CFDIs se registraron y quedaron como comprobados
        inv1 = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == "11111111-2222-3333-4444-555555555555").first()
        assert inv1 is not None
        assert inv1.comprobado is True
        assert inv1.motivo_comprobacion == "Efectivo"
        assert inv1.forma_pago == "01"

        inv2 = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == "66666666-7777-8888-9999-000000000000").first()
        assert inv2 is not None
        assert inv2.comprobado is True
        assert inv2.motivo_comprobacion == "Otra TC"
        assert inv2.forma_pago == "04"

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.account_rfc == test_rfc).delete()
        db.query(BankTransaction).filter(BankTransaction.account_rfc == test_rfc).delete()
        db.commit()
        db.close()


def test_deduplicate_spei_devuelto_and_sabana_consolidation():
    """
    Verifica que el endpoint /deduplicate:
    1. Reclasifique SPEI DEVUELTO como INGRESO y le asigne status NO_APLICA.
    2. Cancele el SPEI ENVIADO correspondiente como NO_APLICA.
    3. Elimine transacciones de sábana (saldo=None) cuando ya existe extracto oficial y acredite las facturas.
    """
    db = SessionLocal()
    test_rfc = "TEST_RFC_DEDUP"
    test_month = "2026-05"

    try:
        # Movimiento 1: SPEI ENVIADO (con saldo de banco oficial)
        t_enviado = BankTransaction(
            account_rfc=test_rfc,
            id_transaccion="tx_spei_enviado",
            banco="BBVA",
            fecha=datetime(2026, 5, 9, 10, 0),
            concepto="SPEI ENVIADO BANAMEX - Reembolso materiales",
            monto=6523.00,
            tipo="EGRESO",
            saldo=235515.64,
            periodo_mes=test_month,
            status_conciliacion="SIN_CFDI"
        )
        # Movimiento 2: SPEI DEVUELTO (con saldo de banco oficial, pero clasificado por error como EGRESO)
        t_devuelto = BankTransaction(
            account_rfc=test_rfc,
            id_transaccion="tx_spei_devuelto",
            banco="BBVA",
            fecha=datetime(2026, 5, 9, 11, 0),
            concepto="SPEI DEVUELTOBANAMEX - Reembolso materiales",
            monto=6523.00,
            tipo="EGRESO",
            saldo=228992.64,
            periodo_mes=test_month,
            status_conciliacion="SIN_CFDI"
        )
        # Movimiento 3: Movimiento oficial de banco
        t_oficial = BankTransaction(
            account_rfc=test_rfc,
            id_transaccion="tx_oficial",
            banco="BBVA",
            fecha=datetime(2026, 5, 20),
            concepto="PAGO DE SERVICIOS LUZ",
            monto=1500.00,
            tipo="EGRESO",
            saldo=227492.64,
            periodo_mes=test_month,
            status_conciliacion="SIN_CFDI"
        )
        # Movimiento 4: Movimiento fantasma de sábana (saldo=None) sin contraparte oficial en banco, con UUID
        test_uuid = "99999999-8888-7777-6666-555555555555"
        cfdi_phantom = CFDIInvoice(
            uuid=test_uuid,
            account_rfc=test_rfc,
            tipo="EGRESO",
            rfc_emisor="GAS123456789",
            rfc_receptor=test_rfc,
            fecha_emision=datetime(2026, 5, 26),
            subtotal=1476.72,
            iva_trasladado=236.28,
            total=1713.00,
            conciliado=False,
            comprobado=False
        )
        t_fantasma = BankTransaction(
            account_rfc=test_rfc,
            id_transaccion="tx_fantasma_sabana",
            banco="BBVA",
            fecha=datetime(2026, 5, 26),
            concepto="TRASLADO TEPIC - GDL",
            monto=1713.00,
            tipo="EGRESO",
            saldo=None,
            uuid_cfdi=test_uuid,
            periodo_mes=test_month,
            status_conciliacion="POR_REVISAR"
        )

        db.add_all([t_enviado, t_devuelto, t_oficial, cfdi_phantom, t_fantasma])
        db.commit()

        # Ejecutar deduplicate
        res = client.post(f"/api/dashboard/reconciliation/deduplicate?account_rfc={test_rfc}&month={test_month}")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["reclassified_count"] >= 1
        assert data["deleted_count"] >= 1

        # Verificar t_devuelto reclasificado como INGRESO y NO_APLICA
        db.refresh(t_devuelto)
        assert t_devuelto.tipo == "INGRESO"
        assert t_devuelto.status_conciliacion == "NO_APLICA"

        # Verificar t_enviado cancelado como NO_APLICA
        db.refresh(t_enviado)
        assert t_enviado.status_conciliacion == "NO_APLICA"

        # Verificar que la transacción fantasma fue eliminada
        db.expire_all()
        fantasma_check = db.query(BankTransaction).filter(BankTransaction.id_transaccion == "tx_fantasma_sabana").first()
        assert fantasma_check is None

        # Verificar que la factura del movimiento fantasma fue acreditada fuera de banco
        cfdi_check = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == test_uuid).first()
        assert cfdi_check is not None
        assert cfdi_check.comprobado is True

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.account_rfc == test_rfc).delete()
        db.query(BankTransaction).filter(BankTransaction.account_rfc == test_rfc).delete()
        db.commit()
        db.close()


def test_overview_xml_and_bank_statement_indicators():
    """
    Verifica que el endpoint /overview retorne correctamente el total de XMLs del mes
    (diferenciando ingresos y egresos) y el indicador de estado de cuenta bancario adjunto (BBVA Fiscal).
    """
    db = SessionLocal()
    test_rfc = "MEHA850118Q96"
    test_month = "2026-11"

    try:
        # 1. Crear facturas XML en el mes: 1 Ingreso y 2 Egresos
        inv_ing = CFDIInvoice(
            uuid="CFDI-TEST-IND-ING-01",
            account_rfc=test_rfc,
            tipo="INGRESO",
            rfc_emisor=test_rfc,
            rfc_receptor="CLIENTE01",
            fecha_emision=datetime(2026, 11, 5, 10, 0),
            total=15000.0,
            subtotal=12931.03,
            iva_trasladado=2068.97,
            conciliado=False,
            comprobado=False
        )
        inv_egr1 = CFDIInvoice(
            uuid="CFDI-TEST-IND-EGR-01",
            account_rfc=test_rfc,
            tipo="EGRESO",
            rfc_emisor="PROV01",
            rfc_receptor=test_rfc,
            fecha_emision=datetime(2026, 11, 10, 12, 0),
            total=3480.0,
            subtotal=3000.0,
            iva_trasladado=480.0,
            conciliado=False,
            comprobado=False
        )
        inv_egr2 = CFDIInvoice(
            uuid="CFDI-TEST-IND-EGR-02",
            account_rfc=test_rfc,
            tipo="EGRESO",
            rfc_emisor="PROV02",
            rfc_receptor=test_rfc,
            fecha_emision=datetime(2026, 11, 15, 15, 0),
            total=1160.0,
            subtotal=1000.0,
            iva_trasladado=160.0,
            conciliado=False,
            comprobado=False
        )
        db.add_all([inv_ing, inv_egr1, inv_egr2])

        # 2. Crear 2 transacciones oficiales de banco BBVA con saldo
        t_banco1 = BankTransaction(
            id_transaccion="tx_bbva_test_01",
            account_rfc=test_rfc,
            banco="BBVA",
            fecha=datetime(2026, 11, 5),
            concepto="DEPOSITO CLIENTE TEST",
            tipo="INGRESO",
            monto=15000.0,
            saldo=50000.0,
            periodo_mes=test_month,
            status_conciliacion="SIN_CFDI"
        )
        t_banco2 = BankTransaction(
            id_transaccion="tx_bbva_test_02",
            account_rfc=test_rfc,
            banco="BBVA",
            fecha=datetime(2026, 11, 10),
            concepto="PAGO PROVEEDOR 01",
            tipo="EGRESO",
            monto=3480.0,
            saldo=46520.0,
            periodo_mes=test_month,
            status_conciliacion="SIN_CFDI"
        )
        db.add_all([t_banco1, t_banco2])
        db.commit()

        # 3. Consultar overview para el mes
        res = client.get(f"/api/dashboard/reconciliation/overview?account_rfc={test_rfc}&month={test_month}")
        assert res.status_code == 200
        k = res.json()["kpis"]

        # Validar métricas de XMLs
        assert k["total_xml_mes"] == 3
        assert k["count_xml_ingresos"] == 1
        assert k["count_xml_egresos"] == 2

        # Validar indicador de estado de cuenta adjunto (BBVA Fiscal)
        assert k["has_bank_statement"] is True
        assert k["count_bank_statement_txs"] == 2
        assert k["bank_statement_name"] == "BBVA Fiscal"

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.account_rfc == test_rfc, CFDIInvoice.uuid.like("CFDI-TEST-IND-%")).delete()
        db.query(BankTransaction).filter(BankTransaction.account_rfc == test_rfc, BankTransaction.id_transaccion.like("tx_bbva_test_%")).delete()
        db.commit()
        db.close()


def test_export_pdf_faltantes_with_xmls_sueltos():
    """Valida la generación de PDF de discrepancias/faltantes incluyendo sección de XMLs sueltos."""
    txs_banco = [
        {
            "fecha": "2026-09-05",
            "concepto": "CARGO BBVA RETIRO EFECTIVO",
            "tipo": "EGRESO",
            "monto": 1500.0,
            "status_conciliacion": "SIN_CFDI"
        },
        {
            "fecha": "2026-09-12",
            "concepto": "COMPRA SIN FACTURA PROVEEDOR X",
            "tipo": "EGRESO",
            "monto": 3480.0,
            "status_conciliacion": "POR_REVISAR"
        }
    ]

    facturas_sueltas = [
        {
            "uuid": "4A1E5211-1B2C-3D4E-5F6A-7B8C9D0E1F2A",
            "fecha": "2026-09-10",
            "tipo": "EGRESO",
            "rfc_emisor": "THD970924V76",
            "nombre_emisor": "THE HOME DEPOT MEXICO",
            "concepto": "MATERIALES Y HERRAMIENTAS",
            "total": 1250.50,
            "forma_pago": "01",
            "metodo_pago": "PUE"
        },
        {
            "uuid": "5B2E6322-2C3D-4E5F-6A7B-8C9D0E1F2B3C",
            "fecha": "2026-09-15",
            "tipo": "INGRESO",
            "rfc_emisor": "MEHA850118Q96",
            "nombre_emisor": "AMDI SOLUCIONES",
            "concepto": "SERVICIO DE CONSULTORIA",
            "total": 23200.00,
            "forma_pago": "03",
            "metodo_pago": "PPD"
        }
    ]

    # 1. Prueba directa de generación de PDF con XMLs sueltos
    pdf_bytes = generate_discrepancies_pdf(
        transacciones=txs_banco,
        mes_label="TEST ENTITY (MEHA850118Q96) - 2026-09",
        facturas_sueltas=facturas_sueltas
    )

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 2000

    # 2. Prueba de endpoint HTTP
    res = client.get("/api/dashboard/reconciliation/export/pdf-faltantes?account_rfc=MEHA850118Q96&month=2026-09")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")
    assert len(res.content) > 1000


def test_complemento_de_pago_ampara_ppd_no_duplica_ingresos():
    """Valida que un Complemento de Pago marque la factura PPD como pagada y NO duplique el ingreso en overview."""
    db = SessionLocal()
    test_rfc = "MEHA850118Q96"
    test_month = "2026-11"

    uuid_ppd = "CFDI-TEST-PPD-ORIGINAL-001"
    uuid_rep = "CFDI-TEST-REP-COMPLEMENTO-001"
    tx_id = "tx_bbva_test_abono_rep_01"

    try:
        # Limpieza previa defensiva
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_([uuid_ppd, uuid_rep])).delete()
        db.query(BankTransaction).filter(BankTransaction.id_transaccion == tx_id).delete()
        db.commit()

        # 1. Factura original PPD de ingreso por $100,000 + IVA $16,000 = $116,000 emitida en el mes
        inv_ppd = CFDIInvoice(
            uuid=uuid_ppd,
            account_rfc=test_rfc,
            area_proyecto="AMDI",
            tipo="INGRESO",
            rfc_emisor=test_rfc,
            nombre_emisor="ADRIANA MEDINA HERNANDEZ",
            rfc_receptor="CLI901010ABC",
            nombre_receptor="CLIENTE CORPORATIVO SA DE CV",
            fecha_emision=datetime(2026, 11, 5, 10, 0, 0),
            subtotal=100000.0,
            iva_trasladado=16000.0,
            total=116000.0,
            metodo_pago="PPD",
            forma_pago="99",
            conceptos_resumen="Servicios de Diseño y Construcción",
            conciliado=False,
            comprobado=False
        )

        # 2. Complemento de Pago (REP) emitido al recibir el pago por $116,000
        # Simular XML con nodo DoctoRelacionado
        rep_xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
    xmlns:pago20="http://www.sat.gob.mx/Pagos20"
    xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
    Version="4.0" Fecha="2026-11-15T12:00:00" Total="0" SubTotal="0" TipoDeComprobante="P">
    <cfdi:Emisor Rfc="{test_rfc}" Nombre="ADRIANA MEDINA HERNANDEZ" />
    <cfdi:Receptor Rfc="CLI901010ABC" Nombre="CLIENTE CORPORATIVO SA DE CV" />
    <cfdi:Complemento>
        <pago20:Pagos Version="2.0">
            <pago20:Totales MontoTotalPagos="116000.00" TotalTrasladosBaseIVA16="100000.00" TotalTrasladosImpuestoIVA16="16000.00" />
            <pago20:Pago FechaPago="2026-11-15T11:30:00" FormaDePagoP="03" MonedaP="MXN" Monto="116000.00">
                <pago20:DoctoRelacionado IdDocumento="{uuid_ppd}" ImpPagado="116000.00" ImpSaldoAnt="116000.00" ImpSaldoInsoluto="0.00" NumParcialidad="1" />
            </pago20:Pago>
        </pago20:Pagos>
        <tfd:TimbreFiscalDigital UUID="{uuid_rep}" FechaTimbrado="2026-11-15T12:05:00" />
    </cfdi:Complemento>
</cfdi:Comprobante>"""

        parsed_rep = parse_cfdi_xml(rep_xml_content.encode("utf-8"), mi_rfc=test_rfc)
        assert parsed_rep["tipo"] == "INGRESO"
        assert parsed_rep["total"] == 116000.0
        assert "Pago recibido" in parsed_rep["conceptos_resumen"]
        assert "(Ingreso)" in parsed_rep["conceptos_resumen"]
        assert len(parsed_rep["doctos_relacionados"]) == 1

        inv_rep = CFDIInvoice(
            uuid=uuid_rep,
            account_rfc=test_rfc,
            area_proyecto="AMDI",
            tipo="INGRESO",
            rfc_emisor=test_rfc,
            nombre_emisor="ADRIANA MEDINA HERNANDEZ",
            rfc_receptor="CLI901010ABC",
            nombre_receptor="CLIENTE CORPORATIVO SA DE CV",
            fecha_emision=datetime(2026, 11, 15, 12, 0, 0),
            subtotal=100000.0,
            iva_trasladado=16000.0,
            total=116000.0,
            metodo_pago="PAGO",
            forma_pago="03",
            conceptos_resumen=parsed_rep["conceptos_resumen"],
            conciliado=False,
            comprobado=False,
            xml_raw=rep_xml_content
        )

        # 3. Transacción bancaria de Abono (INGRESO) en BBVA por $116,000
        tx_abono = BankTransaction(
            id_transaccion=tx_id,
            account_rfc=test_rfc,
            banco="BBVA",
            fecha=datetime(2026, 11, 15, 11, 30, 0),
            concepto="SPEI RECIBIDO CLIENTE CORPORATIVO PAGO FACT 001",
            monto=116000.0,
            saldo=250000.0,
            tipo="INGRESO",
            periodo_mes=test_month,
            status_conciliacion="SIN_CFDI"
        )

        db.add_all([inv_ppd, inv_rep, tx_abono])
        db.commit()

        # 4. Ejecutar conciliación pasante
        from app.api.dashboard.reconciliation_routes import _run_reconciliation_pass
        matches = _run_reconciliation_pass(db, effective_rfc=test_rfc, entity_name="AMDI", periodo_mes=test_month)
        assert matches >= 1

        # 5. Validar que la factura PPD se marcó como pagada con REP
        db.refresh(inv_ppd)
        db.refresh(inv_rep)
        db.refresh(tx_abono)

        assert inv_ppd.conciliado is True
        assert inv_ppd.comprobado is True
        assert inv_ppd.motivo_comprobacion == f"PAGADA_CON_REP:{uuid_rep}"
        assert inv_ppd.complemento_pago_uuid == uuid_rep

        assert tx_abono.status_conciliacion in ("CONCILIADO", "CONCILIADO_POR_REGLA")
        assert tx_abono.uuid_cfdi == uuid_rep
        assert "Pago recibido que ampara" in tx_abono.nota_revision
        assert "(Ingreso)" in tx_abono.nota_revision

        # 6. Consultar overview para el mes
        res = client.get(f"/api/dashboard/reconciliation/overview?account_rfc={test_rfc}&month={test_month}")
        assert res.status_code == 200
        k = res.json()["kpis"]

        # Validar que NO DUPLICA ingresos:
        # El total de ingresos facturados debe ser exactamente $116,000 (proveniente del REP cobrado),
        # y NO $232,000 (que sería duplicar PPD + REP).
        assert k["total_ingresos_facturados"] == 116000.0
        assert k["subtotal_ingresos_facturados"] == 100000.0
        assert k["iva_trasladado_ingresos"] == 16000.0
        assert k["count_ingresos_facturados"] == 1

        # 7. Validar endpoint de facturas para la UI
        res_invs = client.get(f"/api/dashboard/reconciliation/pending-invoices?account_rfc={test_rfc}&month={test_month}&include_reconciled=true&include_comprobados=true")
        assert res_invs.status_code == 200
        items = res_invs.json()
        ppd_item = next(i for i in items if i["uuid"] == uuid_ppd)
        assert ppd_item["is_pagada_rep"] is True
        assert ppd_item["status_pago"] == "PAGADA_CON_REP"
        assert ppd_item["complemento_pago_uuid"] == uuid_rep

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_([uuid_ppd, uuid_rep])).delete()
        db.query(BankTransaction).filter(BankTransaction.id_transaccion == tx_id).delete()
        db.commit()
        db.close()


def test_complemento_pago_ampara_multiples_facturas_ppd():
    """Valida que un Complemento de Pago que ampara múltiples facturas PPD las marque todas como pagadas sin duplicar."""
    db = SessionLocal()
    test_rfc = "MEHA850118Q96"
    test_month = "2026-12"

    uuid_ppd1 = "CFDI-TEST-PPD-MULTI-01"
    uuid_ppd2 = "CFDI-TEST-PPD-MULTI-02"
    uuid_rep = "CFDI-TEST-REP-MULTI-PAGO"
    tx_id = "tx_bbva_test_abono_multi_rep"

    try:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_([uuid_ppd1, uuid_ppd2, uuid_rep])).delete()
        db.query(BankTransaction).filter(BankTransaction.id_transaccion == tx_id).delete()
        db.commit()

        # 2 facturas PPD: $40,000 y $60,000 = $100,000 total
        inv_ppd1 = CFDIInvoice(
            uuid=uuid_ppd1,
            account_rfc=test_rfc,
            area_proyecto="AMDI",
            tipo="INGRESO",
            rfc_emisor=test_rfc,
            nombre_emisor="ADRIANA MEDINA HERNANDEZ",
            rfc_receptor="CLI901010ABC",
            fecha_emision=datetime(2026, 12, 1),
            subtotal=34482.76,
            iva_trasladado=5517.24,
            total=40000.0,
            metodo_pago="PPD",
            conciliado=False,
            comprobado=False
        )
        inv_ppd2 = CFDIInvoice(
            uuid=uuid_ppd2,
            account_rfc=test_rfc,
            area_proyecto="AMDI",
            tipo="INGRESO",
            rfc_emisor=test_rfc,
            nombre_emisor="ADRIANA MEDINA HERNANDEZ",
            rfc_receptor="CLI901010ABC",
            fecha_emision=datetime(2026, 12, 2),
            subtotal=51724.14,
            iva_trasladado=8275.86,
            total=60000.0,
            metodo_pago="PPD",
            conciliado=False,
            comprobado=False
        )

        rep_xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
    xmlns:pago20="http://www.sat.gob.mx/Pagos20"
    xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
    Version="4.0" Fecha="2026-12-10T12:00:00" Total="0" SubTotal="0" TipoDeComprobante="P">
    <cfdi:Emisor Rfc="{test_rfc}" Nombre="ADRIANA MEDINA HERNANDEZ" />
    <cfdi:Receptor Rfc="CLI901010ABC" Nombre="CLIENTE CORPORATIVO SA DE CV" />
    <cfdi:Complemento>
        <pago20:Pagos Version="2.0">
            <pago20:Totales MontoTotalPagos="100000.00" TotalTrasladosBaseIVA16="86206.90" TotalTrasladosImpuestoIVA16="13793.10" />
            <pago20:Pago FechaPago="2026-12-10T10:00:00" FormaDePagoP="03" MonedaP="MXN" Monto="100000.00">
                <pago20:DoctoRelacionado IdDocumento="{uuid_ppd1}" ImpPagado="40000.00" ImpSaldoAnt="40000.00" ImpSaldoInsoluto="0.00" NumParcialidad="1" />
                <pago20:DoctoRelacionado IdDocumento="{uuid_ppd2}" ImpPagado="60000.00" ImpSaldoAnt="60000.00" ImpSaldoInsoluto="0.00" NumParcialidad="1" />
            </pago20:Pago>
        </pago20:Pagos>
        <tfd:TimbreFiscalDigital UUID="{uuid_rep}" FechaTimbrado="2026-12-10T12:05:00" />
    </cfdi:Complemento>
</cfdi:Comprobante>"""

        parsed_rep = parse_cfdi_xml(rep_xml_content.encode("utf-8"), mi_rfc=test_rfc)
        assert len(parsed_rep["doctos_relacionados"]) == 2

        inv_rep = CFDIInvoice(
            uuid=uuid_rep,
            account_rfc=test_rfc,
            area_proyecto="AMDI",
            tipo="INGRESO",
            rfc_emisor=test_rfc,
            nombre_emisor="ADRIANA MEDINA HERNANDEZ",
            rfc_receptor="CLI901010ABC",
            nombre_receptor="CLIENTE CORPORATIVO SA DE CV",
            fecha_emision=datetime(2026, 12, 10),
            subtotal=86206.90,
            iva_trasladado=13793.10,
            total=100000.0,
            metodo_pago="PAGO",
            forma_pago="03",
            conceptos_resumen=parsed_rep["conceptos_resumen"],
            conciliado=False,
            comprobado=False,
            xml_raw=rep_xml_content
        )

        tx_abono = BankTransaction(
            id_transaccion=tx_id,
            account_rfc=test_rfc,
            banco="BBVA",
            fecha=datetime(2026, 12, 10),
            concepto="SPEI CLIENTE CORPORATIVO PAGO FACTURAS 01 Y 02",
            monto=100000.0,
            saldo=150000.0,
            tipo="INGRESO",
            periodo_mes=test_month,
            status_conciliacion="SIN_CFDI"
        )

        db.add_all([inv_ppd1, inv_ppd2, inv_rep, tx_abono])
        db.commit()

        from app.api.dashboard.reconciliation_routes import _run_reconciliation_pass
        matches = _run_reconciliation_pass(db, effective_rfc=test_rfc, entity_name="AMDI", periodo_mes=test_month)
        assert matches >= 1

        db.refresh(inv_ppd1)
        db.refresh(inv_ppd2)

        # Ambas deben estar marcadas como pagadas con REP
        assert inv_ppd1.conciliado is True
        assert inv_ppd1.motivo_comprobacion == f"PAGADA_CON_REP:{uuid_rep}"
        assert inv_ppd2.conciliado is True
        assert inv_ppd2.motivo_comprobacion == f"PAGADA_CON_REP:{uuid_rep}"

        # Consultar overview para validar no duplicidad
        res = client.get(f"/api/dashboard/reconciliation/overview?account_rfc={test_rfc}&month={test_month}")
        assert res.status_code == 200
        k = res.json()["kpis"]

        # Debe ser $100,000.0 (NO $200,000.0)
        assert k["total_ingresos_facturados"] == 100000.0
        assert k["count_ingresos_facturados"] == 1

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_([uuid_ppd1, uuid_ppd2, uuid_rep])).delete()
        db.query(BankTransaction).filter(BankTransaction.id_transaccion == tx_id).delete()
        db.commit()
        db.close()


def test_sync_all_complementos_de_pago_and_no_disponibles_para_justificar():
    """
    Valida el caso exacto reportado con Daltile:
    1. Dos facturas PPD en septiembre ($32,130 y $117,661.35)
    2. Un complemento de pago en octubre amparando ambas facturas
    3. Al consultar pending-invoices, las facturas quedan auto-sincronizadas,
       marcadas como PAGADA_CON_REP y NO disponibles como pendientes de justificar.
    """
    db = SessionLocal()
    test_rfc = "MEHA850118Q96"
    uuid_daltile_1 = "EF11BFCC-AB76-43C4-8759-3F350F9FB30C"
    uuid_daltile_2 = "2050DA55-A12F-470B-82F5-DA9FBB63583B"
    uuid_rep = "ED7867A9-B4DA-4C5E-96A6-A3AF2D3EFE0C"

    try:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_([uuid_daltile_1, uuid_daltile_2, uuid_rep])).delete()
        db.commit()

        # 1. Facturas PPD iniciales
        f1 = CFDIInvoice(
            uuid=uuid_daltile_1,
            account_rfc=test_rfc,
            area_proyecto="AMDI",
            tipo="INGRESO",
            rfc_emisor=test_rfc,
            nombre_emisor="ADRIANA MEDINA HERNANDEZ",
            rfc_receptor="DMC160901KV5",
            nombre_receptor="DAL-TILE MEXICO COMERCIAL",
            fecha_emision=datetime(2026, 9, 9),
            subtotal=28000.0,
            iva_trasladado=4480.0,
            retencion_isr=350.0,
            total=32130.0,
            metodo_pago="PPD",
            conciliado=False,
            comprobado=False
        )
        f2 = CFDIInvoice(
            uuid=uuid_daltile_2,
            account_rfc=test_rfc,
            area_proyecto="AMDI",
            tipo="INGRESO",
            rfc_emisor=test_rfc,
            nombre_emisor="ADRIANA MEDINA HERNANDEZ",
            rfc_receptor="DMC160901KV5",
            nombre_receptor="DAL-TILE MEXICO COMERCIAL",
            fecha_emision=datetime(2026, 9, 8),
            subtotal=101432.20,
            iva_trasladado=16229.15,
            total=117661.35,
            metodo_pago="PPD",
            conciliado=False,
            comprobado=False
        )
        # 2. Complemento de Pago en octubre con conceptos_resumen conteniendo los prefijos
        rep = CFDIInvoice(
            uuid=uuid_rep,
            account_rfc=test_rfc,
            area_proyecto="AMDI",
            tipo="INGRESO",
            rfc_emisor=test_rfc,
            nombre_emisor="ADRIANA MEDINA HERNANDEZ",
            rfc_receptor="DMC160901KV5",
            nombre_receptor="DAL-TILE MEXICO COMERCIAL",
            fecha_emision=datetime(2026, 10, 6),
            subtotal=128905.41,
            iva_trasladado=20885.94,
            total=149791.35,
            metodo_pago="PAGO",
            forma_pago="03",
            conceptos_resumen=f"Complemento de Pago ($149,791.35) ampara 2 factura(s): {uuid_daltile_1[:8]} ($32,130.00), {uuid_daltile_2[:8]} ($117,661.35)",
            conciliado=True,
            comprobado=False
        )
        db.add_all([f1, f2, rep])
        db.commit()

        # 3. Consultar pending-invoices sin include_reconciled (como lo hace el modal de vincular)
        res_pending = client.get(f"/api/dashboard/reconciliation/pending-invoices?account_rfc={test_rfc}&tipo=INGRESO")
        assert res_pending.status_code == 200
        pending_list = res_pending.json()
        pending_uuids = [p["uuid"] for p in pending_list]
        # NO deben aparecer como disponibles para vincular ni pendientes de banco
        assert uuid_daltile_1 not in pending_uuids
        assert uuid_daltile_2 not in pending_uuids

        # 4. Consultar con include_reconciled e include_comprobados (como el modal de buzón completo)
        res_all = client.get(f"/api/dashboard/reconciliation/pending-invoices?account_rfc={test_rfc}&include_reconciled=true&include_comprobados=true")
        assert res_all.status_code == 200
        all_items = {item["uuid"]: item for item in res_all.json()}

        assert uuid_daltile_1 in all_items
        assert uuid_daltile_2 in all_items
        assert all_items[uuid_daltile_1]["is_pagada_rep"] is True
        assert all_items[uuid_daltile_1]["status_pago"] == "PAGADA_CON_REP"
        assert all_items[uuid_daltile_1]["complemento_pago_uuid"] == uuid_rep

        assert all_items[uuid_daltile_2]["is_pagada_rep"] is True
        assert all_items[uuid_daltile_2]["status_pago"] == "PAGADA_CON_REP"
        assert all_items[uuid_daltile_2]["complemento_pago_uuid"] == uuid_rep

        # 5. Probar endpoint de sincronización explícito
        res_sync = client.post(f"/api/dashboard/reconciliation/sync-complementos-pago?account_rfc={test_rfc}")
        assert res_sync.status_code == 200
        assert res_sync.json()["success"] is True

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_([uuid_daltile_1, uuid_daltile_2, uuid_rep])).delete()
        db.commit()
        db.close()


def test_auto_reconcile_cash_expenses():
    """
    Valida que todas las facturas de egreso con forma de pago en efectivo ('01')
    se concilien y amparen automáticamente como 'Pago efectivo', quedando excluidas
    de las facturas pendientes de conciliar con el banco.
    """
    from app.services.reconciliation.mail_listener import auto_reconcile_cash_expenses

    db = SessionLocal()
    test_rfc = "DEGF851127TK1"
    uuid_cash_1 = "TEST-CASH-EGRESO-001"
    uuid_cash_2 = "TEST-CASH-EGRESO-002"
    uuid_transf = "TEST-TRANSFER-EGRESO-003"

    try:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_([uuid_cash_1, uuid_cash_2, uuid_transf])).delete()
        db.commit()

        # 1. Factura en efectivo sin conciliar
        f_cash1 = CFDIInvoice(
            uuid=uuid_cash_1,
            account_rfc=test_rfc,
            area_proyecto="HiphaMX",
            tipo="EGRESO",
            rfc_emisor="GAS990101XYZ",
            nombre_emisor="GASOLINERA TEST",
            rfc_receptor=test_rfc,
            nombre_receptor="HIPHA",
            fecha_emision=datetime(2026, 10, 5),
            subtotal=500.0,
            iva_trasladado=80.0,
            total=580.0,
            metodo_pago="PUE",
            forma_pago="01",
            conciliado=False,
            comprobado=False
        )

        # 2. Factura en efectivo con texto descriptivo
        f_cash2 = CFDIInvoice(
            uuid=uuid_cash_2,
            account_rfc=test_rfc,
            area_proyecto="HiphaMX",
            tipo="EGRESO",
            rfc_emisor="OXX990101XYZ",
            nombre_emisor="CADENA COMERCIAL TEST",
            rfc_receptor=test_rfc,
            nombre_receptor="HIPHA",
            fecha_emision=datetime(2026, 10, 6),
            subtotal=100.0,
            iva_trasladado=16.0,
            total=116.0,
            metodo_pago="PUE",
            forma_pago="01 - Efectivo",
            conciliado=False,
            comprobado=False
        )

        # 3. Factura por transferencia (NO debe conciliarse automáticamente como efectivo)
        f_transf = CFDIInvoice(
            uuid=uuid_transf,
            account_rfc=test_rfc,
            area_proyecto="HiphaMX",
            tipo="EGRESO",
            rfc_emisor="TEL990101XYZ",
            nombre_emisor="TELEFONIA TEST",
            rfc_receptor=test_rfc,
            nombre_receptor="HIPHA",
            fecha_emision=datetime(2026, 10, 7),
            subtotal=1000.0,
            iva_trasladado=160.0,
            total=1160.0,
            metodo_pago="PUE",
            forma_pago="03",
            conciliado=False,
            comprobado=False
        )

        db.add_all([f_cash1, f_cash2, f_transf])
        db.commit()

        # Ejecutar auto-conciliación
        reconciled_cnt = auto_reconcile_cash_expenses(db, test_rfc)
        assert reconciled_cnt >= 2

        # Validar en DB
        inv1 = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_cash_1).first()
        assert inv1.conciliado is True
        assert inv1.comprobado is True
        assert inv1.motivo_comprobacion == "Pago efectivo"

        inv2 = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_cash_2).first()
        assert inv2.conciliado is True
        assert inv2.comprobado is True
        assert inv2.motivo_comprobacion == "Pago efectivo"

        inv3 = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_transf).first()
        assert inv3.conciliado is False
        assert inv3.comprobado is False

        # Validar endpoint de facturas pendientes (no debe listar las de efectivo si include_reconciled=False)
        res = client.get(f"/api/dashboard/reconciliation/pending-invoices?account_rfc={test_rfc}&include_reconciled=false&include_comprobados=false")
        assert res.status_code == 200
        uuids_pending = [item["uuid"] for item in res.json()]
        assert uuid_cash_1 not in uuids_pending
        assert uuid_cash_2 not in uuids_pending
        assert uuid_transf in uuids_pending

        # Validar que si include_comprobados=True se listan y contienen forma_pago y metodo_pago
        res_all = client.get(f"/api/dashboard/reconciliation/pending-invoices?account_rfc={test_rfc}&include_reconciled=true&include_comprobados=true")
        assert res_all.status_code == 200
        items_map = {item["uuid"]: item for item in res_all.json()}
        assert items_map[uuid_cash_1]["forma_pago"] == "01"
        assert items_map[uuid_cash_1]["motivo_comprobacion"] == "Pago efectivo"

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid.in_([uuid_cash_1, uuid_cash_2, uuid_transf])).delete()
        db.commit()
        db.close()


def test_reclassify_invoices_by_fiscal_rfc():
    """
    Valida que los comprobantes recibidos con un account_rfc incorrecto (ej. EXPO OBRA BLANCA
    recibido en el correo de Hipha pero con receptor fiscal de AMDI) sean reclasificados
    automáticamente a su cuenta fiscal real (MEHA850118Q96 / AMDI).
    """
    from app.services.reconciliation.mail_listener import reclassify_invoices_by_fiscal_rfc

    db = SessionLocal()
    uuid_obra_blanca_test = "B5B1A683-A5D5-4509-B007-3BDA15D4B06F-TEST"

    try:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_obra_blanca_test).delete()
        db.commit()

        # Simular factura de Obra Blanca guardada erróneamente en Hipha
        inv_wrong = CFDIInvoice(
            uuid=uuid_obra_blanca_test,
            account_rfc="DEGF851127TK1",  # Guardado erróneamente en Hipha
            area_proyecto="HiphaMX",
            tipo="EGRESO",
            rfc_emisor="EOB181101831",
            nombre_emisor="EXPO OBRA BLANCA",
            rfc_receptor="MEHA850118Q96",  # Receptor real es AMDI
            nombre_receptor="ADRIANA MEDINA HERNANDEZ",
            fecha_emision=datetime(2026, 10, 11),
            subtotal=396.55,
            iva_trasladado=63.45,
            total=460.0,
            metodo_pago="PUE",
            forma_pago="04",
            conceptos_resumen="Acceso al EVENTO OBRA BLANCA 2026",
            conciliado=False,
            comprobado=False
        )
        db.add(inv_wrong)
        db.commit()

        # Ejecutar reclasificación
        reclassified = reclassify_invoices_by_fiscal_rfc(db)
        assert reclassified >= 1

        # Verificar en DB que ahora pertenece a AMDI
        inv_fixed = db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_obra_blanca_test).first()
        assert inv_fixed.account_rfc == "MEHA850118Q96"
        assert inv_fixed.area_proyecto == "AMDI"

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == uuid_obra_blanca_test).delete()
        db.commit()
        db.close()


def test_split_payments_match_single_cfdi():
    """Valida que múltiples depósitos que en conjunto liquidan una factura o Complemento de Pago (ej. Tukipa $2,770 + $443.20 = $3,213.20) se concilien automáticamente."""
    from app.services.reconciliation.matching_engine import conciliar_movimientos

    txs = [
        {
            "id": 101,
            "id_transaccion": "tx_split_1",
            "fecha": "2026-08-28",
            "concepto": "PAGO CUENTA DE TERCERO - 0001699927 BNET 2744866398 Tukipa Marqueting",
            "monto": 2770.0,
            "tipo": "INGRESO",
            "banco": "BBVA",
            "area_proyecto": "HIPHA"
        },
        {
            "id": 102,
            "id_transaccion": "tx_split_2",
            "fecha": "2026-08-28",
            "concepto": "PAGO CUENTA DE TERCERO - 0091687735 BNET 2744866398 iva tukipa marketi",
            "monto": 443.20,
            "tipo": "INGRESO",
            "banco": "BBVA",
            "area_proyecto": "HIPHA"
        }
    ]

    facturas = [
        {
            "uuid": "REP-TUKIPA-3213-UUID",
            "tipo": "INGRESO",
            "rfc_emisor": "DEGF851127TK1",
            "nombre_emisor": "FRANCISCO DE JESUS DELGADILLO GARCIA",
            "rfc_receptor": "MEHA870222DY4",
            "nombre_receptor": "ABEL ALEJANDRO MEDINA HERNANDEZ",
            "fecha_emision": "2026-08-28",
            "subtotal": 2770.0,
            "iva": 443.20,
            "total": 3213.20,
            "metodo_pago": "PAGO",
            "conceptos_resumen": "Pago recibido de $3,213.20",
            "doctos_relacionados": []
        }
    ]

    resultados = conciliar_movimientos(txs, facturas)
    assert len(resultados) == 2
    assert resultados[0]["status_conciliacion"] == "CONCILIADO"
    assert resultados[0]["uuid_cfdi"] == "REP-TUKIPA-3213-UUID"
    assert resultados[1]["status_conciliacion"] == "CONCILIADO"
    assert resultados[1]["uuid_cfdi"] == "REP-TUKIPA-3213-UUID"


def test_search_pending_invoices_by_folio():
    """
    Valida que el endpoint /pending-invoices permita buscar por folio y serie (ej. 'F-176' o '176')
    y retorne la propiedad 'folio' extraída del comprobante.
    """
    db = SessionLocal()
    test_uuid = "FOLIO-TEST-UUID-714038B0-176"
    test_rfc = "DEGF851127TK1"

    try:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == test_uuid).delete()
        db.commit()

        inv = CFDIInvoice(
            uuid=test_uuid,
            account_rfc=test_rfc,
            tipo="INGRESO",
            rfc_emisor=test_rfc,
            nombre_emisor="FRANCISCO DE JESUS DELGADILLO GARCIA",
            rfc_receptor="GAC260318SD7",
            nombre_receptor="GRUPO AXIS COMERCIAL",
            fecha_emision=datetime(2026, 6, 27, 9, 10),
            subtotal=4190.48,
            iva_trasladado=670.48,
            retencion_isr=52.38,
            retencion_iva=446.98,
            total=4361.60,
            metodo_pago="PUE",
            forma_pago="03",
            conceptos_resumen="[F-176] Consultoría en marketing estratégico",
            conciliado=False,
            comprobado=False,
            xml_raw='<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Serie="F" Folio="176" Total="4361.60"></cfdi:Comprobante>'
        )
        db.add(inv)
        db.commit()

        # 1. Búsqueda por folio compuesto: "F-176"
        res_folio_full = client.get(f"/api/dashboard/reconciliation/pending-invoices?account_rfc={test_rfc}&search=F-176")
        assert res_folio_full.status_code == 200
        items = res_folio_full.json()
        assert any(it["uuid"] == test_uuid for it in items)
        target = next(it for it in items if it["uuid"] == test_uuid)
        assert target["folio"] == "F-176"

        # 2. Búsqueda por número de folio simple: "176"
        res_folio_num = client.get(f"/api/dashboard/reconciliation/pending-invoices?account_rfc={test_rfc}&search=176")
        assert res_folio_num.status_code == 200
        assert any(it["uuid"] == test_uuid for it in res_folio_num.json())

    finally:
        db.query(CFDIInvoice).filter(CFDIInvoice.uuid == test_uuid).delete()
        db.commit()
        db.close()


def test_parse_bank_pdf_statement_invex_credit_card():
    from app.services.reconciliation.pdf_parser import parse_bank_pdf_statement

    with open("tests/fixtures/Invex_septiembre_2026.pdf", "rb") as f:
        pdf_bytes = f.read()

    txs = parse_bank_pdf_statement(pdf_bytes, "Invex_septiembre_2026.pdf", account_rfc="MEHA850118Q96")
    assert len(txs) == 30

    # Banco y entidad asociada
    for t in txs:
        assert t["banco"] == "TC INVEX"
        assert t["account_rfc"] == "MEHA850118Q96"
        assert t["periodo_mes"] == "2026-09"

    # Sumas de control exactas del estado de cuenta
    total_cargos = sum(t["monto"] for t in txs if t["tipo"] == "EGRESO")
    total_abonos = sum(t["monto"] for t in txs if t["tipo"] == "INGRESO")
    assert total_cargos == pytest.approx(59275.05, 0.01)
    assert total_abonos == pytest.approx(13597.00, 0.01)

    # Identificación de plásticos (Titular y Digital)
    conceptos = [t["concepto"] for t in txs]
    assert any("[Tarjeta Titular 1330]" in c for c in conceptos)
    assert any("[Tarjeta Digital 2569]" in c for c in conceptos)

    # Pago de tarjeta clasificado como traspaso propio (NO_APLICA)
    pago = next(t for t in txs if "SU PAGO POR SPEI" in t["concepto"])
    assert pago["status_conciliacion"] == "NO_APLICA"
    assert pago["confianza_score"] == 1.0
    assert "Pago de Tarjeta" in pago["nota_revision"] or "Traspaso Propio" in pago["nota_revision"]


def test_invex_reconciliation_matching():
    from app.services.reconciliation.pdf_parser import parse_bank_pdf_statement
    from app.services.reconciliation.matching_engine import conciliar_movimientos

    with open("tests/fixtures/Invex_septiembre_2026.pdf", "rb") as f:
        pdf_bytes = f.read()

    txs = parse_bank_pdf_statement(pdf_bytes, "Invex_septiembre_2026.pdf", account_rfc="MEHA850118Q96")

    # CFDIs simulados correspondientes a los gastos de tarjeta en Septiembre 2026
    facturas_mock = [
        {
            "uuid": "FB8D1374-1111-2222-3333-444444444444",
            "tipo": "EGRESO",
            "rfc_emisor": "CACX880324IAA",
            "nombre_emisor": "ANA GABRIELA CASTELLANOS CERDA",
            "rfc_receptor": "MEHA850118Q96",
            "nombre_receptor": "ADRIANA MEDINA HERNANDEZ",
            "fecha_emision": datetime(2026, 9, 22, 12, 0),
            "total": 10712.16,
            "metodo_pago": "PUE",
            "forma_pago": "04",
            "doctos_relacionados": []
        },
        {
            "uuid": "5BE4116B-1111-2222-3333-444444444444",
            "tipo": "EGRESO",
            "rfc_emisor": "CACX880324IAA",
            "nombre_emisor": "ANA GABRIELA CASTELLANOS CERDA",
            "rfc_receptor": "MEHA850118Q96",
            "nombre_receptor": "ADRIANA MEDINA HERNANDEZ",
            "fecha_emision": datetime(2026, 9, 25, 12, 0),
            "total": 2752.81,
            "metodo_pago": "PUE",
            "forma_pago": "04",
            "doctos_relacionados": []
        },
        {
            "uuid": "35BE005C-1111-2222-3333-444444444444",
            "tipo": "EGRESO",
            "rfc_emisor": "PAR050922GK3",
            "nombre_emisor": "PLURAL ARQUITECTURA",
            "rfc_receptor": "MEHA850118Q96",
            "nombre_receptor": "ADRIANA MEDINA HERNANDEZ",
            "fecha_emision": datetime(2026, 9, 24, 12, 0),
            "total": 19106.12,
            "metodo_pago": "PUE",
            "forma_pago": "04",
            "doctos_relacionados": []
        },
        {
            "uuid": "15E0390A-1111-2222-3333-444444444444",
            "tipo": "EGRESO",
            "rfc_emisor": "HDM001017AS1",
            "nombre_emisor": "HOME DEPOT MEXICO",
            "rfc_receptor": "MEHA850118Q96",
            "nombre_receptor": "ADRIANA MEDINA HERNANDEZ",
            "fecha_emision": datetime(2026, 9, 26, 12, 0),
            "total": 3332.00,
            "metodo_pago": "PUE",
            "forma_pago": "04",
            "doctos_relacionados": []
        }
    ]

    matched = conciliar_movimientos(txs, facturas_mock)

    # 1. Pago de Tarjeta debe ser NO_APLICA
    pago = next(m for m in matched if "SU PAGO POR SPEI" in m["concepto"])
    assert pago["status_conciliacion"] == "NO_APLICA"
    assert pago["confianza_score"] == 1.0

    # 2. Las 4 facturas deben coincidir con Tier 2 por regla comercial (CONCILIADO_POR_REGLA)
    ferremate_1 = next(m for m in matched if abs(m["monto"] - 10712.16) <= 0.01)
    assert ferremate_1["status_conciliacion"] in ("CONCILIADO", "CONCILIADO_POR_REGLA")
    assert ferremate_1["uuid_cfdi"] == "FB8D1374-1111-2222-3333-444444444444"
    assert ferremate_1["confianza_score"] in (0.95, 1.0)

    ferremate_2 = next(m for m in matched if abs(m["monto"] - 2752.81) <= 0.01)
    assert ferremate_2["status_conciliacion"] in ("CONCILIADO", "CONCILIADO_POR_REGLA")
    assert ferremate_2["uuid_cfdi"] == "5BE4116B-1111-2222-3333-444444444444"
    assert ferremate_2["confianza_score"] in (0.95, 1.0)

    plural = next(m for m in matched if abs(m["monto"] - 19106.12) <= 0.01)
    assert plural["status_conciliacion"] in ("CONCILIADO", "CONCILIADO_POR_REGLA")
    assert plural["uuid_cfdi"] == "35BE005C-1111-2222-3333-444444444444"
    assert plural["confianza_score"] in (0.95, 1.0)

    home_depot = next(m for m in matched if abs(m["monto"] - 3332.00) <= 0.01)
    assert home_depot["status_conciliacion"] in ("CONCILIADO", "CONCILIADO_POR_REGLA")
    assert home_depot["uuid_cfdi"] == "15E0390A-1111-2222-3333-444444444444"
    assert home_depot["confianza_score"] in (0.95, 1.0)


def test_get_monthly_flow_summary_endpoint():
    # Probar endpoint para AMDI en Septiembre 2026
    res = client.get("/api/dashboard/reconciliation/monthly-flow-summary?account_rfc=MEHA850118Q96&month=2026-09")
    assert res.status_code == 200
    data = res.json()

    assert data["month"] == "2026-09"
    assert data["entity"]["name"] == "AMDI"
    assert data["entity"]["rfc"] == "MEHA850118Q96"
    assert "Septiembre 2026" in data["month_label"]

    # Total de facturas
    assert data["total_facturas"]["count"] == 19
    assert data["total_facturas"]["monto"] == pytest.approx(58615.83, 0.01)

    # Facturas pagadas con TC Invex
    assert data["pagadas_tc_invex"]["count"] == 4
    assert data["pagadas_tc_invex"]["monto"] == pytest.approx(35903.09, 0.01)
    invex_uuids = [inv["uuid"] for inv in data["pagadas_tc_invex"]["invoices"]]
    assert any("FB8D1374" in u for u in invex_uuids)
    assert any("35BE005C" in u for u in invex_uuids)

    # Facturas pagadas en efectivo
    assert data["pagadas_efectivo"]["count"] == 10
    assert data["pagadas_efectivo"]["monto"] == pytest.approx(9938.72, 0.01)

    # Facturas pendientes de comprobar
    assert data["pendientes_comprobacion"]["count"] == 5
    assert data["pendientes_comprobacion"]["monto"] == pytest.approx(12774.02, 0.01)

    # Cargos bancarios sin CFDI
    assert data["banco_sin_cfdi"]["count"] >= 20

    # Probar validación de mes inválido
    bad_res = client.get("/api/dashboard/reconciliation/monthly-flow-summary?account_rfc=MEHA850118Q96&month=invalid-date")
    assert bad_res.status_code == 400


def test_cascada_scoring_nivel_1_match_exacto_determinista():
    """Nivel 1: Match Exacto (Determinista) con mismo monto, folio/referencia y fecha dentro de +-3 días."""
    factura = {
        "uuid": "11112222-3333-4444-5555-666677778888",
        "tipo": "INGRESO",
        "rfc_receptor": "CLI901010ABC",
        "nombre_receptor": "CLIENTE EJEMPLO SA DE CV",
        "fecha_emision": "2026-10-15",
        "total": 15000.00,
        "serie": "F",
        "folio": "205",
        "conceptos_resumen": "[F-205] Consultoría en estrategia de marca"
    }

    transaccion = {
        "id": 501,
        "id_transaccion": "TX-N1-001",
        "fecha": "2026-10-16",  # +1 día
        "concepto": "SPEI RECIBIDO CLIENTE PAGO FACTURA F-205 REF 88129",
        "monto": 15000.00,
        "tipo": "INGRESO",
        "banco": "BBVA"
    }

    reconciled = conciliar_movimientos([transaccion], [factura])
    assert len(reconciled) == 1
    res = reconciled[0]
    assert res["status_conciliacion"] == "CONCILIADO_DIRECTO"
    assert res["confianza_score"] == 1.0
    assert res["uuid_cfdi"] == "11112222-3333-4444-5555-666677778888"
    assert "F-205" in res["nota_revision"] or "205" in res["nota_revision"]


def test_cascada_scoring_nivel_2_match_fuzzy_1_a_1():
    """Nivel 2: Match Fuzzy (1 a 1) por razón social / alias comercial y RFC, sin referencia explícita."""
    factura = {
        "uuid": "22223333-4444-5555-6666-777788889999",
        "tipo": "EGRESO",
        "rfc_emisor": "BCH150912ABC",
        "nombre_emisor": "BIOZONE CHEMICAL SA DE CV",
        "fecha_emision": "2026-10-10",
        "total": 4850.00,
        "serie": "A",
        "folio": "999",  # Folio no aparece en el concepto bancario
        "conceptos_resumen": "Insumos químicos de limpieza"
    }

    transaccion = {
        "id": 502,
        "id_transaccion": "TX-N2-001",
        "fecha": "2026-10-20",  # +10 días (ventana comercial válida)
        "concepto": "COMPRA TPV ULTRAKLIN GUADALAJARA JAL",  # ULTRAKLIN es alias en TRADE_NAME_ALIASES
        "monto": 4850.00,
        "tipo": "EGRESO",
        "banco": "TC INVEX"
    }

    reconciled = conciliar_movimientos([transaccion], [factura])
    assert len(reconciled) == 1
    res = reconciled[0]
    assert res["status_conciliacion"] == "CONCILIADO_POR_REGLA"
    assert res["confianza_score"] == 0.95
    assert res["uuid_cfdi"] == "22223333-4444-5555-6666-777788889999"
    assert "regla comercial" in res["nota_revision"].lower()


def test_cascada_scoring_nivel_3_match_complejo_univoco_y_ambiguo():
    """Nivel 3: Match Complejo N:1. Unívoco -> CONCILIADO (1.0). Ambiguo -> POR_REVISAR (0.7)."""
    # 1. Caso Unívoco (1 combinación matemática posible)
    facturas_univocas = [
        {
            "uuid": "CFDI-COMB-01",
            "tipo": "INGRESO",
            "rfc_receptor": "DME950316G28",
            "nombre_receptor": "DAL-TILE MEXICO",
            "fecha_emision": "2026-10-01",
            "total": 6000.00
        },
        {
            "uuid": "CFDI-COMB-02",
            "tipo": "INGRESO",
            "rfc_receptor": "DME950316G28",
            "nombre_receptor": "DAL-TILE MEXICO",
            "fecha_emision": "2026-10-02",
            "total": 4000.00
        }
    ]

    tx_univoca = {
        "id": 503,
        "id_transaccion": "TX-N3-UNIVOCO",
        "fecha": "2026-10-05",
        "concepto": "DEPOSITO SPEI DAL-TILE MEXICO LIQUIDACION 2 FACTURAS",
        "monto": 10000.00,
        "tipo": "INGRESO",
        "banco": "BBVA"
    }

    res_u = conciliar_movimientos([tx_univoca], facturas_univocas)[0]
    assert res_u["status_conciliacion"] == "CONCILIADO"
    assert res_u["confianza_score"] == 1.0
    assert set(res_u["related_cfdi_uuids"]) == {"CFDI-COMB-01", "CFDI-COMB-02"}
    assert "unívoco" in res_u["nota_revision"].lower()

    # 2. Caso Ambiguo (Múltiples combinaciones posibles de igual importe)
    facturas_ambiguas = [
        {
            "uuid": "CFDI-AMB-01",
            "tipo": "INGRESO",
            "rfc_receptor": "DME950316G28",
            "nombre_receptor": "DAL-TILE MEXICO",
            "fecha_emision": "2026-10-01",
            "total": 3000.00
        },
        {
            "uuid": "CFDI-AMB-02",
            "tipo": "INGRESO",
            "rfc_receptor": "DME950316G28",
            "nombre_receptor": "DAL-TILE MEXICO",
            "fecha_emision": "2026-10-02",
            "total": 3000.00
        },
        {
            "uuid": "CFDI-AMB-03",
            "tipo": "INGRESO",
            "rfc_receptor": "DME950316G28",
            "nombre_receptor": "DAL-TILE MEXICO",
            "fecha_emision": "2026-10-03",
            "total": 2000.00
        }
    ]

    tx_ambigua = {
        "id": 504,
        "id_transaccion": "TX-N3-AMBIGUO",
        "fecha": "2026-10-05",
        "concepto": "DEPOSITO SPEI DAL-TILE MEXICO LIQUIDACION PARCIAL",
        "monto": 5000.00,  # Se puede formar con (AMB-01 + AMB-03) o (AMB-02 + AMB-03)
        "tipo": "INGRESO",
        "banco": "BBVA"
    }

    res_a = conciliar_movimientos([tx_ambigua], facturas_ambiguas)[0]
    assert res_a["status_conciliacion"] == "POR_REVISAR"
    assert res_a["confianza_score"] == 0.70
    assert "ambiguo" in res_a["nota_revision"].lower()


def test_cascada_scoring_nivel_4_discrepancias_y_huerfanos():
    """Nivel 4: Discrepancias y Huérfanos. Auto-clasificación fiscal/traspasos (NO_APLICA) y comisiones/gastos (SIN_CFDI)."""
    transacciones = [
        {
            "id": 505,
            "id_transaccion": "TX-N4-SIPARE",
            "fecha": "2026-10-17",
            "concepto": "PAGO SIPARE IMSS AFORE 0019284",
            "monto": 12500.00,
            "tipo": "EGRESO",
            "banco": "BBVA"
        },
        {
            "id": 506,
            "id_transaccion": "TX-N4-COMISION",
            "fecha": "2026-10-31",
            "concepto": "COMISION POR TRANSFERENCIA INTERBANCARIA",
            "monto": 5.80,
            "tipo": "EGRESO",
            "banco": "BBVA"
        },
        {
            "id": 507,
            "id_transaccion": "TX-N4-GASTO-SIN-CFDI",
            "fecha": "2026-10-22",
            "concepto": "COMPRA EN TIENDA LOCAL DE CONVENIENCIA",
            "monto": 145.00,
            "tipo": "EGRESO",
            "banco": "BBVA"
        }
    ]

    reconciled = conciliar_movimientos(transacciones, [])
    assert len(reconciled) == 3

    # SIPARE -> NO_APLICA (1.0)
    tx_sipare = next(t for t in reconciled if t["id_transaccion"] == "TX-N4-SIPARE")
    assert tx_sipare["status_conciliacion"] == "NO_APLICA"
    assert tx_sipare["confianza_score"] == 1.0

    # Comisión -> SIN_CFDI con nota de comisión
    tx_com = next(t for t in reconciled if t["id_transaccion"] == "TX-N4-COMISION")
    assert tx_com["status_conciliacion"] == "SIN_CFDI"
    assert "comisión" in tx_com["nota_revision"].lower() or "bancario" in tx_com["nota_revision"].lower()

    # Gasto sin factura -> SIN_CFDI para bandeja de excepciones
    tx_gasto = next(t for t in reconciled if t["id_transaccion"] == "TX-N4-GASTO-SIN-CFDI")
    assert tx_gasto["status_conciliacion"] == "SIN_CFDI"
    assert "sin cfdi" in tx_gasto["nota_revision"].lower()















