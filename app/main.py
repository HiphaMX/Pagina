from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import contact, mercadopago, auth, sat, qa, visual_generator, social_tracker
from app.api.projects import botica as botica_project
from app.api.dashboard import routes as dashboard_routes
from app.core.database import Base, engine, SessionLocal, ensure_db_initialized
from app.models.user import User
from app.models.chilechillon_lead import ChileChillonLead
from app.models.chilechillon_match import ChileChillonMatch
from app.models.sat import SatAccount, SatInvoice, SatDownloadRequest
from app.models.workflow_task import WorkflowTask
from app.models.client import AgencyClient
from app.models.social_tracker import SocialAccount, SocialSnapshot
from app.core.security import get_password_hash

app = FastAPI(title="HiphaMX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    print(f"❌ Excepción no manejada en {request.method} {request.url.path}: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error del servidor: {str(exc)}", "error": str(exc)}
    )

@app.get("/api/health")
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "hiphamx-fastapi"}

@app.on_event("startup")
def startup_db_setup():
    print("Iniciando base de datos y tablas...")
    ensure_db_initialized()
    
    # Sembrar usuario administrador por defecto
    try:
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
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error durante la siembra de base de datos: {str(e)}")

    # Sembrar clientes de agencia iniciales si la tabla está vacía
    try:
        db = SessionLocal()
        try:
            client_count = db.query(AgencyClient).count()
            if client_count == 0:
                print("Sembrando clientes iniciales de agencia...")
                initial_clients = [
                    {"name": "Letrerama", "service_type": "web_design", "billing_day": 22, "monthly_fee": 6500.0, "start_date": "2024-01-15", "contact_email": "contacto@letrerama.com"},
                    {"name": "HealthyIce", "service_type": "web_design", "billing_day": 1, "monthly_fee": 7000.0, "start_date": "2024-02-01", "contact_email": "ventas@healthyice.mx"},
                    {"name": "Grupo Gari", "service_type": "complete", "billing_day": 28, "monthly_fee": 12000.0, "start_date": "2023-11-01", "contact_email": "contacto@grupo-gari.com"},
                    {"name": "AMDI", "service_type": "web_design", "billing_day": 15, "monthly_fee": 5500.0, "start_date": "2024-03-01", "contact_email": "adrianamedina@amdi.mx"},
                    {"name": "Jessica Mendoza", "service_type": "web_design", "billing_day": 10, "monthly_fee": 6000.0, "start_date": "2024-01-10", "contact_email": "jessica@jessicamendozabienesraices.com"},
                    {"name": "El Chile Chillón", "service_type": "web_design", "billing_day": 5, "monthly_fee": 5000.0, "start_date": "2024-04-01", "contact_email": "contacto@chilechillon.com"},
                    {"name": "Valencia Servicios", "service_type": "complete", "billing_day": 20, "monthly_fee": 8500.0, "start_date": "2023-09-15", "contact_email": "contacto@valenciaservicios.com"},
                    {"name": "White Clean", "service_type": "web_design", "billing_day": 3, "monthly_fee": 5500.0, "start_date": "2024-02-15", "contact_email": "contacto@whiteclean.mx"},
                    {"name": "Uro-Oncology", "service_type": "complete", "billing_day": 18, "monthly_fee": 9000.0, "start_date": "2023-08-01", "contact_email": "info@uro-oncology.com"},
                    {"name": "Centro de Urología Avanzada", "service_type": "complete", "billing_day": 18, "monthly_fee": 9000.0, "start_date": "2023-08-01", "contact_email": "drjairo@urologia-avanzada.com.mx"},
                    {"name": "Botica Silvestre", "service_type": "web_design", "billing_day": 1, "monthly_fee": 6000.0, "start_date": "2024-05-01", "contact_email": "contacto@boticasilvestre.com"},
                    {"name": "DAM Pisos", "service_type": "design", "billing_day": 25, "monthly_fee": 4500.0, "start_date": "2024-06-01", "contact_email": "info@dampisos.com"},
                    {"name": "El Ofertón del Piso", "service_type": "design", "billing_day": 25, "monthly_fee": 4500.0, "start_date": "2024-06-01", "contact_email": "contacto@ofertondelpiso.com"}
                ]
                for ic in initial_clients:
                    db.add(AgencyClient(**ic))
                db.commit()
                print(f"✓ {len(initial_clients)} clientes de agencia sembrados con éxito.")
        finally:
            db.close()
    except Exception as ce:
        print(f"Nota: Siembra de clientes iniciales omitida o error: {ce}")

    # Sembrar y ajustar líneas base históricas para cuentas monitoreadas
    try:
        import datetime
        from sqlalchemy import asc
        from app.models.social_tracker import SocialAccount, SocialSnapshot
        db = SessionLocal()
        try:
            targets = [
                {"pattern": "%elchilechillon%", "initial_followers": 567, "date": datetime.datetime(2026, 6, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)},
                {"pattern": "%tukipa%", "initial_followers": 0, "date": datetime.datetime(2026, 9, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)},
                {"pattern": "%dam_pisos%", "initial_followers": 0, "date": datetime.datetime(2026, 4, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)},
                {"pattern": "%soul_shine%", "initial_followers": 401, "date": datetime.datetime(2026, 6, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)},
            ]
            for t in targets:
                acc = db.query(SocialAccount).filter(SocialAccount.handle.ilike(t["pattern"])).first()
                if acc:
                    acc.initial_followers = t["initial_followers"]
                    acc.initial_date = t["date"]
                    base_snap = (
                        db.query(SocialSnapshot)
                        .filter(SocialSnapshot.account_id == acc.id, SocialSnapshot.recorded_at <= t["date"])
                        .first()
                    )
                    if not base_snap:
                        base_snap = SocialSnapshot(
                            account_id=acc.id,
                            followers=t["initial_followers"],
                            growth_count=0,
                            is_manual=True,
                            recorded_at=t["date"]
                        )
                        db.add(base_snap)
                    else:
                        base_snap.followers = t["initial_followers"]
            db.commit()
            print("✓ Líneas base de monitoreo social actualizadas con éxito.")
        finally:
            db.close()
    except Exception as se:
        print(f"Nota: Siembra de líneas base de redes sociales: {se}")

    # Escribir secretos de Google Analytics si estamos en Vercel
    try:
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
    except Exception as e:
        print(f"⚠️ Error configurando secretos en /tmp: {e}")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])
app.include_router(mercadopago.router, prefix="/api/mercadopago", tags=["mercadopago"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(social_tracker.router, prefix="/api/dashboard/social", tags=["social-tracker"])
app.include_router(sat.router, prefix="/api/sat", tags=["sat"])
app.include_router(qa.router, prefix="/api", tags=["qa"])
app.include_router(visual_generator.router, prefix="/api/generator", tags=["generator"])
app.include_router(botica_project.router, prefix="/api/botica", tags=["botica"])




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



