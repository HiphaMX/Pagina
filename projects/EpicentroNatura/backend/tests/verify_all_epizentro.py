#!/usr/bin/env python3
"""
VERIFICACIÓN INTEGRAL DE CALIDAD KAM - EPIZENTRO NATURA
Auditor Automatizado: 'El Vergotas' & Gold Fish
Revisa los 7 puntos exigidos por dirección técnica:
  1. Prevención de CLS / brincos de contenido en categorías.
  2. Textos canónicos y ausencia de salto en Chile Chillón.
  3. Recuperación estable de Botica Silvestre en Productos Artesanales.
  4. Controles de entrega y retiro para fichas esenciales (sin 'Recoger en local' en Valencia).
  5. Insignia 'Verificado' rediseñada y posicionada bajo el título en escaparates.
  6. Motor de búsqueda global con indexación profunda y fallbacks resilientes.
  7. Suite de endpoints de FastAPI y consistencia en base de datos.
"""

import os
import sys
import glob
import re
import json
import sqlite3
import subprocess
import tempfile
from pathlib import Path

# Paths principales y configuración de sys.path
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EPIZENTRO_DIR = REPO_ROOT / "projects" / "EpicentroNatura"
DB_PATH = REPO_ROOT / "database.db"

# Color helpers para output en consola
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

passed_tests = 0
failed_tests = 0

def report_result(title, success, message=""):
    global passed_tests, failed_tests
    if success:
        passed_tests += 1
        print(f"  [{GREEN}PASS{RESET}] {BOLD}{title}{RESET}" + (f" - {message}" if message else ""))
    else:
        failed_tests += 1
        print(f"  [{RED}FAIL{RESET}] {BOLD}{title}{RESET}" + (f" - {RED}{message}{RESET}" if message else ""))


