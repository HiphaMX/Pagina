import io
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from app.models.quotation import Quotation
from app.schemas.quotation import (
    QuotationItemSchema,
    QuotationCreateSchema,
    QuotationResponseSchema,
    CatalogServiceItem,
)
from app.services.quotations.quotation_pdf import generate_quotation_pdf


router = APIRouter()

# Catálogo oficial de servicios y planes de Hipha
OFFICIAL_CATALOG = [
    {
        "id": "identidad-grafica",
        "name": "Identidad Gráfica",
        "category": "Servicio Adicional",
        "description": "Logotipo / ADN de marca y Manual de uso de marca.",
        "price": 3770.0,
        "unit_label": "x proyecto",
        "is_custom": False,
    },
    {
        "id": "diseno-grafico",
        "name": "Diseño Gráfico",
        "category": "Servicio Adicional",
        "description": "Piezas para identidad y herramientas comerciales.",
        "price": 770.0,
        "unit_label": "base / hr",
        "is_custom": False,
    },
    {
        "id": "product-shot",
        "name": "Product Shot",
        "category": "Servicio Adicional",
        "description": "Fotografía profesional de producto en estudio con retoque digital.",
        "price": 470.0,
        "unit_label": "x pz",
        "is_custom": False,
    },
    {
        "id": "registro-fotografico",
        "name": "Registro Fotográfico",
        "category": "Servicio Adicional",
        "description": "Sesión en locación de espacios o producto en uso.",
        "price": 2770.0,
        "unit_label": "x sesión",
        "is_custom": False,
    },
    {
        "id": "video-ia",
        "name": "Video IA",
        "category": "Servicio Adicional",
        "description": "Generación y edición de video con inteligencia artificial (máx 60 seg).",
        "price": 770.0,
        "unit_label": "x video",
        "is_custom": False,
    },
    {
        "id": "email-emprende",
        "name": "E-mail Emprende",
        "category": "Servicio Adicional",
        "description": "5 cuentas de correo corporativo para clientes con sitio web.",
        "price": 770.0,
        "unit_label": "x paquete",
        "is_custom": False,
    },
    {
        "id": "plan-web-mensual",
        "name": "Plan Web (Mensual)",
        "category": "Suscripción",
        "description": "Desarrollo web corporativo, hosting, dominio y soporte técnico continuo (12 meses obligatorios).",
        "price": 770.0,
        "unit_label": "/ mes",
        "is_custom": False,
    },
    {
        "id": "plan-web-anual",
        "name": "Plan Web (Anual)",
        "category": "Suscripción",
        "description": "Desarrollo web corporativo completo, hosting de alta velocidad, dominio y mantenimiento anual.",
        "price": 7760.0,
        "unit_label": "/ año",
        "is_custom": False,
    },
    {
        "id": "plan-design",
        "name": "Plan Design",
        "category": "Suscripción",
        "description": "Solicitudes ilimitadas de diseño gráfico, artes publicitarios y branding continuo.",
        "price": 2770.0,
        "unit_label": "/ mes",
        "is_custom": False,
    },
    {
        "id": "plan-mkt",
        "name": "Plan MKT",
        "category": "Suscripción",
        "description": "Departamento de marketing externo integral: Web + Diseño ilimitado + Campañas y Correos.",
        "price": 7760.0,
        "unit_label": "/ mes",
        "is_custom": False,
    },
]


