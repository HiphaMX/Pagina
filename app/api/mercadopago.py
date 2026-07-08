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

    mp_items = []
    for item in cart.items:
        mp_items.append({
            "title": item.name,
            "quantity": item.quantity,
            "currency_id": "MXN",
            "unit_price": item.price,
            "picture_url": item.image if item.image and item.image.startswith("http") else None
        })

    site_domain = os.getenv("FRONTEND_URL", "https://www.botica-silvestre.com")
    backend_url = os.getenv("BACKEND_URL", "https://hipha-mx-fastapi.vercel.app")

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
        "statement_descriptor": "BOTICA SILVESTRE",
        "notification_url": f"{backend_url}/api/mercadopago/webhook"
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

    # We add metadata here for the webhook to use later
    if cart.payer and cart.payer.email:
        total_with_shipping = total_price + shipping_cost
        order_details_html = "<ul>"
        for item in cart.items:
            order_details_html += f"<li>{item.quantity}x {item.name} - ${item.price}</li>"
        order_details_html += "</ul>"
        if shipping_cost > 0:
            order_details_html += f"<p>Envío: ${shipping_cost}</p>"
            
        payer_name = cart.payer.name or "Cliente"
        payer_email = cart.payer.email
        payer_phone = cart.payer.phone or "No provisto"
        address_str = ""
        if cart.payer.address:
            address_str = f"{cart.payer.address.street_name or ''}, CP {cart.payer.address.zip_code or ''}"

        preference_data["metadata"] = {
            "cart_html": order_details_html,
            "payer_name": payer_name,
            "payer_email": payer_email,
            "payer_phone": payer_phone,
            "address": address_str,
            "total": str(total_with_shipping)
        }

    try:
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response.get("response", {})
        
        is_sandbox = mp_access_token.startswith("TEST-")
        init_point_key = "sandbox_init_point" if is_sandbox else "init_point"
        
        if init_point_key not in preference:
            raise Exception(f"No {init_point_key} in response")
            
        return {"init_point": preference[init_point_key], "id": preference.get("id")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def mercadopago_webhook(request: Request):
    payload = await request.json()
    action = payload.get("action") or payload.get("type") or payload.get("topic")
    
    if action in ["payment.created", "payment.updated", "payment"]:
        payment_id = payload.get("data", {}).get("id")
        if payment_id:
            try:
                payment_info = sdk.payment().get(payment_id)
                payment = payment_info.get("response", {})
                status = payment.get("status")
                
                if status == "approved":
                    metadata = payment.get("metadata", {})
                    # Mercado Pago might return empty metadata or we might not have email.
                    payer_email = metadata.get("payer_email")
                    if payer_email:
                        from app.core.mailer import send_botica_order_customer, send_botica_order_team
                        import asyncio
                        
                        payer_name = metadata.get("payer_name", "Cliente")
                        payer_phone = metadata.get("payer_phone", "")
                        address_str = metadata.get("address", "")
                        cart_html = metadata.get("cart_html", "")
                        total = float(metadata.get("total", 0.0))
                        
                        # Use asyncio.create_task to not block webhook response
                        asyncio.create_task(send_botica_order_customer(payer_name, payer_email, cart_html, total))
                        asyncio.create_task(send_botica_order_team(payer_name, payer_email, payer_phone, address_str, cart_html, total))
                        
            except Exception as e:
                print(f"Webhook error: {e}")
                
    return {"status": "ok"}


class PaymentPayerIdentification(BaseModel):
    type: Optional[str] = None
    number: Optional[str] = None


class PaymentPayer(BaseModel):
    email: str
    identification: Optional[PaymentPayerIdentification] = None


class PaymentAdditionalInfo(BaseModel):
    payer_name: str
    payer_phone: str
    address: str
    cart_html: str


class PaymentRequest(BaseModel):
    token: Optional[str] = None
    issuer_id: Optional[str] = None
    payment_method_id: str
    transaction_amount: float
    installments: int
    payer: PaymentPayer
    additional_info: Optional[PaymentAdditionalInfo] = None


@router.get("/config")
def get_mercadopago_config():
    pub_key = os.getenv("MERCADOPAGO_PUBLIC_KEY", "")
    return {"public_key": pub_key}


@router.post("/process_payment")
async def process_payment(payload: PaymentRequest):
    if not mp_access_token:
        raise HTTPException(status_code=500, detail="Mercado Pago token is not configured")

    # Split name into first and last name if possible
    first_name = "Cliente"
    last_name = ""
    if payload.additional_info and payload.additional_info.payer_name:
        parts = payload.additional_info.payer_name.split(" ", 1)
        first_name = parts[0]
        if len(parts) > 1:
            last_name = parts[1]

    # Build metadata block for webhook/email notification
    cart_html = ""
    payer_name = "Cliente"
    payer_phone = ""
    address_str = ""
    if payload.additional_info:
        cart_html = payload.additional_info.cart_html
        payer_name = payload.additional_info.payer_name
        payer_phone = payload.additional_info.payer_phone
        address_str = payload.additional_info.address

    payment_data = {
        "transaction_amount": payload.transaction_amount,
        "token": payload.token,
        "description": "Pedido Botica Silvestre",
        "payment_method_id": payload.payment_method_id,
        "installments": payload.installments,
        "payer": {
            "email": payload.payer.email,
            "first_name": first_name,
            "last_name": last_name
        },
        "notification_url": f"{os.getenv('BACKEND_URL', 'https://hipha-mx-fastapi.vercel.app')}/api/mercadopago/webhook",
        "metadata": {
            "cart_html": cart_html,
            "payer_name": payer_name,
            "payer_email": payload.payer.email,
            "payer_phone": payer_phone,
            "address": address_str,
            "total": str(payload.transaction_amount)
        }
    }

    if payload.payer.identification and payload.payer.identification.type:
        payment_data["payer"]["identification"] = {
            "type": payload.payer.identification.type,
            "number": payload.payer.identification.number
        }

    if payload.issuer_id:
        payment_data["issuer_id"] = payload.issuer_id

    try:
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response.get("response", {})
        status = payment.get("status")
        status_detail = payment.get("status_detail")

        # If payment is approved immediately, send emails right away
        if status == "approved":
            from app.core.mailer import send_botica_order_customer, send_botica_order_team
            import asyncio
            asyncio.create_task(send_botica_order_customer(payer_name, payload.payer.email, cart_html, payload.transaction_amount))
            asyncio.create_task(send_botica_order_team(payer_name, payload.payer.email, payer_phone, address_str, cart_html, payload.transaction_amount))

        return {
            "id": payment.get("id"),
            "status": status,
            "status_detail": status_detail
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

