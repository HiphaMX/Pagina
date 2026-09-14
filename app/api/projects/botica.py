import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db, Base, engine
from app.core.config import settings
from app.models.botica_product import BoticaProduct

router = APIRouter()
logger = logging.getLogger(__name__)

# Catálogo inicial con todos los productos y variantes de Botica Silvestre
DEFAULT_BOTICA_CATALOG = [
    # Soul Shine
    {"slug": "focus-tintura", "base_name": "Focus", "format": "Tintura", "display_name": "Focus - Tintura", "category": "Soul Shine", "price": 490.0, "stock": 10, "image_url": "assets/images/Product Shots/Focus 01.webp"},
    {"slug": "focus-oleato", "base_name": "Focus", "format": "Oleato", "display_name": "Focus - Oleato", "category": "Soul Shine", "price": 490.0, "stock": 10, "image_url": "assets/images/Product Shots/Focus 01.webp"},
    {"slug": "balance-tintura", "base_name": "Balance", "format": "Tintura", "display_name": "Balance - Tintura", "category": "Soul Shine", "price": 490.0, "stock": 10, "image_url": "assets/images/Product Shots/Balance 01.webp"},
    {"slug": "balance-oleato", "base_name": "Balance", "format": "Oleato", "display_name": "Balance - Oleato", "category": "Soul Shine", "price": 490.0, "stock": 10, "image_url": "assets/images/Product Shots/Balance 01.webp"},
    {"slug": "energy-tintura", "base_name": "Energy+", "format": "Tintura", "display_name": "Energy+ - Tintura", "category": "Soul Shine", "price": 490.0, "stock": 10, "image_url": "assets/images/Product Shots/Energy 01.webp"},
    {"slug": "energy-oleato", "base_name": "Energy+", "format": "Oleato", "display_name": "Energy+ - Oleato", "category": "Soul Shine", "price": 490.0, "stock": 10, "image_url": "assets/images/Product Shots/Energy 01.webp"},
    {"slug": "emuna-tintura", "base_name": "Emuná", "format": "Tintura", "display_name": "Emuná - Tintura", "category": "Soul Shine", "price": 490.0, "stock": 10, "image_url": "assets/images/Product Shots/Emuna 01.webp"},
    {"slug": "emuna-oleato", "base_name": "Emuná", "format": "Oleato", "display_name": "Emuná - Oleato", "category": "Soul Shine", "price": 490.0, "stock": 10, "image_url": "assets/images/Product Shots/Emuna 01.webp"},
    {"slug": "mindii-tintura", "base_name": "Mindii", "format": "Tintura", "display_name": "Mindii - Tintura", "category": "Soul Shine", "price": 490.0, "stock": 10, "image_url": "assets/images/Product Shots/Mindii 01.webp"},
    {"slug": "smile-tintura", "base_name": "Smile", "format": "Tintura", "display_name": "Smile - Tintura", "category": "Soul Shine", "price": 690.0, "stock": 10, "image_url": "assets/images/Product Shots/Smile 01.webp"},
    {"slug": "smile-oleato", "base_name": "Smile", "format": "Oleato", "display_name": "Smile - Oleato", "category": "Soul Shine", "price": 690.0, "stock": 10, "image_url": "assets/images/Product Shots/Smile 01.webp"},
    {"slug": "mystic-tintura", "base_name": "Mystic", "format": "Tintura", "display_name": "Mystic - Tintura", "category": "Soul Shine", "price": 990.0, "stock": 10, "image_url": "assets/images/Product Shots/Mystic 01.webp"},
    {"slug": "mystic-oleato", "base_name": "Mystic", "format": "Oleato", "display_name": "Mystic - Oleato", "category": "Soul Shine", "price": 990.0, "stock": 10, "image_url": "assets/images/Product Shots/Mystic 01.webp"},
    {"slug": "armonizador-spray", "base_name": "Armonizador", "format": "Spray", "display_name": "Armonizador - Spray", "category": "Soul Shine", "price": 59.0, "stock": 10, "image_url": "assets/images/Product Shots/Armonizador1.webp"},

    # Sabina
    {"slug": "calma-tintura", "base_name": "Calma", "format": "Tintura", "display_name": "Calma - Tintura", "category": "Sabina", "price": 390.0, "stock": 10, "image_url": "assets/images/Product Shots/Sabina/Calma 01.webp"},
    {"slug": "descansa-tintura", "base_name": "Descansa", "format": "Tintura", "display_name": "Descansa - Tintura", "category": "Sabina", "price": 390.0, "stock": 10, "image_url": "assets/images/Product Shots/Sabina/Descansa 01.webp"},
    {"slug": "equilibra-tintura", "base_name": "Equilibra", "format": "Tintura", "display_name": "Equilibra - Tintura", "category": "Sabina", "price": 390.0, "stock": 10, "image_url": "assets/images/Product Shots/Sabina/Equilibra 01.webp"},
    {"slug": "luna-tintura", "base_name": "Luna", "format": "Tintura", "display_name": "Luna - Tintura", "category": "Sabina", "price": 390.0, "stock": 10, "image_url": "assets/images/Product Shots/Sabina/Luna 01.webp"},
    {"slug": "suena-tintura", "base_name": "Sueña", "format": "Tintura", "display_name": "Sueña - Tintura", "category": "Sabina", "price": 390.0, "stock": 10, "image_url": "assets/images/Product Shots/Sabina/Suena 01.webp"},

    # Pomadas
    {"slug": "colita-de-rana-pomada", "base_name": "Colita de Rana", "format": "Pomada", "display_name": "Colita de Rana - Pomada", "category": "Pomadas", "price": 190.0, "stock": 10, "image_url": "assets/images/Product Shots/Colita de rana1.webp"},
    {"slug": "abacho-pomada", "base_name": "Abacho", "format": "Pomada", "display_name": "Abacho - Pomada", "category": "Pomadas", "price": 190.0, "stock": 10, "image_url": "assets/images/Product Shots/Abacho1.webp"},
    {"slug": "descansa-pomada", "base_name": "Descansa (Pomada)", "format": "Pomada", "display_name": "Descansa (Pomada) - Pomada", "category": "Pomadas", "price": 190.0, "stock": 10, "image_url": "assets/images/Product Shots/Descansa1.webp"},
    {"slug": "piel-silvestre-pomada", "base_name": "Piel Silvestre", "format": "Pomada", "display_name": "Piel Silvestre - Pomada", "category": "Pomadas", "price": 250.0, "stock": 10, "image_url": "assets/images/Product Shots/PielSilvestre1.webp"},
    {"slug": "fluye-pomada", "base_name": "Fluye", "format": "Pomada", "display_name": "Fluye - Pomada", "category": "Pomadas", "price": 190.0, "stock": 10, "image_url": "assets/images/Product Shots/Fluye1.webp"},
]

