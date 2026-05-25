from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api import contact, mercadopago, auth
from app.api.dashboard import routes as dashboard_routes
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

app = FastAPI(title="HiphaMX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_setup():
    print("Iniciando base de datos y tablas...")
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    # Sembrar usuario administrador por defecto
    db = SessionLocal()
    try:
        admin_email = "hola@hipha.mx"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            print("Sembrando usuario administrador por defecto...")
            admin_password = os.environ.get("ADMIN_PASSWORD", "Celi@ThePug2026")
            hashed_password = get_password_hash(admin_password)
            new_admin = User(
                email=admin_email,
                hashed_password=hashed_password,
                full_name="Administrador Hipha",
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            print("✓ Usuario administrador sembrado con éxito.")
        else:
            print("✓ El usuario administrador ya existe.")
    except Exception as e:
        print(f"❌ Error durante la siembra de base de datos: {str(e)}")
        db.rollback()
    finally:
        db.close()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])
app.include_router(mercadopago.router, prefix="/api/mercadopago", tags=["mercadopago"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
def read_root():
    return {"message": "Welcome to HiphaMX API"}



