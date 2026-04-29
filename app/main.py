from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, webflow, dam_curador, contact
from app.core.database import Base, engine

import logging

# Create tables if not using Alembic migrations
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.warning(f"Could not create database tables: {e}")

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
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])

@app.get("/")
def read_root():
    return {"message": "Welcome to HiphaMX API"}
    
import os

curador_dir = "projects/DAM/app_curador"
if os.path.exists(curador_dir):
    app.mount("/curador", StaticFiles(directory=curador_dir, html=True), name="curador")
else:
    logging.warning(f"Static directory not found: {curador_dir}")
