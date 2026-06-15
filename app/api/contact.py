from fastapi import APIRouter
from app.api.projects import hipha, chilechillon, healthyice, whiteclean, grupogari

router = APIRouter()

router.include_router(hipha.router)
router.include_router(chilechillon.router)
router.include_router(healthyice.router)
router.include_router(whiteclean.router)
router.include_router(grupogari.router)