def seed_botica_catalog(db: Session):
    """Inicializa el catálogo si la tabla botica_products está vacía."""
    try:
        count = db.query(BoticaProduct).count()
        if count == 0:
            logger.info("Sembrando catálogo inicial de Botica Silvestre...")
            for item in DEFAULT_BOTICA_CATALOG:
                prod = BoticaProduct(
                    slug=item["slug"],
                    base_name=item["base_name"],
                    format=item["format"],
                    display_name=item["display_name"],
                    category=item["category"],
                    price=item["price"],
                    stock=item["stock"],
                    is_active=True,
                    image_url=item.get("image_url")
                )
                db.add(prod)
            db.commit()
            logger.info("✓ Catálogo inicial de Botica Silvestre sembrado con éxito.")
    except Exception as e:
        logger.error(f"Error al sembrar catálogo de Botica Silvestre: {e}")
        db.rollback()

class AdminLoginRequest(BaseModel):
    password: str

class ProductStockUpdate(BaseModel):
    slug: str
    stock: int
    is_active: Optional[bool] = True

class BatchStockUpdateRequest(BaseModel):
    password: str
    updates: List[ProductStockUpdate]

def verify_botica_admin(password: str) -> bool:
    expected = getattr(settings, "BOTICA_ADMIN_PASSWORD", "Mibotic4_2026")
    return password.strip() == expected.strip()

