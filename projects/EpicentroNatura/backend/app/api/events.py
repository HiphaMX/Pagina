from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import CulturalEvent, TargetAudience
from app.schemas.schemas import CulturalEventOut, RSVPResponse

router = APIRouter(prefix="/api/v1/events", tags=["Cultural Engine"])


def enrich_event(e: CulturalEvent) -> CulturalEventOut:
    """Calcula campos dinámicos de cupo y disponibilidad para el evento."""
    out = CulturalEventOut.model_validate(e)
    if e.capacity_limit is not None:
        spots_left = max(0, e.capacity_limit - e.current_rsvp_count)
        out.spots_remaining = spots_left
        out.is_sold_out = spots_left == 0
    else:
        out.spots_remaining = None
        out.is_sold_out = False
    return out


@router.get("", response_model=List[CulturalEventOut])
def list_upcoming_events(
    target_audience: Optional[TargetAudience] = Query(None, description="Filtrar por público objetivo"),
    limit: int = Query(20, ge=1, le=100, description="Límite de eventos a retornar"),
    db: Session = Depends(get_db)
):
    """
    Lista los próximos eventos culturales ordenados por fecha ascendente (start_datetime >= now()).
    Excluye eventos cancelados.
    """
    now_utc = datetime.now(timezone.utc)
    
    query = (
        db.query(CulturalEvent)
        .filter(
            CulturalEvent.start_datetime >= now_utc,
            CulturalEvent.is_cancelled == False  # noqa: E712
        )
    )

    if target_audience and target_audience != TargetAudience.ALL:
        query = query.filter(
            (CulturalEvent.target_audience == target_audience) |
            (CulturalEvent.target_audience == TargetAudience.ALL)
        )

    events = query.order_by(CulturalEvent.start_datetime.asc()).limit(limit).all()
    return [enrich_event(e) for e in events]


@router.get("/{id}", response_model=CulturalEventOut)
def get_event_by_id(id: UUID, db: Session = Depends(get_db)):
    """Obtiene el detalle de un evento cultural por su ID."""
    event = db.query(CulturalEvent).filter(CulturalEvent.id == id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento cultural no encontrado")
    return enrich_event(event)


@router.post("/{id}/rsvp", response_model=RSVPResponse)
def rsvp_to_event(id: UUID, db: Session = Depends(get_db)):
    """
    Incremento atómico de cupo para un evento si no supera capacity_limit.
    Protegido contra condiciones de carrera concurrentes a nivel de base de datos.
    """
    # Ejecutar actualización atómica condicionada
    stmt = (
        update(CulturalEvent)
        .where(
            CulturalEvent.id == id,
            CulturalEvent.is_cancelled == False,  # noqa: E712
            (
                (CulturalEvent.capacity_limit == None) |  # Sin límite  # noqa: E711
                (CulturalEvent.current_rsvp_count < CulturalEvent.capacity_limit)
            )
        )
        .values(current_rsvp_count=CulturalEvent.current_rsvp_count + 1)
    )

    result = db.execute(stmt)
    db.commit()

    if result.rowcount > 0:
        # Éxito: obtener estado actualizado
        updated_event = db.query(CulturalEvent).filter(CulturalEvent.id == id).first()
        spots_left = None
        if updated_event.capacity_limit is not None:
            spots_left = max(0, updated_event.capacity_limit - updated_event.current_rsvp_count)
            
        return RSVPResponse(
            success=True,
            message="¡Tu registro ha sido confirmado exitosamente!",
            event_id=id,
            current_rsvp_count=updated_event.current_rsvp_count,
            spots_remaining=spots_left
        )

    # Si no se afectó ninguna fila, diagnosticar la causa exacta
    existing = db.query(CulturalEvent).filter(CulturalEvent.id == id).first()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento solicitado no existe"
        )
    if existing.is_cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El evento ha sido cancelado"
        )
    if existing.capacity_limit is not None and existing.current_rsvp_count >= existing.capacity_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lo sentimos, el cupo para este evento está completamente agotado"
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No fue posible completar el registro"
    )
