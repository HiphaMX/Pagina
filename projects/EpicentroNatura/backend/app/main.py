import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.api import (
    businesses_router,
    events_router,
    notices_router,
    admin_router,
    common_router,
)
from app.tasks.auto_expiry import expire_outdated_notices


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de tablas en base de datos
    print("🌱 [Epicentro Natura] Inicializando base de datos y esquemas...")
    init_db()
    # Ejecutar limpieza inicial de avisos expirados
    expire_outdated_notices()
    yield
    print("🛑 [Epicentro Natura] Apagando servicio.")


app = FastAPI(
    title="Epicentro Natura API",
    description="Ecosistema digital comunitario hiperlocal para Natura Bosque Residencial (Zapopan, Jalisco)",
    version="1.0.0",
    lifespan=lifespan
)

# Configuración de CORS para Next.js y clientes autorizados
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar Routers
app.include_router(common_router)
app.include_router(businesses_router)
app.include_router(events_router)
app.include_router(notices_router)
app.include_router(admin_router)


@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": "Epicentro Natura API",
        "zone": "Prolongación Mariano Otero, Zapopan, Jal.",
        "version": "1.0.0"
    }
