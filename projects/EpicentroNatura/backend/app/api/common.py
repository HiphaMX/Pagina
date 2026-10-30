from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Community, BusinessCategory
from app.schemas.schemas import CommunityOut, BusinessCategoryOut

router = APIRouter(prefix="/api/v1", tags=["Common Metadata"])


@router.get("/communities", response_model=List[CommunityOut])
def list_communities(db: Session = Depends(get_db)):
    """Lista todos los cotos, fraccionamientos vecinos y espacios públicos activos."""
    return db.query(Community).filter(Community.is_active == True).order_by(Community.name.asc()).all()  # noqa: E712


@router.get("/categories", response_model=List[BusinessCategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """Lista las categorías comerciales disponibles en la plataforma."""
    return db.query(BusinessCategory).order_by(BusinessCategory.name.asc()).all()