def _get_flexible_user(
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Optional[UserSchema]:
    """Permite autenticación por Bearer header o parámetro token para descargas directas en el navegador."""
    from app.main import app
    if get_current_active_user in app.dependency_overrides:
        return app.dependency_overrides[get_current_active_user]()
    if token:
        try:
            from jose import jwt
            from app.schemas.token import TokenPayload
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            token_data = TokenPayload(**payload)
            from app.models.user import User
            user = db.query(User).filter(User.email == token_data.sub).first()
            if user and user.is_active:
                return user
        except Exception:
            pass
    return None


def generate_next_folio(db: Session) -> str:
    """Genera un folio correlativo del año en curso, por ejemplo HIP-2026-0001."""
    year = datetime.datetime.now().year
    prefix = f"HIP-{year}-"
    last_q = (
        db.query(Quotation)
        .filter(Quotation.folio.like(f"{prefix}%"))
        .order_by(desc(Quotation.id))
        .first()
    )
    if last_q and last_q.folio:
        try:
            num = int(last_q.folio.replace(prefix, ""))
            return f"{prefix}{num + 1:04d}"
        except Exception:
            pass
    count = db.query(Quotation).count()
    return f"{prefix}{count + 1:04d}"


@router.get("/catalog", response_model=List[CatalogServiceItem])
def get_quotation_catalog(
    current_user: UserSchema = Depends(get_current_active_user),
):
    """Devuelve los servicios y planes oficiales de Hipha para alimentar el cotizador rápido."""
    return OFFICIAL_CATALOG


@router.post("/generate-pdf")
def generate_quotation_pdf_stream(
    payload: QuotationCreateSchema,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Genera el PDF en vivo a partir de los datos ingresados en el cotizador
    sin necesidad de haber guardado previamente en base de datos.
    """
    effective_folio = payload.folio or generate_next_folio(db)
    quotation_data = payload.model_dump()
    quotation_data["folio"] = effective_folio

    try:
        pdf_bytes = generate_quotation_pdf(quotation_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando el documento PDF: {str(e)}")

    safe_filename = f"Cotizacion_{effective_folio}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "X-Quotation-Folio": effective_folio,
        },
    )


@router.get("/direct-pdf/{quotation_id}")
def download_quotation_pdf_direct(
    quotation_id: int,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth_user: Optional[UserSchema] = Depends(_get_flexible_user),
):
    """Descarga directa del PDF de una cotización guardada, accesible vía token query o sesión."""
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    quotation_data = {
        "folio": quotation.folio,
        "client_name": quotation.client_name,
        "client_contact": quotation.client_contact,
        "client_email": quotation.client_email,
        "client_phone": quotation.client_phone,
        "date": quotation.date,
        "validity_days": quotation.validity_days,
        "items": quotation.items_json,
        "apply_tax": quotation.apply_tax,
        "tax_rate": quotation.tax_rate,
        "tax_amount": quotation.tax_amount,
        "down_payment_rate": quotation.down_payment_rate,
        "notes": quotation.notes,
    }

    try:
        pdf_bytes = generate_quotation_pdf(quotation_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando el documento PDF: {str(e)}")

    safe_filename = f"Cotizacion_{quotation.folio}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'},
    )


@router.get("/", response_model=List[QuotationResponseSchema])
def list_quotations(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user),
):
    """Lista las cotizaciones creadas en orden cronológico descendente."""
    records = (
        db.query(Quotation)
        .order_by(desc(Quotation.id))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return records


@router.post("/", response_model=QuotationResponseSchema)
def create_quotation(
    payload: QuotationCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user),
):
    """Guarda una nueva cotización en el historial del dashboard."""
    folio = payload.folio or generate_next_folio(db)

    # Validar unicidad de folio si fue provisto a mano
    existing = db.query(Quotation).filter(Quotation.folio == folio).first()
    if existing:
        folio = generate_next_folio(db)

    # Calcular subtotales
    subtotal = 0.0
    items_list = []
    for it in payload.items:
        it_dict = it.model_dump()
        qty = float(it_dict.get("quantity", 1.0))
        unit = float(it_dict.get("unit_price", 0.0))
        it_sub = round(qty * unit, 2)
        it_dict["subtotal"] = it_sub
        subtotal += it_sub
        items_list.append(it_dict)

    subtotal = round(subtotal, 2)
    tax_rate = payload.tax_rate if payload.apply_tax else 0.0
    tax_amount = round(subtotal * tax_rate, 2) if payload.apply_tax else 0.0
    total = round(subtotal + tax_amount, 2)

    down_payment_rate = payload.down_payment_rate or 0.50
    down_payment_amount = round(total * down_payment_rate, 2)

    new_quotation = Quotation(
        folio=folio,
        client_name=payload.client_name,
        client_contact=payload.client_contact,
        client_email=payload.client_email,
        client_phone=payload.client_phone,
        client_id=payload.client_id,
        date=payload.date or datetime.datetime.now(),
        validity_days=payload.validity_days,
        currency=payload.currency or "MXN",
        items_json=items_list,
        subtotal=subtotal,
        apply_tax=payload.apply_tax,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        total=total,
        down_payment_rate=down_payment_rate,
        down_payment_amount=down_payment_amount,
        notes=payload.notes,
        status=payload.status or "BORRADOR",
    )

    db.add(new_quotation)
    db.commit()
    db.refresh(new_quotation)
    return new_quotation


@router.get("/{quotation_id}", response_model=QuotationResponseSchema)
def get_quotation_by_id(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user),
):
    """Consulta los datos de una cotización específica."""
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return quotation


@router.delete("/{quotation_id}")
def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user),
):
    """Elimina una cotización del historial."""
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    db.delete(quotation)
    db.commit()
    return {"success": True, "message": f"Cotización {quotation.folio} eliminada exitosamente"}