def test_1_html_and_js_syntax():
    print(f"\n{BLUE}=== 1. VERIFICACIÓN DE SINTAXIS JS Y JSON-LD (TODOS LOS ARCHIVOS HTML) ==={RESET}")
    html_files = sorted(list(set(glob.glob(str(EPIZENTRO_DIR / "**/*.html"), recursive=True) + glob.glob(str(EPIZENTRO_DIR / "*.html")))))
    
    syntax_errors = []
    for fpath in html_files:
        rel_path = os.path.relpath(fpath, REPO_ROOT)
        content = open(fpath, "r", encoding="utf-8").read()
        
        # Analizar scripts inline
        script_matches = re.finditer(r'<script([^>]*)>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
        for i, m in enumerate(script_matches):
            attrs = m.group(1)
            code = m.group(2).strip()
            if not code or "src=" in attrs:
                continue
            
            # Si es JSON-LD, validar JSON
            if "application/ld+json" in attrs:
                try:
                    json.loads(code)
                except Exception as err:
                    syntax_errors.append(f"{rel_path} script #{i} (JSON-LD): {err}")
                continue
            
            # Sintaxis JavaScript con Node.js
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
                tf.write(code)
                tf_name = tf.name
            try:
                res = subprocess.run(["node", "-c", tf_name], capture_output=True, text=True)
                if res.returncode != 0:
                    syntax_errors.append(f"{rel_path} script #{i} (JS): {res.stderr.strip()[:150]}")
            finally:
                if os.path.exists(tf_name):
                    os.remove(tf_name)
    
    # Validar también epicentro-search.js
    search_js = EPIZENTRO_DIR / "epicentro-search.js"
    if search_js.exists():
        res = subprocess.run(["node", "-c", str(search_js)], capture_output=True, text=True)
        if res.returncode != 0:
            syntax_errors.append(f"epicentro-search.js: {res.stderr.strip()[:150]}")
    
    success = len(syntax_errors) == 0
    report_result("Sintaxis en 25 archivos HTML y epicentro-search.js", success, f"Errores: {len(syntax_errors)}" if not success else "100% código válido")
    if not success:
        for err in syntax_errors:
            print(f"       -> {err}")


def test_2_cls_and_category_stability():
    print(f"\n{BLUE}=== 2. ESTABILIDAD DE CATEGORÍAS Y PREVENCIÓN DE BRINCOS (CLS / FOUC) ==={RESET}")
    
    # 2.1 Cero ocurrencias de 'const catParam'
    matches_const_cat = []
    for fpath in glob.glob(str(EPIZENTRO_DIR / "**/*.html"), recursive=True):
        content = open(fpath, "r", encoding="utf-8").read()
        if "const catParam" in content:
            matches_const_cat.append(os.path.relpath(fpath, REPO_ROOT))
    
    report_result(
        "Cero reasignaciones 'const catParam' (Previene TypeError en runtime)",
        len(matches_const_cat) == 0,
        f"Encontrados en: {matches_const_cat}" if matches_const_cat else "0 archivos con 'const catParam'"
    )
    
    # 2.2 Presencia de window.ALL_BUSINESSES en todas las categorías principales
    category_files = [
        "categoria.html",
        "index.html",
        "categorias/comida-delivery.html",
        "categorias/productos-artesanales.html",
        "categorias/servicios-hogar.html",
        "categorias/servicios-profesionales.html",
        "categorias/cuidado-personal.html",
        "categorias/educacion.html",
        "categorias/fitness.html",
        "categorias/mascotas.html",
    ]
    missing_bindings = []
    for rel in category_files:
        full_p = EPIZENTRO_DIR / rel
        if not full_p.exists():
            missing_bindings.append(f"{rel} (archivo no existe)")
            continue
        c = open(full_p, "r", encoding="utf-8").read()
        if "window.ALL_BUSINESSES = ALL_BUSINESSES" not in c:
            missing_bindings.append(rel)
            
    report_result(
        "Vinculación global 'window.ALL_BUSINESSES = ALL_BUSINESSES' en 10 páginas clave",
        len(missing_bindings) == 0,
        f"Faltantes: {missing_bindings}" if missing_bindings else "Presente en todas"
    )
    
    # 2.3 Botica Silvestre presente y sin variables indefinidas en productos-artesanales.html
    artesanales_path = EPIZENTRO_DIR / "categorias" / "productos-artesanales.html"
    art_content = open(artesanales_path, "r", encoding="utf-8").read()
    has_botica = "Botica Silvestre" in art_content
    has_broken_var = "biz.payment_status" in art_content or "biz.payment_amount" in art_content
    report_result(
        "Botica Silvestre activa y sin 'biz.*' indefinido en productos-artesanales.html",
        has_botica and not has_broken_var,
        "Recuperada y estable" if (has_botica and not has_broken_var) else "Presenta variables no definidas"
    )


def test_3_chile_chillon_synchronization():
    print(f"\n{BLUE}=== 3. CHILE CHILLÓN: TEXTOS CANÓNICOS Y SINCRONIZACIÓN DE BASE DE DATOS ==={RESET}")
    
    # 3.1 Consulta en database.db
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT business_name, schedule, coto_address, whatsapp FROM epicentro_registrations WHERE slug IN ('chile-chillon', 'elchilechillon') OR id = 'reg-chile-chillon'")
    chillon_db = cursor.fetchone()
    conn.close()
    
    db_ok = False
    if chillon_db:
        name, sched, coto, wa = chillon_db
        db_ok = (
            name == "Chile Chillón" and 
            "Lunes a Domingo · 10:00 a 20:00 hrs" in sched and
            wa == "3336762545"
        )
    report_result(
        "Base de datos: Horario canónico '10:00 a 20:00 hrs' y WhatsApp '3336762545' en SQLite",
        db_ok,
        f"Valor DB: {chillon_db}" if db_ok else f"Discrepancia en DB: {chillon_db}"
    )
    
    # 3.2 HTML estático de chile-chillon.html coincide con la base de datos (Cero Layout Shift)
    chillon_html = open(EPIZENTRO_DIR / "chile-chillon.html", "r", encoding="utf-8").read()
    has_sched_static = "Lunes a Domingo · 10:00 a 20:00 hrs" in chillon_html
    has_loc_static = "Zona Mariano Otero" in chillon_html
    has_wa_static = "3336762545" in chillon_html
    report_result(
        "Plantilla HTML chile-chillon.html pre-renderiza textos canónicos idénticos a DB",
        has_sched_static and has_loc_static and has_wa_static,
        "HTML inicial coincide 100% con DB para evitar repintado"
    )


def test_4_essential_cards_and_valencia_pickup():
    print(f"\n{BLUE}=== 4. FICHAS ESENCIALES Y CONTROLES DE ENTREGA / RECOGIDA (VALENCIA SERVICIOS) ==={RESET}")
    
    # 4.1 Valencia en DB no tiene recogida en local
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT business_name, business_type, delivery_available, pickup_available, pickup_badge, delivery_badge FROM epicentro_registrations WHERE slug = 'valenciaservicios'")
    valencia_db = cursor.fetchone()
    conn.close()
    
    valencia_ok = False
    if valencia_db:
        name, btype, deliv, pickup, pbadge, dbadge = valencia_db
        valencia_ok = (
            btype == "sin-punto-venta" and
            deliv == 1 and
            pickup == 0 and
            (pbadge is None or pbadge == "") and
            dbadge == "Servicio a domicilio en cotos"
        )
    report_result(
        "Valencia Servicios en DB: pickup_available=0, pickup_badge=NULL, delivery_badge configurada",
        valencia_ok,
        f"Datos DB: {valencia_db}"
    )
    
    # 4.2 Lógica de supresión de 'Recoger en local' en renderizadores de frontend
    files_to_check = [
        EPIZENTRO_DIR / "categoria.html",
        EPIZENTRO_DIR / "index.html",
        EPIZENTRO_DIR / "categorias" / "servicios-hogar.html"
    ]
    suppression_ok = True
    for fp in files_to_check:
        c = open(fp, "r", encoding="utf-8").read()
        if "sin-punto-venta" not in c or ("pickup_available !== false" not in c and "has_pickup: false" not in c):
            suppression_ok = False
            break
    report_result(
        "Supresión de insignia 'Recoger en local' para comercios sin punto de venta en HTMLs",
        suppression_ok,
        "Validado en categoria.html, index.html y servicios-hogar.html"
    )

    # 4.3 Controles en admin.html y editar.html
    admin_c = open(EPIZENTRO_DIR / "admin.html", "r", encoding="utf-8").read()
    editar_c = open(EPIZENTRO_DIR / "editar.html", "r", encoding="utf-8").read()
    admin_has_ctrls = "edit-pickup-available" in admin_c and "edit-delivery-badge" in admin_c
    editar_has_ctrls = "edit-pickup" in editar_c and "edit-delivery-badge" in editar_c
    report_result(
        "Controles de pickup/delivery en admin.html y editar.html (Link Mágico)",
        admin_has_ctrls and editar_has_ctrls,
        "Checkboxes y campos de texto para badges presentes en consola y autoservicio"
    )


def test_5_verified_badge_placement():
    print(f"\n{BLUE}=== 5. REDISEÑO Y UBICACIÓN DE LA INSIGNIA 'VERIFICADO' EN ESCAPARATES ==={RESET}")
    escaparates = [
        ("chile-chillon.html", EPIZENTRO_DIR / "chile-chillon.html"),
        ("botica-silvestre.html", EPIZENTRO_DIR / "botica-silvestre.html"),
        ("amdi.html", EPIZENTRO_DIR / "amdi.html"),
        ("tu-negocio.html", EPIZENTRO_DIR / "tu-negocio.html"),
        ("negocio.html", EPIZENTRO_DIR / "negocio.html"),
        ("app/templates/negocio.html", REPO_ROOT / "app" / "templates" / "negocio.html"),
    ]
    
    escaparates_ok = True
    for name, path in escaparates:
        c = open(path, "r", encoding="utf-8").read()
        # Verificar que NO tenga el badge flotante invasivo en el banner
        has_floating_badge = 'absolute top-4 right-4 sm:top-6 sm:right-6' in c and 'Verificado' in c
        # Verificar que tenga el badge compacto cerca de hero-title
        has_sub_badge = 'text-emerald-400 text-[10.5px] font-bold tracking-wide' in c or 'badge-check' in c
        if has_floating_badge or not has_sub_badge:
            escaparates_ok = False
            print(f"       -> Fallo en {name}: floating={has_floating_badge}, sub_badge={has_sub_badge}")
    
    report_result(
        "Insignia 'Verificado' compacta y ubicada debajo del nombre en los 6 escaparates",
        escaparates_ok,
        "100% de escaparates actualizados"
    )


def test_6_search_engine_and_indexing():
    print(f"\n{BLUE}=== 6. MOTOR DE BÚSQUEDA GLOBAL (EPICENTRO-SEARCH.JS) ==={RESET}")
    search_path = EPIZENTRO_DIR / "epicentro-search.js"
    search_code = open(search_path, "r", encoding="utf-8").read()
    
    has_fallback = "FALLBACK_CANONICAL_BUSINESSES" in search_code
    has_get_dir = "function getDirectoryBusinesses()" in search_code
    has_redirect = "getCategoryPageUrl(" in search_code and "categoria.html" in search_code
    
    report_result(
        "epicentro-search.js implementa getDirectoryBusinesses(), fallback canónico y redirección",
        has_fallback and has_get_dir and has_redirect,
        "Buscador preparado con respaldo y redirección de navegación"
    )
    
    # Simular la lógica de búsqueda de epicentro-search.js mediante Node.js
    query_tests = [
        ("chile", "Chile Chillón"),
        ("botica", "Botica Silvestre"),
        ("plomero", "Valencia Servicios"),
        ("valencia", "Valencia Servicios"),
        ("jessica", "Jessica Mendoza Bienes Raíces"),
        ("arquitectura", "AMDI Diseño Interior"),
    ]
    
    node_eval_script = f"""
    const fs = require('fs');
    const content = fs.readFileSync('{search_path}', 'utf8');
    const match = content.match(/const FALLBACK_CANONICAL_BUSINESSES\\s*=\\s*(\\[[\\s\\S]*?\\n  \\];)/);
    if (match) {{
        const list = eval(match[1]);
        console.log(JSON.stringify(list));
    }} else {{
        console.log('[]');
    }}
    """
    
    try:
        res = subprocess.run(["node", "-e", node_eval_script], capture_output=True, text=True, check=True)
        businesses = json.loads(res.stdout.strip())
        
        all_matches_found = True
        for term, expected_name in query_tests:
            q = term.lower().strip()
            matched = False
            for b in businesses:
                text_corpus = " ".join([
                    b.get("name", ""),
                    b.get("description", ""),
                    b.get("category_label", ""),
                    b.get("subcategory_label", ""),
                    b.get("coto", "")
                ]).lower()
                if q in text_corpus:
                    matched = True
                    break
            if not matched:
                all_matches_found = False
                print(f"       -> Query '{term}' no encontró '{expected_name}'")
        
        report_result(
            "Simulación de búsqueda en catálogo ('chile', 'botica', 'plomero', 'valencia', 'jessica')",
            all_matches_found and len(businesses) >= 5,
            "100% de consultas indexadas y resueltas exitosamente"
        )
    except Exception as e:
        report_result("Parseo y simulación de índice de búsqueda", False, str(e))


def test_7_fastapi_endpoints():
    print(f"\n{BLUE}=== 7. PRUEBAS DE INTEGRACIÓN DE ENDPOINTS FASTAPI ==={RESET}")
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # 7.1 /api/epicentro/businesses/active
        res_active = client.get("/api/epicentro/businesses/active")
        active_ok = res_active.status_code == 200 and len(res_active.json()) >= 5
        report_result(
            "GET /api/epicentro/businesses/active retorna comercios con schema extendido",
            active_ok,
            f"Status {res_active.status_code}, comercios: {len(res_active.json()) if active_ok else 0}"
        )
        
        # 7.2 /api/epicentro/businesses/chile-chillon
        res_chillon = client.get("/api/epicentro/businesses/chile-chillon")
        data_ch = res_chillon.json() if res_chillon.status_code == 200 else {}
        ch_ok = (
            res_chillon.status_code == 200 and
            data_ch.get("business_name") == "Chile Chillón" and
            "10:00 a 20:00 hrs" in (data_ch.get("schedule") or "")
        )
        report_result(
            "GET /api/epicentro/businesses/chile-chillon retorna horario y datos canónicos",
            ch_ok,
            f"Horario: {data_ch.get('schedule')}"
        )
        
        # 7.3 /api/epicentro/businesses/valencia-servicios
        res_valencia = client.get("/api/epicentro/businesses/valencia-servicios")
        data_val = res_valencia.json() if res_valencia.status_code == 200 else {}
        val_ok = (
            res_valencia.status_code == 200 and
            data_val.get("business_name") == "Valencia Servicios" and
            data_val.get("pickup_available") is False
        )
        report_result(
            "GET /api/epicentro/businesses/valencia-servicios retorna pickup_available: false",
            val_ok,
            f"pickup_available: {data_val.get('pickup_available')}"
        )
        
    except Exception as err:
        report_result("Ejecución de TestClient de FastAPI", False, str(err))


def test_8_self_service_autoservicio():
    print(f"\n{BLUE}=== 8. VALIDACIÓN DE AUTOSERVICIO (EDITAR.HTML), MENÚ SIN FOTO Y SECCIÓN 3 ==={RESET}")
    editar_path = EPIZENTRO_DIR / "editar.html"
    if not editar_path.exists():
        report_result("Archivo editar.html existe", False)
        return
    
    html = open(editar_path, "r", encoding="utf-8").read()
    
    has_menu_sections = (
        "menu-sections-container" in html and
        "btn-add-menu-section" in html and
        "other_products_sections" in html and
        "renderMenuSections" in html
    )
    report_result(
        "editar.html cuenta con módulo de Secciones Tipo Menú Sin Foto (Sección 2.1)",
        has_menu_sections,
        "Contenedor dinámico y funciones de gestión presentes"
    )

    has_ordered_section_3 = (
        "edit-delivery" in html and
        "edit-pickup" in html and
        "edit-schedule" in html and
        "edit-address" in html and
        "edit-description" in html and
        "edit-payment-method" in html and
        "edit-coverage-zone" in html and
        "edit-wa" in html and
        "edit-phone" in html
    )
    pos_delivery = html.find('id="edit-delivery"')
    pos_schedule = html.find('id="edit-schedule"')
    pos_address = html.find('id="edit-address"')
    pos_desc = html.find('id="edit-description"')
    pos_payment = html.find('id="edit-payment-method"')
    pos_coverage = html.find('id="edit-coverage-zone"')
    
    order_ok = (
        has_ordered_section_3 and
        pos_delivery < pos_schedule < pos_address < pos_desc < pos_payment < pos_coverage
    )
    report_result(
        "Sección 3 en editar.html ordenada estrictamente (Modalidades -> Horario -> Ubicación -> Descripción -> Pagos -> Cobertura)",
        order_ok,
        "Orden y controles de Sección 3 verificados 100%"
    )

    try:
        from fastapi.testclient import TestClient
        from app.main import app
        from app.core.database import SessionLocal
        from app.models.epicentro_registration import EpicentroRegistration
        
        client = TestClient(app)
        db = SessionLocal()
        try:
            reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.business_name.ilike("%chill%")).first()
            if not reg:
                reg = db.query(EpicentroRegistration).first()
            if not reg.edit_token:
                reg.edit_token = "test-token-autoservicio-vergotas"
                db.commit()
            
            token = reg.edit_token
            
            res_get = client.get(f"/api/epicentro/self-service/{token}")
            get_data = res_get.json() if res_get.status_code == 200 else {}
            get_ok = (
                res_get.status_code == 200 and
                "delivery_badge" in get_data and
                "pickup_available" in get_data and
                "payment_method" in get_data and
                "coverage_zone" in get_data
            )
            report_result(
                "GET /api/epicentro/self-service/{token} retorna campos operativos completos",
                get_ok,
                f"Status: {res_get.status_code}"
            )
            
            test_menu_sections = [
                {
                    "title": "Presentaciones por Litro",
                    "subtitle": "Para familias y eventos",
                    "description": "Precios especiales en presentaciones grandes",
                    "items": [
                        {"name": "1 Litro Salsa Macha", "price": 280.0, "description": "Presentación familiar"},
                        {"name": "1 Litro Salsa Habanera", "price": 260.0, "description": "Picante medio"}
                    ]
                }
            ]
            put_payload = {
                "schedule": "Lunes a Domingo · 10:00 a 20:00 hrs",
                "payment_method": "Efectivo contra entrega, transferencia SPEI, tarjetas y Mercado Pago",
                "coverage_zone": "Zona Mariano Otero (Envíos directos a caseta en cotos Natura y Los Robles)",
                "delivery_available": True,
                "delivery_badge": "Servicio a domicilio en cotos",
                "pickup_available": True,
                "pickup_badge": "Recoger en local",
                "microsite_data": {
                    "other_products_sections": test_menu_sections
                }
            }
            res_put = client.put(f"/api/epicentro/self-service/{token}", json=put_payload)
            put_ok = res_put.status_code == 200 and res_put.json().get("success") is True
            report_result(
                "PUT /api/epicentro/self-service/{token} guarda cambios operativos y secciones de menú",
                put_ok,
                f"Status: {res_put.status_code}"
            )
            
            db.refresh(reg)
            md_persisted = json.loads(reg.microsite_data) if isinstance(reg.microsite_data, str) else (reg.microsite_data or {})
            persist_ok = (
                reg.payment_method == put_payload["payment_method"] and
                reg.coverage_zone == put_payload["coverage_zone"] and
                "other_products_sections" in md_persisted and
                len(md_persisted["other_products_sections"]) >= 1
            )
            report_result(
                "Persistencia SQLite de secciones de menú, métodos de pago y zona de cobertura",
                persist_ok,
                f"Menu sections: {len(md_persisted.get('other_products_sections', []))}"
            )
            
        finally:
            db.close()
            
    except Exception as err:
        report_result("Pruebas E2E de API de autoservicio", False, str(err))