@router.get("/stock")
def get_botica_stock(db: Session = Depends(get_db)):
    """
    Devuelve la lista completa de productos y un mapa de existencias para el frontend.
    Ejecuta auto-seeding si la base de datos está vacía.
    """
    Base.metadata.create_all(bind=engine)
    seed_botica_catalog(db)

    products = db.query(BoticaProduct).order_by(BoticaProduct.id).all()
    
    items_data = []
    stock_map = {}
    
    for p in products:
        item = {
            "id": p.id,
            "slug": p.slug,
            "base_name": p.base_name,
            "format": p.format,
            "display_name": p.display_name,
            "category": p.category,
            "price": p.price,
            "stock": p.stock,
            "is_active": p.is_active,
            "image_url": p.image_url,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None
        }
        items_data.append(item)
        
        # Mapa de consulta rápida para frontend (por slug y por display_name)
        stock_map[p.slug] = {
            "stock": p.stock,
            "is_active": p.is_active,
            "price": p.price
        }
        stock_map[p.display_name] = {
            "stock": p.stock,
            "is_active": p.is_active,
            "price": p.price
        }
        # También permitir consulta por clave combinada minúscula "base_name - format"
        combined_key = f"{p.base_name} - {p.format}".strip().lower()
        stock_map[combined_key] = {
            "stock": p.stock,
            "is_active": p.is_active,
            "price": p.price
        }

    return {
        "success": True,
        "items": items_data,
        "stock_map": stock_map
    }

@router.post("/admin/login")
def admin_login(body: AdminLoginRequest):
    """Verifica la contraseña del panel de administración."""
    if not verify_botica_admin(body.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta.")
    return {
        "success": True,
        "message": "Autenticación exitosa",
        "token": "botica_admin_session_valid"
    }

@router.post("/admin/stock")
def update_botica_stock(body: BatchStockUpdateRequest, db: Session = Depends(get_db)):
    """Actualiza en lote el stock y estado de los productos."""
    if not verify_botica_admin(body.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta.")

    updated_count = 0
    for update in body.updates:
        prod = db.query(BoticaProduct).filter(BoticaProduct.slug == update.slug).first()
        if prod:
            prod.stock = max(0, update.stock)
            if update.is_active is not None:
                prod.is_active = update.is_active
            updated_count += 1

    db.commit()
    return {
        "success": True,
        "updated_count": updated_count,
        "message": f"Se actualizaron {updated_count} productos correctamente."
    }

def deduct_botica_stock(db: Session, cart_items: list) -> Dict[str, Any]:
    """
    Descuenta del inventario los productos comprados tras confirmarse un pago.
    Utilizado por el webhook de Mercado Pago y process_payment.
    """
    deducted = []
    try:
        for item in cart_items:
            name = item.get("name") or item.get("title", "")
            qty = int(item.get("quantity", 1))
            if not name:
                continue

            # Buscar por display_name exacto
            prod = db.query(BoticaProduct).filter(BoticaProduct.display_name.ilike(name.strip())).first()
            if not prod:
                # Buscar por coincidencia parcial si el nombre incluye variante o viceversa
                prod = db.query(BoticaProduct).filter(BoticaProduct.display_name.contains(name.strip())).first()
            if not prod:
                # Buscar por base_name
                prod = db.query(BoticaProduct).filter(BoticaProduct.base_name.ilike(name.strip())).first()

            if prod:
                old_stock = prod.stock
                prod.stock = max(0, prod.stock - qty)
                deducted.append({
                    "slug": prod.slug,
                    "name": prod.display_name,
                    "old_stock": old_stock,
                    "new_stock": prod.stock,
                    "quantity": qty
                })
                logger.info(f"[STOCK DEDUCTED] {prod.display_name}: {old_stock} -> {prod.stock} (-{qty})")

        db.commit()
    except Exception as e:
        logger.error(f"Error al descontar stock de Botica: {e}")
        db.rollback()

    return {"deducted": deducted}
