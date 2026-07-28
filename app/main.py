from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import contact, mercadopago, auth, sat, qa, visual_generator
from app.api.dashboard import routes as dashboard_routes
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.chilechillon_lead import ChileChillonLead
from app.models.chilechillon_match import ChileChillonMatch
from app.models.sat import SatAccount, SatInvoice, SatDownloadRequest
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
app.include_router(sat.router, prefix="/api/sat", tags=["sat"])
app.include_router(qa.router, prefix="/api", tags=["qa"])
app.include_router(visual_generator.router, prefix="/api/generator", tags=["generator"])



HOST_PROJECT_MAP = {
    "jessicamendozabienesraices": "JessicaMendoza",
    "urologia-avanzada": "urologia-avanzada",
    "amdi": "AMDI",
    "valenciaservicios": "ValenciaServicios",
    "elchilechillon": "ChileChillon",
    "whiteclean": "WhiteClean",
    "healthyice": "HealthyIce",
    "botica-silvestre": "BoticaSilvestre",
    "uro-oncology": "uro-oncology"
}

@app.get("/")
def read_root(request: Request):
    host = request.headers.get("host", "").lower()
    for keyword, folder in HOST_PROJECT_MAP.items():
        if keyword in host:
            index_path = os.path.join("projects", folder, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
    return {"message": "Welcome to HiphaMX API"}

@app.get("/{path_name:path}")
def serve_client_static(request: Request, path_name: str):
    host = request.headers.get("host", "").lower()
    
    # Determinar qué proyecto corresponde al host
    project_dir = None
    for keyword, folder in HOST_PROJECT_MAP.items():
        if keyword in host:
            project_dir = folder
            break
            
    if not project_dir:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not Found")
        
    file_path = os.path.join("projects", project_dir, path_name)
    
    # Verificar si el archivo físico existe
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
        
    # Si no existe, verificar si agregando .html existe (para URLs limpias)
    html_file_path = f"{file_path}.html"
    if os.path.exists(html_file_path) and os.path.isfile(html_file_path):
        return FileResponse(html_file_path)
        
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Not Found")


# Servir la carpeta de proyectos locales si existe
if os.path.exists("projects"):
    app.mount("/projects", StaticFiles(directory="projects"), name="projects")

# trigger: force vercel rebuild for AMDI reCAPTCHA - v15



