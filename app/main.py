from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, webflow, dam_curador
from app.core.database import Base, engine

# Create tables if not using Alembic migrations
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HiphaMX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(webflow.router, prefix="/api/webflow", tags=["webflow"])
app.include_router(dam_curador.router, prefix="/api/dam", tags=["dam_curador"])
@app.get("/")
def read_root():
    return {"message": "Welcome to HiphaMX API"}
    
app.mount("/curador", StaticFiles(directory="projects/DAM/app_curador", html=True), name="curador")
