from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import contact, mercadopago, auth
from app.api.dashboard import routes as dashboard_routes

app = FastAPI(title="HiphaMX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])
app.include_router(mercadopago.router, prefix="/api/mercadopago", tags=["mercadopago"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
def read_root():
    return {"message": "Welcome to HiphaMX API"}


