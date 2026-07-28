from fastapi import APIRouter
from app.api.projects import hipha, chilechillon, healthyice, whiteclean, grupogari, valencia_servicios, amdi, letrerama, jessica_mendoza

router = APIRouter()

router.include_router(hipha.router)
router.include_router(chilechillon.router)
router.include_router(healthyice.router)
router.include_router(whiteclean.router)
router.include_router(grupogari.router)
router.include_router(valencia_servicios.router)
router.include_router(amdi.router)
router.include_router(letrerama.router)
router.include_router(jessica_mendoza.router)



