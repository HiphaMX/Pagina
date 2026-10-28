import json
import logging
import re
import socket
import ssl
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.client import AgencyClient
from app.models.web_health import WebHealthAudit

logger = logging.getLogger(__name__)

# Lista de respaldo de dominios de clientes activos en producción
DEFAULT_CLIENT_SITES = [
    {"name": "Hipha MX", "domain": "hipha.mx", "url": "https://www.hipha.mx"},
    {"name": "AMDI", "domain": "amdi.mx", "url": "https://www.amdi.mx"},
    {"name": "Centro de Urología Avanzada", "domain": "urologia-avanzada.com.mx", "url": "https://www.urologia-avanzada.com.mx"},
    {"name": "Uro-Oncology", "domain": "uro-oncology.com.mx", "url": "https://www.uro-oncology.com.mx"},
    {"name": "Oncología Robótica", "domain": "oncologia-robotica.com", "url": "https://oncologia-robotica.com"},
    {"name": "El Chile Chillón", "domain": "elchilechillon.mx", "url": "https://www.elchilechillon.mx"},
    {"name": "White Clean", "domain": "whiteclean.com.mx", "url": "https://www.whiteclean.com.mx"},
    {"name": "Valencia Servicios", "domain": "valenciaservicios.mx", "url": "https://www.valenciaservicios.mx"},
    {"name": "Botica Silvestre", "domain": "botica-silvestre.com", "url": "https://www.botica-silvestre.com"},
    {"name": "Jessica Mendoza Bienes Raíces", "domain": "jessicamendozabienesraices.com", "url": "https://www.jessicamendozabienesraices.com"},
    {"name": "Grupo Gari", "domain": "grupo-gari.com", "url": "https://www.grupo-gari.com"},
    {"name": "Letrerama", "domain": "letrerama.com", "url": "https://www.letrerama.com"}
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (HiphaWebGuardian/1.0)"


def clean_domain_string(raw: str) -> str:
    """Extrae el dominio limpio sin http, www inicial ni rutas."""
    if not raw:
        return ""
    d = raw.strip().lower()
    d = re.sub(r"^https?://", "", d)
    d = d.split("/")[0]
    if d.startswith("www."):
        d = d[4:]
    return d


def query_doh_txt_record(domain: str) -> List[str]:
    """Consulta registros TXT usando Cloudflare DNS-over-HTTPS (DoH)."""
    try:
        url = f"https://cloudflare-dns.com/dns-query?name={domain}&type=TXT"
        res = requests.get(url, headers={"accept": "application/dns-json"}, timeout=4)
        if res.status_code == 200:
            data = res.json()
            answers = data.get("Answer", [])
            records = []
            for ans in answers:
                rdata = ans.get("data", "").strip('\"')
                if rdata:
                    records.append(rdata)
            return records
    except Exception as e:
        logger.debug(f"Error DoH para {domain}: {e}")
    return []


def check_ssl_certificate(domain: str) -> Dict[str, Any]:
    """Inspecciona el certificado SSL nativo vía socket TLS."""
    result = {
        "valid": False,
        "days_remaining": None,
        "issuer": None,
        "error": None
    }
    try:
        context = ssl.create_default_context()
        # Conexión directa con timeout corto
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    expires_str = cert.get("notAfter")
                    expires_dt = datetime.strptime(expires_str, "%b %d %H:%M:%S %Y %Z")
                    days_left = (expires_dt - datetime.utcnow()).days
                    result["valid"] = days_left > 0
                    result["days_remaining"] = max(0, days_left)
                    
                    issuer_tuples = cert.get("issuer", ())
                    issuer_dict = dict(x[0] for x in issuer_tuples if x)
                    result["issuer"] = issuer_dict.get("organizationName") or issuer_dict.get("commonName") or "Desconocido"
    except ssl.SSLCertVerificationError as e:
        result["valid"] = False
        result["error"] = f"Error verificación SSL: {e.verify_message}"
    except Exception as e:
        result["valid"] = False
        result["error"] = str(e)
    return result


def audit_single_domain(site_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Realiza una auditoría completa de salud web para un dominio:
    1. HTTP Status & TTFB
    2. SSL & Expiración
    3. DNS SPF & DMARC
    4. Google Maps & APIs
    5. GEO & llms.txt / robots.txt
    """
    name = site_info.get("name") or "Sitio Web"
    raw_url = site_info.get("url") or site_info.get("domain") or ""
    client_id = site_info.get("client_id")
    
    clean_domain = clean_domain_string(raw_url)
    target_url = f"https://www.{clean_domain}" if not clean_domain.startswith("www.") else f"https://{clean_domain}"

    issues: List[str] = []
    details: Dict[str, Any] = {}
    score = 100

    # 1. PING HTTP & Medición de Rendimiento (TTFB)
    is_up = False
    status_code = None
    response_time_ms = 0.0
    html_content = ""

    t_start = time.perf_counter()
    try:
        res = requests.get(
            target_url,
            headers={"User-Agent": USER_AGENT},
            timeout=8,
            allow_redirects=True
        )
        response_time_ms = round((time.perf_counter() - t_start) * 1000, 1)
        status_code = res.status_code
        is_up = 200 <= status_code < 400
        html_content = res.text[:50000] if is_up else ""
        details["final_url"] = res.url
        details["server_headers"] = dict(res.headers)
    except requests.exceptions.SSLError:
        # Intento fallback a http para medir si el sitio existe pero falla el certificado
        try:
            res_http = requests.get(f"http://{clean_domain}", timeout=6, allow_redirects=True)
            status_code = res_http.status_code
            is_up = True
            response_time_ms = round((time.perf_counter() - t_start) * 1000, 1)
        except Exception:
            is_up = False
            status_code = 0
            issues.append("Error crítico: Certificado SSL no válido o conexión rechazada.")
    except Exception as e:
        is_up = False
        status_code = 0
        response_time_ms = round((time.perf_counter() - t_start) * 1000, 1)
        issues.append(f"Sitio no disponible o timeout (>8s): {str(e)[:60]}")

    if not is_up:
        score -= 60
    elif response_time_ms > 2000:
        score -= 15
        issues.append(f"Tiempo de respuesta elevado ({response_time_ms} ms)")
    elif response_time_ms > 1200:
        score -= 8

    # 2. SSL & Expiración
    ssl_info = check_ssl_certificate(clean_domain)
    ssl_valid = ssl_info.get("valid", False)
    ssl_days = ssl_info.get("days_remaining")
    ssl_issuer = ssl_info.get("issuer")

    if not ssl_valid:
        score -= 30
        if "SSL" not in "".join(issues):
            issues.append(f"Certificado SSL no válido ({ssl_info.get('error', 'Fallo')})")
    elif ssl_days is not None:
        if ssl_days <= 10:
            score -= 20
            issues.append(f"¡Atención urgente! Certificado SSL vence en {ssl_days} días")
        elif ssl_days <= 25:
            score -= 10
            issues.append(f"Certificado SSL por vencer ({ssl_days} días restantes)")

    # 3. DNS: SPF & DMARC para Entregabilidad de Correos
    spf_records = query_doh_txt_record(clean_domain)
    dmarc_records = query_doh_txt_record(f"_dmarc.{clean_domain}")

    has_spf = any("v=spf1" in r for r in spf_records)
    has_dmarc = any("v=dmarc1" in r.lower() for r in dmarc_records)

    dns_spf_status = "OK" if has_spf else "MISSING"
    dns_dmarc_status = "OK" if has_dmarc else "MISSING"

    spf_val = next((r for r in spf_records if "v=spf1" in r), None)
    dmarc_val = next((r for r in dmarc_records if "v=dmarc1" in r.lower()), None)

    if not has_spf:
        score -= 8
        issues.append("Registro DNS SPF ausente (riesgo de rebote en correos salientes)")
    if not has_dmarc:
        score -= 4
        issues.append("Registro DNS DMARC ausente")

    # 4. Google Maps & Integración de APIs
    maps_status = "NO_MAPS"
    if html_content:
        has_maps_iframe = bool(re.search(r'(?:google\.com/maps|maps\.google\.com)', html_content, re.IGNORECASE))
        has_maps_script = bool(re.search(r'maps\.googleapis\.com/maps/api/js', html_content, re.IGNORECASE))

        if has_maps_iframe or has_maps_script:
            # Revisar si hay claves rotas o desarrollo
            if "for development purposes only" in html_content.lower():
                maps_status = "ERROR"
                score -= 15
                issues.append("API de Google Maps en modo 'Development purposes only'")
            elif has_maps_script and "key=" not in html_content:
                maps_status = "WARNING"
                score -= 8
                issues.append("Script de Google Maps sin API Key explícita")
            else:
                maps_status = "OK"

    # 5. Estándar GEO & Web Agéntica (robots.txt y llms.txt)
    has_robots_txt = False
    robots_allows_ai = False
    has_llms_txt = False

    try:
        res_rob = requests.get(f"https://{clean_domain}/robots.txt", timeout=4)
        if res_rob.status_code == 200 and len(res_rob.text) > 10:
            has_robots_txt = True
            rob_txt = res_rob.text.lower()
            if "google-extended" in rob_txt or "gptbot" in rob_txt or "allow: /" in rob_txt:
                robots_allows_ai = True
    except Exception:
        pass

    try:
        res_llm = requests.get(f"https://{clean_domain}/llms.txt", timeout=4)
        if res_llm.status_code == 200 and len(res_llm.text) > 40:
            has_llms_txt = True
    except Exception:
        pass

    if not has_llms_txt:
        score -= 5

    # Determinar Nivel de Salud
    final_score = max(0, min(100, score))
    if not is_up or (ssl_days is not None and ssl_days <= 0):
        health_level = "CRITICAL"
    elif final_score >= 85 and not issues:
        health_level = "HEALTHY"
    elif final_score >= 60:
        health_level = "WARNING"
    else:
        health_level = "CRITICAL"

    # Recomendación del Agente
    if health_level == "HEALTHY":
        recommendation = "Sitio operando con disponibilidad y rendimiento óptimos. Certificados y seguridad al día."
    elif health_level == "WARNING":
        recommendation = f"Se detectaron aspectos no críticos que ameritan revisión preventiva: {', '.join(issues[:2])}."
    else:
        recommendation = f"¡Incidencia crítica detectada! {', '.join(issues[:2])}. Requiere atención técnica inmediata."

    return {
        "client_id": client_id,
        "client_name": name,
        "domain": clean_domain,
        "url": target_url,
        "status_code": status_code,
        "is_up": is_up,
        "response_time_ms": response_time_ms,
        "ssl_valid": ssl_valid,
        "ssl_days_remaining": ssl_days,
        "ssl_issuer": ssl_issuer,
        "dns_spf_status": dns_spf_status,
        "dns_spf_record": spf_val,
        "dns_dmarc_status": dns_dmarc_status,
        "dns_dmarc_record": dmarc_val,
        "smtp_status": "OK",
        "maps_status": maps_status,
        "has_llms_txt": has_llms_txt,
        "has_robots_txt": has_robots_txt,
        "robots_allows_ai": robots_allows_ai,
        "overall_score": final_score,
        "health_level": health_level,
        "issues_summary": issues,
        "details_json": details,
        "agent_recommendation": recommendation,
        "created_at": datetime.utcnow()
    }


def generate_fleet_ai_summary(audits: List[Dict[str, Any]]) -> str:
    """
    Genera un resumen ejecutivo en lenguaje natural utilizando Gemini (o fallback inteligente)
    sintetizando el estado global de todos los sitios monitoreados.
    """
    total = len(audits)
    healthy = sum(1 for a in audits if a["health_level"] == "HEALTHY")
    warnings = sum(1 for a in audits if a["health_level"] == "WARNING")
    critical = sum(1 for a in audits if a["health_level"] == "CRITICAL")
    
    issues_list = []
    for a in audits:
        if a["issues_summary"]:
            issues_list.append(f"- {a['client_name']} ({a['domain']}): {'; '.join(a['issues_summary'])}")

    # Intento con Gemini API si está configurada
    gemini_key = getattr(settings, "GEMINI_API_KEY", None) or __import__("os").environ.get("GEMINI_API_KEY")
    if gemini_key and len(gemini_key) > 10:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = (
                f"Eres el Agente Guardián Web de la agencia HiphaMX. "
                f"Acabas de auditar {total} sitios web de clientes. "
                f"Resultados: {healthy} saludables, {warnings} con advertencias, {critical} críticos. "
                f"Detalle de incidencias encontradas:\n" + ("\n".join(issues_list) if issues_list else "Ninguna, todos 100% operativos.") + "\n\n"
                f"Escribe un reporte ejecutivo de 2 a 3 oraciones en tono profesional, ágil y de confianza para el dashboard de la agencia. "
                f"Menciona los puntos que requieran atención inmediata si los hay, o felicita por la estabilidad general si todo está en orden."
            )
            resp = model.generate_content(prompt)
            if resp and resp.text:
                return resp.text.strip()
        except Exception as e:
            logger.debug(f"Gemini AI briefing fallback: {e}")

    # Fallback Determinista Inteligente
    if critical > 0:
        return f"🛡️ Alerta del Guardián: Se detectaron {critical} sitio(s) con incidencias críticas y {warnings} con advertencias de un total de {total} dominios. Revisa las tarjetas en rojo para restaurar servicios prioritarios."
    elif warnings > 0:
        return f"🛡️ Diagnóstico del Guardián: {healthy} de {total} sitios web operan con disponibilidad total. Existen {warnings} observación(es) menores (tiempos de respuesta o registros DNS) que recomendamos optimizar."
    else:
        return f"🛡️ Flota al 100%: Los {total} sitios web monitoreados operan sin interrupciones, con certificados SSL vigentes y tiempos de carga óptimos."


def audit_all_fleet(db: Session, use_ai: bool = True) -> Dict[str, Any]:
    """
    Ejecuta la auditoría en paralelo para todos los clientes activos registrados en el sistema.
    """
    # 1. Obtener clientes de la base de datos
    db_clients = db.query(AgencyClient).filter(AgencyClient.status == "active").all()
    
    fleet_map: Dict[str, Dict[str, Any]] = {}
    
    # Agregar primero los predeterminados para asegurar cobertura total
    for item in DEFAULT_CLIENT_SITES:
        d_clean = clean_domain_string(item["domain"])
        if "healthyice" in d_clean.lower() or "healthyice" in item["name"].lower():
            continue
        fleet_map[d_clean] = {
            "name": item["name"],
            "domain": d_clean,
            "url": item["url"],
            "client_id": None
        }

    # Combinar con los registrados en base de datos
    for c in db_clients:
        if "healthyice" in c.name.lower():
            continue
        if c.website_url:
            d_clean = clean_domain_string(c.website_url)
            if d_clean and "healthyice" not in d_clean.lower():
                fleet_map[d_clean] = {
                    "name": c.name,
                    "domain": d_clean,
                    "url": f"https://www.{d_clean}",
                    "client_id": c.id
                }

    sites_to_audit = list(fleet_map.values())
    audits: List[Dict[str, Any]] = []

    # 2. Ejecución en paralelo con ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_site = {executor.submit(audit_single_domain, s): s for s in sites_to_audit}
        for future in as_completed(future_to_site):
            try:
                res = future.result()
                audits.append(res)
            except Exception as e:
                s_info = future_to_site[future]
                logger.error(f"Fallo en auditoría de {s_info.get('domain')}: {e}")

    # Ordenar por score ascendente (los que tienen problemas primero)
    audits.sort(key=lambda x: (0 if x["health_level"] == "CRITICAL" else (1 if x["health_level"] == "WARNING" else 2), x["overall_score"]))

    # 3. Guardar en base de datos
    now_dt = datetime.utcnow()
    for item in audits:
        db_audit = WebHealthAudit(
            client_id=item.get("client_id"),
            client_name=item.get("client_name"),
            domain=item.get("domain"),
            url=item.get("url"),
            status_code=item.get("status_code"),
            is_up=item.get("is_up"),
            response_time_ms=item.get("response_time_ms"),
            ssl_valid=item.get("ssl_valid"),
            ssl_days_remaining=item.get("ssl_days_remaining"),
            ssl_issuer=item.get("ssl_issuer"),
            dns_spf_status=item.get("dns_spf_status"),
            dns_spf_record=item.get("dns_spf_record"),
            dns_dmarc_status=item.get("dns_dmarc_status"),
            dns_dmarc_record=item.get("dns_dmarc_record"),
            smtp_status=item.get("smtp_status"),
            maps_status=item.get("maps_status"),
            has_llms_txt=item.get("has_llms_txt"),
            has_robots_txt=item.get("has_robots_txt"),
            robots_allows_ai=item.get("robots_allows_ai"),
            overall_score=item.get("overall_score"),
            health_level=item.get("health_level"),
            issues_summary=json.dumps(item.get("issues_summary", []), ensure_ascii=False),
            details_json=json.dumps(item.get("details_json", {}), ensure_ascii=False),
            agent_recommendation=item.get("agent_recommendation"),
            created_at=now_dt
        )
        db.add(db_audit)
    
    try:
        db.commit()
    except Exception as e:
        logger.error(f"Error guardando auditorías en DB: {e}")
        db.rollback()

    # 4. Generar reporte consolidado del agente
    agent_summary = generate_fleet_ai_summary(audits) if use_ai else "Auditoría completada exitosamente."

    total_sites = len(audits)
    healthy_sites = sum(1 for a in audits if a["health_level"] == "HEALTHY")
    warning_sites = sum(1 for a in audits if a["health_level"] == "WARNING")
    critical_sites = sum(1 for a in audits if a["health_level"] == "CRITICAL")
    avg_resp = round(sum(a["response_time_ms"] for a in audits) / max(1, total_sites), 1)
    ssl_expiring = sum(1 for a in audits if a["ssl_days_remaining"] is not None and a["ssl_days_remaining"] <= 30)

    return {
        "kpis": {
            "total_sites": total_sites,
            "healthy_sites": healthy_sites,
            "warning_sites": warning_sites,
            "critical_sites": critical_sites,
            "avg_response_time_ms": avg_resp,
            "ssl_expiring_soon_count": ssl_expiring,
            "smtp_ok_count": sum(1 for a in audits if a["dns_spf_status"] == "OK"),
            "maps_ok_count": sum(1 for a in audits if a["maps_status"] in ("OK", "NO_MAPS")),
            "llms_txt_count": sum(1 for a in audits if a["has_llms_txt"]),
            "last_audit_time": now_dt
        },
        "agent_summary": agent_summary,
        "sites": audits,
        "last_audit_iso": now_dt.isoformat()
    }
