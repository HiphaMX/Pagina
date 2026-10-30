import sys
import os
from datetime import datetime, timezone
import logging

# Asegurar path para ejecución directa
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy import update
from app.database import SessionLocal
from app.models.models import CivicNotice, CivicNoticeStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AutoExpiryTask")


def expire_outdated_notices() -> int:
    """
    Evalúa todos los avisos cívicos activos cuya fecha de expiración haya pasado
    y actualiza automáticamente su estado a 'expired'.
    
    Returns:
        int: Número de avisos expirados en esta ejecución.
    """
    now_utc = datetime.now(timezone.utc)
    db = SessionLocal()
    try:
        stmt = (
            update(CivicNotice)
            .where(
                CivicNotice.status == CivicNoticeStatus.ACTIVE,
                CivicNotice.expires_at <= now_utc
            )
            .values(status=CivicNoticeStatus.EXPIRED)
        )
        
        result = db.execute(stmt)
        db.commit()
        expired_count = result.rowcount

        if expired_count > 0:
            logger.info(f"✓ Se actualizaron {expired_count} avisos cívicos a estado 'expired'.")
        else:
            logger.info("• No hay avisos cívicos vencidos pendientes de caducar.")
            
        return expired_count
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error al ejecutar tarea de expiración de avisos: {e}", exc_info=True)
        return 0
    finally:
        db.close()


def run_daemon(interval_seconds: int = 3600):
    """Ejecuta la tarea de forma recurrente en segundo plano."""
    import time
    logger.info(f"Iniciando daemon de auto-expiración (revisión cada {interval_seconds} segundos)...")
    while True:
        expire_outdated_notices()
        time.sleep(interval_seconds)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Tarea de auto-expiración de avisos de Epicentro Natura")
    parser.add_argument("--daemon", action="store_true", help="Ejecutar en bucle infinito tipo daemon")
    parser.add_argument("--interval", type=int, default=3600, help="Intervalo en segundos para modo daemon")
    args = parser.parse_args()

    if args.daemon:
        run_daemon(interval_seconds=args.interval)
    else:
        count = expire_outdated_notices()
        print(f"Finalizado. Avisos expirados: {count}")
