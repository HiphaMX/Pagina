import uuid
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import Business, BusinessCategory, BusinessStatus, BusinessType, Community
from app.schemas.schemas import BusinessOut, BusinessRegister
from app.utils.opening_hours import check_is_open_now
from app.utils.whatsapp import build_whatsapp_link
from app.utils.slug import slugify

router = APIRouter(prefix="/api/v1/businesses", tags=["Commercial Engine"])


def enrich_business(b: Business) -> BusinessOut:
    """Enriquece el modelo de negocio con estatus en vivo y link a WhatsApp."""
    is_open, status_text = check_is_open_now(b.opening_hours)
    wa_link = build_whatsapp_link(b.whatsapp_number, b.name)
    
    out = BusinessOut.model_validate(b)
    out.is_open_now = is_open
    out.opening_status_text = status_text
    out.whatsapp_link = wa_link
    return out


@router.get("", response_model=List[BusinessOut])
def list_businesses(
    category_slug: Optional[str] = Query(None, description="Filtrar por slug de categoría"),
    community_id: Optional[UUID] = Query(None, description="Filtrar por ID del coto/comunidad"),
    business_type: Optional[BusinessType] = Query(None, description="Filtrar por tipo de negocio"),
    is_home_based: Optional[bool] = Query(None, description="Filtrar por comercio en coto vs a pie de calle"),
    has_km0_badge: Optional[bool] = Query(None, description="Filtrar por Distintivo Sello Verde Km 0"),
    only_open_now: bool = Query(False, description="Mostrar únicamente comercios abiertos en tiempo real"),
    delivery_available: Optional[bool] = Query(None, description="Filtrar comercios con servicio a domicilio"),
    search: Optional[str] = Query(None, description="Búsqueda por nombre o descripción"),
    db: Session = Depends(get_db)
):
    """
    Listado del directorio comercial local con filtros avanzados y cálculo dinámico de apertura.
    """
    query = (
        db.query(Business)
        .options(joinedload(Business.category), joinedload(Business.community))
        .filter(Business.status == BusinessStatus.ACTIVE)
    )

    if category_slug:
        query = query.join(Business.category).filter(BusinessCategory.slug == category_slug)

    if community_id:
        query = query.filter(Business.community_id == community_id)

    if business_type is not None:
        query = query.filter(Business.business_type == business_type)

    if is_home_based is not None:
        query = query.filter(Business.is_home_based == is_home_based)

    if has_km0_badge is not None:
        query = query.filter(Business.has_km0_badge == has_km0_badge)

    if delivery_available is not None:
        query = query.filter(Business.delivery_available == delivery_available)

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Business.name.ilike(search_fmt)) | (Business.description.ilike(search_fmt))
        )

    results = query.order_by(Business.name.asc()).all()

    enriched_list = []
    for b in results:
        enriched = enrich_business(b)
        if only_open_now and not enriched.is_open_now:
            continue
        enriched_list.append(enriched)

    return enriched_list


@router.get("/{slug}", response_model=BusinessOut)
def get_business_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Detalle de ficha comercial con estatus de apertura calculado en tiempo real.
    """
    b = (
        db.query(Business)
        .options(joinedload(Business.category), joinedload(Business.community))
        .filter(Business.slug == slug)
        .first()
    )

    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comercio no encontrado")

    return enrich_business(b)


@router.post("/register", response_model=BusinessOut, status_code=status.HTTP_201_CREATED)
def register_business(payload: BusinessRegister, db: Session = Depends(get_db)):
    """
    Envío de solicitud de auto-registro vecinal (crea registro en estado pending_approval).
    """
    # Validar categoría
    category = db.query(BusinessCategory).filter(BusinessCategory.id == payload.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La categoría comercial con ID {payload.category_id} no existe"
        )

    # Validar comunidad si fue proporcionada
    if payload.community_id:
        community = db.query(Community).filter(Community.id == payload.community_id).first()
        if not community:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El coto o comunidad especificada no existe"
            )

    # Generar slug único
    base_slug = slugify(payload.name)
    unique_slug = base_slug
    counter = 1
    while db.query(Business).filter(Business.slug == unique_slug).first():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1

    new_business = Business(
        id=uuid.uuid4(),
        community_id=payload.community_id,
        category_id=payload.category_id,
        name=payload.name,
        slug=unique_slug,
        description=payload.description,
        business_type=payload.business_type,
        is_home_based=payload.is_home_based,
        address_reference=payload.address_reference,
        phone_number=payload.phone_number,
        whatsapp_number=payload.whatsapp_number,
        delivery_available=payload.delivery_available,
        delivery_scope=payload.delivery_scope,
        has_km0_badge=payload.has_km0_badge,
        km0_reason=payload.km0_reason,
        opening_hours=payload.opening_hours,
        status=BusinessStatus.PENDING_APPROVAL
    )

    db.add(new_business)
    db.commit()
    db.refresh(new_business)

    return enrich_business(new_business)
