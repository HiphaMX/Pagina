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

@router.get("/debug-smtp")
def debug_smtp():
    from app.core.config import settings
    return {
        "AMDI_SMTP_HOST": settings.AMDI_SMTP_HOST,
        "AMDI_SMTP_PORT": settings.AMDI_SMTP_PORT,
        "AMDI_SMTP_USER": settings.AMDI_SMTP_USER,
        "AMDI_SMTP_PASSWORD_LEN": len(settings.AMDI_SMTP_PASSWORD),
        "SMTP_HOST": settings.SMTP_HOST,
        "SMTP_PORT": settings.SMTP_PORT,
        "SMTP_USER": settings.SMTP_USER,
        "SMTP_PASSWORD_LEN": len(settings.SMTP_PASSWORD),
    }


