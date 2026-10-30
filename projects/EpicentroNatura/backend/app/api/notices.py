import uuid
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import (
    CivicNotice,
    CivicNoticeStatus,
    CivicNoticeType,
    Community,
    default_notice_expiration,
)
from app.schemas.schemas import CivicNoticeOut, CivicNoticeSubmit
from app.utils.whatsapp import build_whatsapp_link

router = APIRouter(prefix="/api/v1/notices", tags=["Civic & Notices Engine"])


def enrich_notice(n: CivicNotice) -> CivicNoticeOut:
    """Enriquece el modelo de aviso cívico con días restantes y link a WhatsApp."""
    now_utc = datetime.now(timezone.utc)
    # Asegurar tz-aware para calcular diferencia
    exp = n.expires_at if n.expires_at.tzinfo else n.expires_at.replace(tzinfo=timezone.utc)
    delta_days = max(0, (exp - now_utc).days)

    wa_link = None
    if n.contact_whatsapp:
        context = f"información sobre el aviso '{n.title}'"
        wa_link = build_whatsapp_link(n.contact_whatsapp, "Vecino", context)

    out = CivicNoticeOut.model_validate(n)
    out.days_remaining = delta_days
    out.whatsapp_link = wa_link
    return out


@router.get("", response_model=List[CivicNoticeOut])
def list_active_notices(
    type_filter: Optional[CivicNoticeType] = Query(None, description="Filtrar por tipo de aviso"),
    community_id: Optional[UUID] = Query(None, description="Filtrar por coto o comunidad"),
    db: Session = Depends(get_db)
):
    """
    Lista los avisos vecinales vigentes (status = active AND expires_at > now()).
    Ordenados por prioridad de alerta (alerta_zona primero, luego comunicados oficiales, luego otros).
    """
    now_utc = datetime.now(timezone.utc)

    # Definir orden de prioridad: Alerta de Zona = 1, Comunicado Oficial = 2, Otros = 3
    priority_order = case(
        (CivicNotice.type == CivicNoticeType.ALERTA_ZONA, 1),
        (CivicNotice.type == CivicNoticeType.COMUNICADO_OFICIAL, 2),
        else_=3
    )

    query = (
        db.query(CivicNotice)
        .options(joinedload(CivicNotice.community))
        .filter(
            CivicNotice.status == CivicNoticeStatus.ACTIVE,
            CivicNotice.expires_at > now_utc
        )
    )

    if type_filter:
        query = query.filter(CivicNotice.type == type_filter)

    if community_id:
        query = query.filter(
            (CivicNotice.community_id == community_id) | (CivicNotice.community_id == None)  # noqa: E711
        )

    notices = query.order_by(priority_order.asc(), CivicNotice.published_at.desc()).all()
    return [enrich_notice(n) for n in notices]


@router.post("/submit", response_model=CivicNoticeOut, status_code=status.HTTP_201_CREATED)
def submit_public_notice(payload: CivicNoticeSubmit, db: Session = Depends(get_db)):
    """
    Envío público de reporte vecinal (mascota perdida, empleo local, causa social).
    Crea el registro en estado pending_moderation con vigencia automática de 15 días.
    """
    if payload.community_id:
        comm = db.query(Community).filter(Community.id == payload.community_id).first()
        if not comm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El coto o comunidad especificada no existe"
            )

    new_notice = CivicNotice(
        id=uuid.uuid4(),
        community_id=payload.community_id,
        type=payload.type,
        title=payload.title,
        content=payload.content,
        contact_whatsapp=payload.contact_whatsapp,
        is_official=False,
        expires_at=default_notice_expiration(),
        status=CivicNoticeStatus.PENDING_MODERATION
    )

    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)

    return enrich_notice(new_notice)
