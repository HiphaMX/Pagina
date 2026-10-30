import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import CivicNotice, CivicNoticeStatus, Community
from app.schemas.schemas import CivicNoticeOfficialCreate, CivicNoticeOut
from app.api.notices import enrich_notice

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Engine"])

ADMIN_TOKEN = os.getenv("ADMIN_SECRET_TOKEN", "natura_admin_secret_2026")


def verify_admin_token(
    x_admin_token: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
):
    """
    Verifica que la petición incluya el token de administración autorizado.
    Soporta header X-Admin-Token o Bearer token en Authorization.
    """
    token = x_admin_token
    if not token and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token or token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de administración inválido o no suministrado"
        )
    return True


@router.post("/notices/official", response_model=CivicNoticeOut, status_code=status.HTTP_201_CREATED)
def publish_official_notice(
    payload: CivicNoticeOfficialCreate,
    is_authenticated: bool = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """
    Publicación de comunicados y alertas oficiales emitidos por comités o administración de cotos.
    Protegido por token de rol. Se publica directamente en estado ACTIVE sin moderación.
    """
    if payload.community_id:
        comm = db.query(Community).filter(Community.id == payload.community_id).first()
        if not comm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El coto o comunidad especificada no existe"
            )

    now_utc = datetime.now(timezone.utc)
    # Por defecto comunicados oficiales tienen vigencia de 30 días si no se especifica fecha
    expiration = payload.expires_at or (now_utc + timedelta(days=30))

    new_notice = CivicNotice(
        id=uuid.uuid4(),
        community_id=payload.community_id,
        type=payload.type,
        title=payload.title,
        content=payload.content,
        contact_whatsapp=payload.contact_whatsapp,
        is_official=True,
        published_at=now_utc,
        expires_at=expiration,
        status=CivicNoticeStatus.ACTIVE
    )

    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)

    return enrich_notice(new_notice)


@router.post("/businesses/{id}/approve", status_code=status.HTTP_200_OK)
def approve_business(
    id: uuid.UUID,
    is_authenticated: bool = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Aprueba un comercio o microemprendimiento registrado por vecinos."""
    from app.models.models import Business, BusinessStatus
    biz = db.query(Business).filter(Business.id == id).first()
    if not biz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comercio no encontrado")
    biz.status = BusinessStatus.ACTIVE
    db.commit()
    return {"message": f"Comercio '{biz.name}' aprobado exitosamente"}
