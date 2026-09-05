import os
import json
import mercadopago
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.healthyice_order import HealthyIceOrder

router = APIRouter()

# Initialize Mercado Pago SDK dynamically based on store credentials
def get_sdk_for_store(store: str = "botica"):
    if store == "healthyice":
        token = os.getenv("HEALTHYICE_MERCADOPAGO_ACCESS_TOKEN", "") or os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
    elif store == "chilechillon":
        token = os.getenv("CHILECHILLON_MERCADOPAGO_ACCESS_TOKEN", "") or os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
    else:
        token = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
    
    if not token:
        raise HTTPException(status_code=500, detail=f"Mercado Pago token is not configured for store '{store}'")
    return mercadopago.SDK(token)

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
    store: Optional[str] = "botica"

@router.post("/create_preference")
async def create_preference(cart: CartRequest, request: Request, db: Session = Depends(get_db)):
    store_name = cart.store or "botica"
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    try:
        store_sdk = get_sdk_for_store(store_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    if store_name == "healthyice":
        site_domain = "https://www.healthyice.mx"
    elif store_name == "chilechillon":
        site_domain = "https://elchilechillon.mx"
        
    backend_url = os.getenv("BACKEND_URL", "https://hipha-mx-fastapi.vercel.app")
 
    total_price = sum(item.price * item.quantity for item in cart.items)
    shipping_cost = 0.0 if total_price > 590 else 180.0
    if store_name == "healthyice":
        # HealthyIce doesn't charge shipping or handles it differently
        shipping_cost = 0.0
 
    if store_name == "healthyice":
        statement_descriptor = "HEALTHY ICE"
    elif store_name == "chilechillon":
        statement_descriptor = "CHILE CHILLON"
    else:
        statement_descriptor = "BOTICA SILVESTRE"

    preference_data = {
        "items": mp_items,
        "back_urls": {
            "success": f"{site_domain}/index.html",
            "failure": f"{site_domain}/index.html",
            "pending": f"{site_domain}/index.html"
        },
        "auto_return": "approved",
        "statement_descriptor": statement_descriptor,
        "notification_url": f"{backend_url}/api/mercadopago/webhook?store={store_name}"
    }

    if shipping_cost > 0.0:
        preference_data["shipments"] = {
            "cost": shipping_cost,
            "mode": "custom"
        }

    if cart.payer:
        preference_data["payer"] = {}
        if cart.payer.email:
            preference_data["payer"]["email"] = cart.payer.email
        if cart.payer.name:
            parts = cart.payer.name.split(" ", 1)
            preference_data["payer"]["name"] = parts[0]
            if len(parts) > 1:
                preference_data["payer"]["surname"] = parts[1]

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

        # Persistir orden borrador para HealthyIce en base de datos antes de ir a Mercado Pago
        order_id = None
        if store_name == "healthyice":
            try:
                cart_items_list = []
                for item in cart.items:
                    cart_items_list.append({
                        "name": item.name,
                        "price": item.price,
                        "quantity": item.quantity,
                        "image": item.image
                    })
                new_order = HealthyIceOrder(
                    nombre=payer_name,
                    email=payer_email,
                    telefono=payer_phone,
                    direccion=address_str,
                    carrito_items=json.dumps(cart_items_list),
                    total=total_price,
                    status="pending_payment"
                )
                db.add(new_order)
                db.commit()
                db.refresh(new_order)
                order_id = new_order.id
            except Exception as db_err:
                print(f"Error al guardar orden pre-pago: {db_err}")

        preference_data["metadata"] = {
            "cart_html": order_details_html,
            "payer_name": payer_name,
            "payer_email": payer_email,
            "payer_phone": payer_phone,
            "address": address_str,
            "total": str(total_with_shipping),
            "store": store_name,
            "order_id": str(order_id) if order_id else ""
        }

    try:
        preference_response = store_sdk.preference().create(preference_data)
        preference = preference_response.get("response", {})
        
        if store_name == "healthyice":
            token_for_sandbox = os.getenv("HEALTHYICE_MERCADOPAGO_ACCESS_TOKEN", "") or os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
        elif store_name == "chilechillon":
            token_for_sandbox = os.getenv("CHILECHILLON_MERCADOPAGO_ACCESS_TOKEN", "") or os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
        else:
            token_for_sandbox = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
        is_sandbox = token_for_sandbox.startswith("TEST-")
        init_point_key = "sandbox_init_point" if is_sandbox else "init_point"
        
        if init_point_key not in preference:
            raise Exception(f"No {init_point_key} in response")
            
        return {"init_point": preference[init_point_key], "id": preference.get("id")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def mercadopago_webhook(request: Request, store: str = "botica", db: Session = Depends(get_db)):
    payload = await request.json()
    action = payload.get("action") or payload.get("type") or payload.get("topic")
    
    if action in ["payment.created", "payment.updated", "payment"]:
        payment_id = payload.get("data", {}).get("id")
        if payment_id:
            try:
                store_sdk = get_sdk_for_store(store)
                payment_info = store_sdk.payment().get(payment_id)
                payment = payment_info.get("response", {})
                status = payment.get("status")
                
                if status == "approved":
                    metadata = payment.get("metadata", {})
                    # Mercado Pago might return empty metadata or we might not have email.
                    payer_email = metadata.get("payer_email")
                    if payer_email:
                        import asyncio
                        store_name = metadata.get("store") or "botica"
                        
                        payer_name = metadata.get("payer_name", "Cliente")
                        payer_phone = metadata.get("payer_phone", "")
                        address_str = metadata.get("address", "")
                        cart_html = metadata.get("cart_html", "")
                        total = float(metadata.get("total", 0.0))
                        order_id_str = metadata.get("order_id")
                        
                        if store_name == "healthyice":
                            # Actualizar la orden local a "paid" (pagado)
                            if order_id_str:
                                try:
                                    order_id = int(order_id_str)
                                    order = db.query(HealthyIceOrder).filter(HealthyIceOrder.id == order_id).first()
                                    if order:
                                        order.status = "paid"
                                        order.mercadopago_payment_id = str(payment_id)
                                        db.commit()
                                except Exception as db_err:
                                    print(f"Error al actualizar orden {order_id_str} en webhook: {db_err}")

                            from app.core.mailer import send_healthyice_payment_customer, send_healthyice_payment_team
                            asyncio.create_task(send_healthyice_payment_customer(payer_name, payer_email, cart_html, total))
                            asyncio.create_task(send_healthyice_payment_team(payer_name, payer_email, payer_phone, address_str, cart_html, total))
                        elif store_name == "chilechillon":
                            from app.core.mailer import send_chilechillon_order_customer, send_chilechillon_order_team
                            asyncio.create_task(send_chilechillon_order_customer(payer_name, payer_email, cart_html, total))
                            asyncio.create_task(send_chilechillon_order_team(payer_name, payer_email, payer_phone, address_str, cart_html, total))
                        else:
                            from app.core.mailer import send_botica_order_customer, send_botica_order_team
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
    store: Optional[str] = "botica"


@router.get("/config")
def get_mercadopago_config(store: str = "botica"):
    if store == "healthyice":
        pub_key = os.getenv("HEALTHYICE_MERCADOPAGO_PUBLIC_KEY", "") or os.getenv("MERCADOPAGO_PUBLIC_KEY", "")
    elif store == "chilechillon":
        pub_key = os.getenv("CHILECHILLON_MERCADOPAGO_PUBLIC_KEY", "") or os.getenv("MERCADOPAGO_PUBLIC_KEY", "")
    else:
        pub_key = os.getenv("MERCADOPAGO_PUBLIC_KEY", "")
    return {"public_key": pub_key}


@router.post("/process_payment")
async def process_payment(payload: PaymentRequest):
    store_name = payload.store or "botica"
    try:
        store_sdk = get_sdk_for_store(store_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

    if store_name == "healthyice":
        description = "Pedido HealthyIce"
    elif store_name == "chilechillon":
        description = "Pedido Chile Chillón"
    else:
        description = "Pedido Botica Silvestre"

    payment_data = {
        "transaction_amount": payload.transaction_amount,
        "token": payload.token,
        "description": description,
        "payment_method_id": payload.payment_method_id,
        "installments": payload.installments,
        "payer": {
            "email": payload.payer.email,
            "first_name": first_name,
            "last_name": last_name
        },
        "notification_url": f"{os.getenv('BACKEND_URL', 'https://hipha-mx-fastapi.vercel.app')}/api/mercadopago/webhook?store={store_name}",
        "metadata": {
            "cart_html": cart_html,
            "payer_name": payer_name,
            "payer_email": payload.payer.email,
            "payer_phone": payer_phone,
            "address": address_str,
            "total": str(payload.transaction_amount),
            "store": store_name
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
        payment_response = store_sdk.payment().create(payment_data)
        payment = payment_response.get("response", {})
        status = payment.get("status")
        status_detail = payment.get("status_detail")

        # If payment is approved immediately, send emails right away
        if status == "approved":
            import asyncio
            if store_name == "healthyice":
                from app.core.mailer import send_healthyice_payment_customer, send_healthyice_payment_team
                asyncio.create_task(send_healthyice_payment_customer(payer_name, payload.payer.email, cart_html, payload.transaction_amount))
                asyncio.create_task(send_healthyice_payment_team(payer_name, payload.payer.email, payer_phone, address_str, cart_html, payload.transaction_amount))
            elif store_name == "chilechillon":
                from app.core.mailer import send_chilechillon_order_customer, send_chilechillon_order_team
                asyncio.create_task(send_chilechillon_order_customer(payer_name, payload.payer.email, cart_html, payload.transaction_amount))
                asyncio.create_task(send_chilechillon_order_team(payer_name, payload.payer.email, payer_phone, address_str, cart_html, payload.transaction_amount))
            else:
                from app.core.mailer import send_botica_order_customer, send_botica_order_team
                asyncio.create_task(send_botica_order_customer(payer_name, payload.payer.email, cart_html, payload.transaction_amount))
                asyncio.create_task(send_botica_order_team(payer_name, payload.payer.email, payer_phone, address_str, cart_html, payload.transaction_amount))

        return {
            "id": payment.get("id"),
            "status": status,
            "status_detail": status_detail
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest_payments_debug")
async def latest_payments_debug(secret: str, store: str = "healthyice", db: Session = Depends(get_db)):
    if secret != "HiphaSecret2026!":
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        store_sdk = get_sdk_for_store(store)
        filters = {
            "sort": "date_created",
            "criteria": "desc",
            "limit": 15
        }
        search_response = store_sdk.payment().search(filters)
        
        orders = db.query(HealthyIceOrder).order_by(HealthyIceOrder.id.desc()).limit(10).all()
        orders_data = [
            {
                "id": o.id,
                "nombre": o.nombre,
                "email": o.email,
                "telefono": o.telefono,
                "direccion": o.direccion,
                "carrito_items": o.carrito_items,
                "total": o.total,
                "status": o.status,
                "mercadopago_payment_id": o.mercadopago_payment_id,
                "created_at": str(o.created_at)
            } for o in orders
        ]
        
        return {
            "payments": search_response.get("response", {}).get("results", []),
            "orders": orders_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

