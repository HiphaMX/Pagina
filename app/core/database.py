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

try:
    if "sqlite" in db_uri:
        engine = create_engine(
            db_uri, connect_args={"check_same_thread": False}
        )
    else:
        try:
            engine = create_engine(
                db_uri,
                poolclass=NullPool,
                pool_pre_ping=True
            )
        except Exception as e_drv:
            # Fallback entre psycopg y psycopg2 si alguno no está disponible
            if "psycopg" in str(e_drv):
                if db_uri.startswith("postgresql://"):
                    alt_uri = db_uri.replace("postgresql://", "postgresql+psycopg2://", 1)
                    engine = create_engine(alt_uri, poolclass=NullPool, pool_pre_ping=True)
                elif db_uri.startswith("postgresql+psycopg://"):
                    alt_uri = db_uri.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
                    engine = create_engine(alt_uri, poolclass=NullPool, pool_pre_ping=True)
                else:
                    raise e_drv
            else:
                raise e_drv
except Exception as e_engine:
    print(f"⚠️ Error inicializando base de datos externa ({e_engine}), usando fallback SQLite en /tmp/database.db")
    db_uri = "sqlite:////tmp/database.db"
    engine = create_engine(
        db_uri, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

_tables_created = False

def ensure_db_initialized():
    global _tables_created
    if not _tables_created:
        try:
            Base.metadata.create_all(bind=engine)
            # Migración defensiva para columnas adicionales si la tabla ya existía
            try:
                from sqlalchemy import text
                is_pg = ("postgres" in str(engine.url).lower())
                
                if is_pg:
                    migration_stmts = [
                        "ALTER TABLE agency_clients ADD COLUMN IF NOT EXISTS billing_period VARCHAR DEFAULT 'monthly'",
                        "ALTER TABLE agency_clients ADD COLUMN IF NOT EXISTS requires_invoice BOOLEAN DEFAULT FALSE",
                        "ALTER TABLE agency_clients ADD COLUMN IF NOT EXISTS apply_tax_retention BOOLEAN DEFAULT FALSE",
                        "ALTER TABLE agency_clients ADD COLUMN IF NOT EXISTS tax_retention_rate FLOAT DEFAULT 1.25",
                        "ALTER TABLE workflow_tasks ADD COLUMN IF NOT EXISTS revision_hours FLOAT DEFAULT 0.0",
                        "ALTER TABLE workflow_tasks ADD COLUMN IF NOT EXISTS revisions_count INTEGER DEFAULT 0",
                        "ALTER TABLE workflow_tasks ADD COLUMN IF NOT EXISTS month_id VARCHAR DEFAULT NULL",
                        "ALTER TABLE workflow_tasks ADD COLUMN IF NOT EXISTS task_date VARCHAR DEFAULT NULL",
                        "ALTER TABLE social_accounts ADD COLUMN IF NOT EXISTS initial_followers INTEGER DEFAULT 0",
                        "ALTER TABLE social_accounts ADD COLUMN IF NOT EXISTS initial_date TIMESTAMP WITH TIME ZONE DEFAULT NULL",
                    ]
                else:
                    migration_stmts = [
                        "ALTER TABLE agency_clients ADD COLUMN billing_period VARCHAR DEFAULT 'monthly'",
                        "ALTER TABLE agency_clients ADD COLUMN requires_invoice BOOLEAN DEFAULT 0",
                        "ALTER TABLE agency_clients ADD COLUMN apply_tax_retention BOOLEAN DEFAULT 0",
                        "ALTER TABLE agency_clients ADD COLUMN tax_retention_rate FLOAT DEFAULT 1.25",
                        "ALTER TABLE workflow_tasks ADD COLUMN revision_hours FLOAT DEFAULT 0.0",
                        "ALTER TABLE workflow_tasks ADD COLUMN revisions_count INTEGER DEFAULT 0",
                        "ALTER TABLE workflow_tasks ADD COLUMN month_id VARCHAR DEFAULT NULL",
                        "ALTER TABLE workflow_tasks ADD COLUMN task_date VARCHAR DEFAULT NULL",
                        "ALTER TABLE social_accounts ADD COLUMN initial_followers INTEGER DEFAULT 0",
                        "ALTER TABLE social_accounts ADD COLUMN initial_date TIMESTAMP WITH TIME ZONE DEFAULT NULL",
                    ]

                for stmt in migration_stmts:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text(stmt))
                    except Exception:
                        pass
            except Exception as e_mig:
                print(f"Nota en proceso de migración: {e_mig}")
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

