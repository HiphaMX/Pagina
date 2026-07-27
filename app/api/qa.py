from fastapi import APIRouter
from app.core.config import settings
from typing import Dict, Any, List

router = APIRouter()

@router.get("/qa/validate-smtp", response_model=Dict[str, Any])
async def validate_smtp_alignment():
    """
    Diagnóstico de QA para verificar que cada proyecto envíe correos 
    solamente con su dominio correspondiente o mediante un fallback válido.
    Utilizado por SiteSentinel para auditoría de configuración.
    """
    projects = [
        {"prefix": "HIPHA", "domain": "hipha.mx", "name": "HiphaMX Agency (Global)"},
        {"prefix": "AMDI", "domain": "amdi.mx", "name": "Adriana Medina Diseño Interior"},
        {"prefix": "CHILECHILLON", "domain": "chilechillon.com", "name": "El Chile Chillón"},
        {"prefix": "WHITECLEAN", "domain": "whiteclean.mx", "name": "White Clean"},
        {"prefix": "GRUPOGARI", "domain": "grupogari.com", "name": "Grupo Gari"},
        {"prefix": "VALENCIA", "domain": "valenciaservicios.com", "name": "Valencia Servicios"},
        {"prefix": "BOTICA", "domain": "boticasilvestre.com", "name": "Botica Silvestre"},
        {"prefix": "HEALTHYICE", "domain": "healthyice.mx", "name": "HealthyIce"},
    ]

    report: List[Dict[str, Any]] = []
    has_critical_errors = False
    has_warnings = False

    # 1. Check Global/Agency SMTP first
    global_user = settings.SMTP_USER
    global_host = settings.SMTP_HOST
    global_configured = bool(global_host and global_user)
    
    global_status = "NOT_CONFIGURED"
    global_error = None
    if global_configured:
        if "hipha.mx" in global_user.lower():
            global_status = "OK"
        else:
            global_status = "CRITICAL_MISMATCH"
            global_error = f"Global SMTP user '{global_user}' does not belong to agency domain 'hipha.mx'"
            has_critical_errors = True

    # 2. Check each project
    for proj in projects:
        prefix = proj["prefix"]
        domain = proj["domain"]
        name = proj["name"]

        if prefix == "HIPHA":
            # Global agency SMTP info
            report.append({
                "project": name,
                "prefix": prefix,
                "configured_specifically": True,
                "smtp_user": global_user,
                "smtp_host": global_host,
                "expected_domain": domain,
                "status": global_status,
                "details": global_error or "Global SMTP is correctly aligned."
            })
            continue

        # Check client-specific SMTP
        spec_host = getattr(settings, f"{prefix}_SMTP_HOST", "")
        spec_user = getattr(settings, f"{prefix}_SMTP_USER", "")
        spec_configured = bool(spec_host and spec_user)

        status = "OK"
        details = ""

        if spec_configured:
            if domain.lower() in spec_user.lower():
                status = "OK"
                details = f"Dedicated SMTP configured and correctly aligned with domain '{domain}'."
            else:
                status = "WARNING_MISMATCH"
                details = f"Dedicated SMTP configured but user '{spec_user}' does not match domain '{domain}'."
                has_warnings = True
        else:
            # Fallback to global
            if global_configured:
                if global_status == "OK":
                    status = "FALLBACK_OK"
                    details = f"Using global SMTP fallback ({global_user}). Replies will go to project from_email."
                else:
                    status = "FALLBACK_WARNING"
                    details = f"Using global SMTP fallback but global SMTP has mismatch error: {global_error}"
                    has_warnings = True
            else:
                status = "SMTP_MISSING"
                details = "No dedicated SMTP configured and global SMTP fallback is not available."
                has_warnings = True

        report.append({
            "project": name,
            "prefix": prefix,
            "configured_specifically": spec_configured,
            "smtp_user": spec_user if spec_configured else (global_user if global_configured else None),
            "smtp_host": spec_host if spec_configured else (global_host if global_configured else None),
            "expected_domain": domain,
            "status": status,
            "details": details
        })

    return {
        "summary": {
            "has_critical_errors": has_critical_errors,
            "has_warnings": has_warnings,
            "global_smtp_user": global_user if global_configured else None,
            "global_smtp_host": global_host if global_configured else None
        },
        "report": report
    }

@router.post("/qa/send-test-email")
async def send_test_email(project: str, email: str):
    project = project.upper()
    if project == "BOTICA":
        from app.core.mailer import send_botica_order_customer, send_botica_order_team
        r1 = await send_botica_order_customer("Cliente Prueba Botica", email, "<ul><li>1x Ritual Adaptógenos Reset - $450 MXN</li></ul>", 450.0)
        r2 = await send_botica_order_team("Cliente Prueba Botica", email, "3336762545", "Av. Paseo Natura 40, Zapopan", "<ul><li>1x Ritual Adaptógenos Reset - $450 MXN</li></ul>", 450.0)
        return {"project": project, "customer_sent": r1, "team_sent": r2}
    elif project == "HEALTHYICE":
        from pydantic import BaseModel
        class TempForm(BaseModel):
            nombre: str
            email: str
            telefono: str
            mensaje: str
            honeypot: str = None
        form = TempForm(nombre="Prueba HealthyIce", email=email, telefono="3336762545", mensaje="Esta es una prueba de contacto de HealthyIce")
        from app.core.mailer import send_healthyice_order_customer, send_healthyice_order_team
        r1 = await send_healthyice_order_customer(form)
        r2 = await send_healthyice_order_team(form)
        return {"project": project, "customer_sent": r1, "team_sent": r2}
    elif project == "CHILECHILLON":
        from pydantic import BaseModel
        class TempChileForm(BaseModel):
            nombre: str
            apellido: str = ""
            email: str
            telefono: str
            perfil: str
            mensaje: str = ""
            honeypot: str = None
        form = TempChileForm(
            nombre="Prueba Chile Chillón",
            email=email,
            telefono="3336762545",
            perfil="Cliente Final",
            mensaje="Esta es una prueba del formulario de contacto para El Chile Chillón."
        )
        from app.core.mailer import send_chilechillon_confirmation_email, send_chilechillon_notification_team
        r1 = await send_chilechillon_confirmation_email(form)
        r2 = await send_chilechillon_notification_team(form)
        return {"project": project, "customer_sent": r1, "team_sent": r2}
    else:
        return {"error": f"Project {project} is not supported for QA tests"}
