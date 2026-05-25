from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

from app.core.config import settings

db_uri = settings.SQLALCHEMY_DATABASE_URI
# En Vercel, el sistema de archivos raíz es de solo lectura.
# Redirigimos la base de datos SQLite a /tmp que sí tiene permisos de escritura.
if os.environ.get("VERCEL") == "1":
    db_uri = "sqlite:////tmp/database.db"

engine = create_engine(
    db_uri, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
