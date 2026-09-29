from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

from app.core.config import settings

from sqlalchemy.pool import NullPool

def _resolve_db_uri() -> str:
    candidate_keys = [
        "DATABASE_URL",
        "POSTGRES_URL",
        "POSTGRES_PRISMA_URL",
        "POSTGRES_URL_NON_POOLING",
        "DATABASE_URL_UNPOOLED",
        "STORAGE_URL",
        "STORAGE_DATABASE_URL",
        "STORAGE_POSTGRES_URL",
        "NEON_DATABASE_URL"
    ]
    for key in candidate_keys:
        val = os.environ.get(key)
        if val and val.strip():
            print(f"✓ Conectando a base de datos externa mediante variable '{key}'")
            return val.strip()

    if os.environ.get("VERCEL") == "1":
        return "sqlite:////tmp/database.db"

    return settings.SQLALCHEMY_DATABASE_URI

db_uri = _resolve_db_uri()
if db_uri and db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)


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

_tables_created = False

def ensure_db_initialized():
    global _tables_created
    if not _tables_created:
        try:
            Base.metadata.create_all(bind=engine)
            _tables_created = True
        except Exception as e:
            print(f"Warning: could not auto-create tables: {e}")


def get_db():
    ensure_db_initialized()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

