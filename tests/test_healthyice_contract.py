import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthyice_contract_generation_normal():
    # Test generation with full info filled out
    payload = {
        "nombre": "JUAN PÉREZ",
        "razon_social": "DISTRIBUIDORA DEL CENTRO S.A. DE C.V.",
        "rfc": "DCE123456HG7",
        "domicilio": "AV. PATRIA 1234, ZAPOPAN, JALISCO",
        "email": "juan@distribuidora.com",
        "telefono": "3312345678",
        "tipo_alianza": "Punto de Venta",
        "firma": "",
        "fecha": "15 DE JUNIO DE 2026",
        "nombre_establecimiento": "HELADOS GABY",
        "esquema_comercial": "COMPRA DIRECTA",
        "esquema_comercial_otro": "",
        "frecuencia_pagos": "SEMANAL",
        "metodo_pago": "TRANSFERENCIA BANCARIA",
        "metodo_pago_otro": "",
        "vigencia_meses": 12,
        "fecha_inicio_dia": 15,
        "fecha_inicio_mes": "JUNIO",
        "fecha_inicio_anio": 2026,
        "ciudad_jurisdiccion": "GUADALAJARA, JALISCO",
        "representante_healthyice": "FRANCISCO DELGADILLO",
        "llenado_manual": False
    }
    
    response = client.post("/api/contact/healthyice/contract", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=Contrato_HealthyIce_DISTRIBUIDORA_DEL_CENTRO_S.A._DE_C.V..pdf" in response.headers["content-disposition"]
    assert len(response.content) > 10000

def test_healthyice_contract_generation_manual():
    # Test generation with manual print enabled (most fields omitted/None)
    payload = {
        "llenado_manual": True
    }
    
    response = client.post("/api/contact/healthyice/contract", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=Contrato_HealthyIce_Formato_Manual.pdf" in response.headers["content-disposition"]
    assert len(response.content) > 10000
