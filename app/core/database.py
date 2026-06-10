from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

from app.core.config import settings

from sqlalchemy.pool import NullPool

db_uri = os.environ.get("DATABASE_URL") or settings.SQLALCHEMY_DATABASE_URI
if db_uri and db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

# En Vercel, el sistema de archivos raíz es de solo lectura.
# Redirigimos la base de datos SQLite a /tmp si no hay base de datos externa.
if not os.environ.get("DATABASE_URL") and os.environ.get("VERCEL") == "1":
    db_uri = "sqlite:////tmp/database.db"

if "sqlite" in db_uri:
    engine = create_engine(
        db_uri, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        db_uri,
        poolclass=NullPool,
        pool_pre_ping=True
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