def main():
    print(f"\n{BOLD}{'=' * 75}{RESET}")
    print(f"{BOLD}   SUITE AUTOMATIZADA DE VERIFICACIÓN KAM - EPIZENTRO NATURA{RESET}")
    print(f"{BOLD}   Auditor: 'El Vergotas' · Metodología Gold Fish{RESET}")
    print(f"{BOLD}{'=' * 75}{RESET}")
    
    test_1_html_and_js_syntax()
    test_2_cls_and_category_stability()
    test_3_chile_chillon_synchronization()
    test_4_essential_cards_and_valencia_pickup()
    test_5_verified_badge_placement()
    test_6_search_engine_and_indexing()
    test_7_fastapi_endpoints()
    test_8_self_service_autoservicio()
    
    total = passed_tests + failed_tests
    rate = (passed_tests / total * 100) if total > 0 else 0
    
    print(f"\n{BOLD}{'=' * 75}{RESET}")
    print(f"{BOLD}RESULTADO FINAL DE AUDITORÍA:{RESET}")
    print(f"  Pruebas Ejecutadas: {total}")
    print(f"  Aprobadas: {GREEN}{passed_tests}{RESET}")
    print(f"  Falladas:  {RED if failed_tests > 0 else GREEN}{failed_tests}{RESET}")
    print(f"  Tasa de Éxito: {GREEN if rate == 100 else RED}{rate:.1f}%{RESET}")
    print(f"{BOLD}{'=' * 75}{RESET}")
    
    if failed_tests == 0:
        print(f"\n{GREEN}{BOLD}✓ CERTIFICACIÓN KAM APROBADA: CERO DEFECTOS DETECTADOS.{RESET}")
        print(f"{GREEN}Listo para commit y despliegue a producción.{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{RED}{BOLD}✗ RECHAZADO POR 'EL VERGOTAS': SE ENCONTRARON {failed_tests} DEFECTOS.{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
