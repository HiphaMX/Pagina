from app.api.businesses import router as businesses_router
from app.api.events import router as events_router
from app.api.notices import router as notices_router
from app.api.admin import router as admin_router
from app.api.common import router as common_router

__all__ = [
    "businesses_router",
    "events_router",
    "notices_router",
    "admin_router",
    "common_router",
]
