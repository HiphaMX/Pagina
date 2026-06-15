from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api import contact, mercadopago, auth
from app.api.dashboard import routes as dashboard_routes
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.chilechillon_lead import ChileChillonLead
from app.models.chilechillon_match import ChileChillonMatch
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

    # Escribir secretos de Google Analytics si estamos en Vercel
    if os.environ.get("VERCEL") == "1":
        print("Configurando secretos de Google Analytics en /tmp...")
        secrets_dir = "/tmp/.secrets"
        os.makedirs(secrets_dir, exist_ok=True)
        
        # Leer el contenido de las variables de entorno
        ga_token = os.environ.get("GA_TOKEN_JSON")
        ga_client_secret = os.environ.get("GA_CLIENT_SECRET_JSON")
        
        if ga_token:
            with open(os.path.join(secrets_dir, "token.json"), "w") as f:
                f.write(ga_token)
            print("✓ token.json configurado con éxito en /tmp.")
        else:
            print("⚠️ Advertencia: GA_TOKEN_JSON no está configurado en las variables de entorno.")
            
        if ga_client_secret:
            with open(os.path.join(secrets_dir, "client_secret.json"), "w") as f:
                f.write(ga_client_secret)
            print("✓ client_secret.json configurado con éxito en /tmp.")
        else:
            print("⚠️ Advertencia: GA_CLIENT_SECRET_JSON no está configurado en las variables de entorno.")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])
app.include_router(mercadopago.router, prefix="/api/mercadopago", tags=["mercadopago"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
def read_root():
    return {"message": "Welcome to HiphaMX API"}



