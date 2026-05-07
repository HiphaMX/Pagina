import os
import mercadopago
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Initialize Mercado Pago SDK
mp_access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
sdk = mercadopago.SDK(mp_access_token)

class CartItem(BaseModel):
    name: str
    price: float
    quantity: int
    image: Optional[str] = None

class AddressInfo(BaseModel):
    street_name: Optional[str] = None
    zip_code: Optional[str] = None

class PayerInfo(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[AddressInfo] = None

class CartRequest(BaseModel):
    items: List[CartItem]
    payer: Optional[PayerInfo] = None

@router.post("/create_preference")
async def create_preference(cart: CartRequest, request: Request):
    if not mp_access_token:
        raise HTTPException(status_code=500, detail="Mercado Pago token is not configured")

    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Define the items for Mercado Pago
    mp_items = []
    for item in cart.items:
        mp_items.append({
            "title": item.name,
            "quantity": item.quantity,
            "currency_id": "MXN",
            "unit_price": item.price,
            "picture_url": item.image if item.image and item.image.startswith("http") else None
        })

    # The success redirect URL is the Vercel site
    # This can be configured in env vars or hardcoded to botica-silvestre.com
    site_domain = os.getenv("FRONTEND_URL", "https://www.botica-silvestre.com")

    total_price = sum(item.price * item.quantity for item in cart.items)
    shipping_cost = 0.0 if total_price > 590 else 180.0

    preference_data = {
        "items": mp_items,
        "shipments": {
            "cost": shipping_cost,
            "mode": "custom"
        },
        "back_urls": {
            "success": f"{site_domain}/index.html",
            "failure": f"{site_domain}/botica.html",
            "pending": f"{site_domain}/botica.html"
        },
        "auto_return": "approved",
        "statement_descriptor": "BOTICA SILVESTRE"
    }

    if cart.payer:
        preference_data["payer"] = {}
        if cart.payer.name:
            parts = cart.payer.name.split(" ", 1)
            preference_data["payer"]["name"] = parts[0]
            if len(parts) > 1:
                preference_data["payer"]["surname"] = parts[1]
        if cart.payer.email:
            preference_data["payer"]["email"] = cart.payer.email
        if cart.payer.phone:
            preference_data["payer"]["phone"] = {"area_code": "", "number": cart.payer.phone}
        if cart.payer.address:
            preference_data["payer"]["address"] = {}
            if cart.payer.address.street_name:
                preference_data["payer"]["address"]["street_name"] = cart.payer.address.street_name
            if cart.payer.address.zip_code:
                preference_data["payer"]["address"]["zip_code"] = cart.payer.address.zip_code

    try:
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response.get("response", {})
        
        # Mercado Pago returns 'init_point' for the checkout page
        if "init_point" not in preference:
            raise Exception("No init_point in response")
            
        return {"init_point": preference["init_point"], "id": preference.get("id")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
