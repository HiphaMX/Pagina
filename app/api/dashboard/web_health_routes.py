import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from app.models.web_health import WebHealthAudit
from app.schemas.web_health import (
    WebHealthOverviewResponse,
    WebHealthItemSchema,
    RunAuditRequest
)
from app.services.monitoring.web_guardian import (
    audit_all_fleet,
    audit_single_domain,
    clean_domain_string,
    generate_fleet_ai_summary
)

router = APIRouter()


@router.get("/overview")
def get_web_health_overview(
    force_refresh: bool = Query(False, description="Forzar nueva inspección en vivo de todos los sitios"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Retorna el estado de salud de todos los sitios web de clientes de Hipha.
    Si existen auditorías recientes (<24h), las retorna al instante de la base de datos;
    de lo contrario (o con force_refresh=true), detona una nueva auditoría en vivo.
    """
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)

    # 1. Si no es force_refresh, buscar la última auditoría en base de datos
    if not force_refresh:
        latest_audit = db.query(WebHealthAudit).order_by(desc(WebHealthAudit.created_at)).first()
        if latest_audit and latest_audit.created_at >= yesterday:
            # Obtener el registro más reciente por cada dominio
            subq = (
                db.query(
                    WebHealthAudit.domain,
                    func.max(WebHealthAudit.id).label("max_id")
                )
                .group_by(WebHealthAudit.domain)
                .subquery()
            )

            records = (
                db.query(WebHealthAudit)
                .join(subq, WebHealthAudit.id == subq.c.max_id)
                .order_by(
                    desc(WebHealthAudit.health_level == "CRITICAL"),
                    desc(WebHealthAudit.health_level == "WARNING"),
                    WebHealthAudit.overall_score
                )
                .all()
            )

            if records:
                sites = []
                for r in records:
                    issues = []
                    if r.issues_summary:
                        try:
                            issues = json.loads(r.issues_summary)
                        except Exception:
                            issues = []
                    details = {}
                    if r.details_json:
                        try:
                            details = json.loads(r.details_json)
                        except Exception:
                            details = {}

                    sites.append({
                        "id": r.id,
                        "client_id": r.client_id,
                        "client_name": r.client_name,
                        "domain": r.domain,
                        "url": r.url,
                        "status_code": r.status_code,
                        "is_up": r.is_up,
                        "response_time_ms": r.response_time_ms or 0.0,
                        "ssl_valid": r.ssl_valid,
                        "ssl_days_remaining": r.ssl_days_remaining,
                        "ssl_issuer": r.ssl_issuer,
                        "dns_spf_status": r.dns_spf_status,
                        "dns_spf_record": r.dns_spf_record,
                        "dns_dmarc_status": r.dns_dmarc_status,
                        "dns_dmarc_record": r.dns_dmarc_record,
                        "smtp_status": r.smtp_status,
                        "maps_status": r.maps_status,
                        "has_llms_txt": r.has_llms_txt,
                        "has_robots_txt": r.has_robots_txt,
                        "robots_allows_ai": r.robots_allows_ai,
                        "overall_score": r.overall_score,
                        "health_level": r.health_level,
                        "issues_summary": issues,
                        "details_json": details,
                        "agent_recommendation": r.agent_recommendation,
                        "created_at": r.created_at.isoformat() if r.created_at else None
                    })

                total = len(sites)
                healthy = sum(1 for s in sites if s["health_level"] == "HEALTHY")
                warnings = sum(1 for s in sites if s["health_level"] == "WARNING")
                critical = sum(1 for s in sites if s["health_level"] == "CRITICAL")
                avg_time = round(sum(s["response_time_ms"] for s in sites) / max(1, total), 1)
                ssl_expiring = sum(1 for s in sites if s["ssl_days_remaining"] is not None and s["ssl_days_remaining"] <= 30)

                agent_summary = generate_fleet_ai_summary(sites)

                return {
                    "kpis": {
                        "total_sites": total,
                        "healthy_sites": healthy,
                        "warning_sites": warnings,
                        "critical_sites": critical,
                        "avg_response_time_ms": avg_time,
                        "ssl_expiring_soon_count": ssl_expiring,
                        "smtp_ok_count": sum(1 for s in sites if s["dns_spf_status"] == "OK"),
                        "maps_ok_count": sum(1 for s in sites if s["maps_status"] in ("OK", "NO_MAPS")),
                        "llms_txt_count": sum(1 for s in sites if s["has_llms_txt"]),
                        "last_audit_time": latest_audit.created_at.isoformat()
                    },
                    "agent_summary": agent_summary,
                    "sites": sites,
                    "last_audit_iso": latest_audit.created_at.isoformat()
                }

    # 2. Si no hay datos o se solicitó refrescar, correr auditoría en vivo
    result = audit_all_fleet(db, use_ai=True)
    return result


@router.post("/run-audit")
def run_fleet_audit(
    payload: Optional[RunAuditRequest] = None,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Ejecuta una auditoría manual inmediata de toda la flota de sitios web
    o de un dominio en particular.
    """
    domain_to_audit = payload.domain if payload else None
    if domain_to_audit:
        clean = clean_domain_string(domain_to_audit)
        site_info = {
            "name": clean,
            "domain": clean,
            "url": f"https://www.{clean}"
        }
        res = audit_single_domain(site_info)
        # Guardar en DB
        db_audit = WebHealthAudit(
            client_name=res.get("client_name"),
            domain=res.get("domain"),
            url=res.get("url"),
            status_code=res.get("status_code"),
            is_up=res.get("is_up"),
            response_time_ms=res.get("response_time_ms"),
            ssl_valid=res.get("ssl_valid"),
            ssl_days_remaining=res.get("ssl_days_remaining"),
            ssl_issuer=res.get("ssl_issuer"),
            dns_spf_status=res.get("dns_spf_status"),
            dns_spf_record=res.get("dns_spf_record"),
            dns_dmarc_status=res.get("dns_dmarc_status"),
            dns_dmarc_record=res.get("dns_dmarc_record"),
            smtp_status=res.get("smtp_status"),
            maps_status=res.get("maps_status"),
            has_llms_txt=res.get("has_llms_txt"),
            has_robots_txt=res.get("has_robots_txt"),
            robots_allows_ai=res.get("robots_allows_ai"),
            overall_score=res.get("overall_score"),
            health_level=res.get("health_level"),
            issues_summary=json.dumps(res.get("issues_summary", []), ensure_ascii=False),
            details_json=json.dumps(res.get("details_json", {}), ensure_ascii=False),
            agent_recommendation=res.get("agent_recommendation")
        )
        db.add(db_audit)
        db.commit()
        return {"success": True, "site": res}

    use_ai = payload.use_ai if payload else True
    return audit_all_fleet(db, use_ai=use_ai)


@router.get("/history/{domain}")
def get_domain_health_history(
    domain: str,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Retorna el historial de auditorías de salud de un dominio específico.
    """
    clean = clean_domain_string(domain)
    records = (
        db.query(WebHealthAudit)
        .filter(WebHealthAudit.domain == clean)
        .order_by(desc(WebHealthAudit.created_at))
        .limit(limit)
        .all()
    )

    results = []
    for r in records:
        issues = []
        if r.issues_summary:
            try:
                issues = json.loads(r.issues_summary)
            except Exception:
                issues = []
        results.append({
            "id": r.id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "status_code": r.status_code,
            "is_up": r.is_up,
            "response_time_ms": r.response_time_ms,
            "ssl_days_remaining": r.ssl_days_remaining,
            "overall_score": r.overall_score,
            "health_level": r.health_level,
            "issues_summary": issues
        })
    return results


@router.get("/cron")
def run_cron_web_health(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Endpoint público optimizado para ser detonado por Vercel Cron cada 48h.
    Ejecuta la auditoría completa y persiste las métricas.
    """
    try:
        res = audit_all_fleet(db, use_ai=False)
        return {
            "success": True,
            "message": "Auditoría de flota ejecutada por cron exitosamente.",
            "kpis": res.get("kpis")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
