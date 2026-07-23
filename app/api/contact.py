from fastapi import APIRouter
from app.api.projects import hipha, chilechillon, healthyice, whiteclean, grupogari, valencia_servicios, amdi, letrerama

router = APIRouter()

router.include_router(hipha.router)
router.include_router(chilechillon.router)
router.include_router(healthyice.router)
router.include_router(whiteclean.router)
router.include_router(grupogari.router)
router.include_router(valencia_servicios.router)
router.include_router(amdi.router)
router.include_router(letrerama.router)

@router.get("/test-email")
async def test_email(to: str = "efe.creativo@gmail.com"):
    from app.core.mailer import _prepare_project_email, _send_smtp
    try:
        message, smtp_host, smtp_port, smtp_user, smtp_password = _prepare_project_email(
            project_prefix="AMDI",
            from_name="AMDI Test",
            from_email="contacto@amdi.mx",
            to_email=to,
            subject="Test de Entrega AMDI",
            html_content="<p>Este es un correo de prueba para validar la conexion SMTP de AMDI.</p>",
            domain="amdi.mx"
        )
        await _send_smtp(message, smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password)
        return {"status": "success", "message": "Email sent successfully", "smtp_user": smtp_user}
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}



