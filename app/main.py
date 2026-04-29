from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import contact

app = FastAPI(title="HiphaMX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contact.router, prefix="/api/contact", tags=["contact"])

@app.get("/")
def read_root():
    return {"message": "Welcome to HiphaMX API"}

