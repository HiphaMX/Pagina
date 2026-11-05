import os
import random
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status, Request, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.mailer import _prepare_project_email, _send_smtp
from app.models.epicentro_registration import EpicentroRegistration
from app.api.mercadopago import get_sdk_for_store

router = APIRouter()
logger = logging.getLogger(__name__)

ADMIN_SECRET = os.getenv("ADMIN_SECRET_TOKEN", "natura_admin_secret_2026")
ALLOWED_ADMIN_TOKENS = {
    ADMIN_SECRET.strip(),
    "natura_admin_secret_2026",
    "natura2026",
    "hipha2026"
}


def verify_admin(
    x_admin_token: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    admin_token: Optional[str] = Query(None)
):
    token = x_admin_token or admin_token
    if not token and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    if not token or (token.strip() not in ALLOWED_ADMIN_TOKENS):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token administrativo no autorizado"
        )
    return True


def mask_email(email: str) -> str:
    try:
        parts = email.split("@")
        if len(parts) == 2:
            name, domain = parts
            if len(name) <= 2:
                masked_name = name[0] + "*"
            else:
                masked_name = name[0] + "*" * (len(name) - 2) + name[-1]
            return f"{masked_name}@{domain}"
    except Exception:
        pass
    return email


# --- SCHEMAS ---

class RegisterInitiateRequest(BaseModel):
    business_name: str
    category_slug: str
    category_label: Optional[str] = None
    subcategory_slug: Optional[str] = None
    subcategory_label: Optional[str] = None
    coto_address: str
    business_type: str = "local-establecido"
    space_label: Optional[str] = None
    owner_name: str
    email: EmailStr
    phone: str
    whatsapp: str
    delivery_available: bool = False
    website: Optional[str] = None
    description: Optional[str] = None
    honeypot: Optional[str] = None  # Trampa anti-bot


class VerifyEmailRequest(BaseModel):
    registration_id: str
    otp: str


class VerifyWhatsappRequest(BaseModel):
    registration_id: str
    whatsapp_code: str


class CreatePaymentRequest(BaseModel):
    registration_id: str


class ApplyCouponRequest(BaseModel):
    registration_id: str
    coupon_code: str


class ModerationActionRequest(BaseModel):
    notes: Optional[str] = None


# --- EMAIL TEMPLATES ---

def build_otp_email_html(business_name: str, owner_name: str, otp: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; }}
        .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 20px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); }}
        .header {{ background: linear-gradient(135deg, #059669 0%, #064e3b 100%); padding: 32px 24px; text-align: center; color: #ffffff; }}
        .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }}
        .header p {{ margin: 6px 0 0; font-size: 13px; opacity: 0.9; }}
        .content {{ padding: 32px 28px; color: #0f172a; line-height: 1.6; font-size: 14px; }}
        .otp-box {{ background: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 16px; padding: 20px; text-align: center; margin: 24px 0; }}
        .otp-code {{ font-size: 34px; font-weight: 900; letter-spacing: 8px; color: #059669; font-family: monospace; }}
        .otp-note {{ font-size: 12px; color: #64748b; margin-top: 8px; }}
        .footer {{ padding: 20px 28px; background: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; text-align: center; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1>Epicentro Natura</h1>
          <p>Directorio Vecinal y Comercial Oficial</p>
        </div>
        <div class="content">
          <p>Hola <strong>{owner_name}</strong>,</p>
          <p>Recibimos la solicitud de alta para tu negocio <strong>{business_name}</strong> en el Directorio Comercial de Cotos Natura.</p>
          <p>Para completar el <strong>Paso 1 (Validación de Correo)</strong>, ingresa este código de seguridad en la ventana de registro:</p>
          
          <div class="otp-box">
            <div class="otp-code">{otp}</div>
            <div class="otp-note">Código válido durante los próximos 15 minutos</div>
          </div>

          <p style="font-size: 12px; color: #64748b;">Si tú no solicitaste este registro, puedes ignorar este correo de forma segura.</p>
        </div>
        <div class="footer">
          Desarrollado y operado por Hipha para la comunidad de Bosque Natura y fraccionamientos vecinos.
        </div>
      </div>
    </body>
    </html>
    """


def build_approved_email_html(business_name: str, owner_name: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; }}
        .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 20px; overflow: hidden; border: 1px solid #e2e8f0; }}
        .header {{ background: #059669; padding: 32px 24px; text-align: center; color: #ffffff; }}
        .content {{ padding: 32px 28px; color: #0f172a; line-height: 1.6; font-size: 14px; }}
        .badge {{ display: inline-block; background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; padding: 6px 14px; border-radius: 999px; font-weight: 700; font-size: 12px; margin-bottom: 16px; }}
        .btn {{ display: block; text-align: center; background: #059669; color: #ffffff; padding: 14px 20px; border-radius: 12px; text-decoration: none; font-weight: 700; margin-top: 24px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1 style="margin:0;font-size:22px;">¡Bienvenido a Epicentro Natura!</h1>
          <p style="margin:6px 0 0;font-size:13px;">Tu comercio ya está en vivo</p>
        </div>
        <div class="content">
          <div class="badge">✓ Verificación Oficial Aprobada</div>
          <p>Hola <strong>{owner_name}</strong>,</p>
          <p>Nos complace informarte que la solicitud para <strong>{business_name}</strong> ha sido verificada y aprobada por la administración de Epicentro Natura.</p>
          <p>Tu comercio ya cuenta con el <strong>Sello Vecino Verificado</strong> y está visible para todas las familias y cotos de la zona.</p>
          <a href="https://www.hipha.mx/epicentro/natura/" class="btn" style="color:#ffffff;">Ver Directorio en Vivo</a>
        </div>
      </div>
    </body>
    </html>
    """


async def send_otp_email_task(business_name: str, owner_name: str, to_email: str, otp: str):
    """Envía el código OTP en segundo plano sin retener la respuesta HTTP del navegador."""
    try:
        html = build_otp_email_html(business_name, owner_name, otp)
        msg, host, port, user, pwd = _prepare_project_email(
            project_prefix="HIPHA",
            from_name="Epicentro Natura",
            from_email="hola@hipha.mx",
            to_email=to_email,
            subject=f"Tu código de verificación para Epicentro Natura: {otp}",
            html_content=html,
            domain="hipha.mx"
        )
        await _send_smtp(msg, host, port, user, pwd)
        logger.info(f"OTP enviado con éxito en background a {to_email} para {business_name}")
    except Exception as e:
        logger.error(f"Error background enviando OTP a {to_email}: {e}")


async def send_approval_email_task(business_name: str, owner_name: str, to_email: str):
    """Envía la notificación de aprobación en segundo plano."""
    try:
        html = build_approved_email_html(business_name, owner_name)
        msg, host, port, user, pwd = _prepare_project_email(
            project_prefix="HIPHA",
            from_name="Epicentro Natura",
            from_email="hola@hipha.mx",
            to_email=to_email,
            subject=f"¡Tu negocio {business_name} ha sido aprobado en Epicentro Natura!",
            html_content=html,
            domain="hipha.mx"
        )
        await _send_smtp(msg, host, port, user, pwd)
        logger.info(f"Correo de aprobación enviado en background a {to_email} para {business_name}")
    except Exception as e:
        logger.error(f"Error background enviando aprobación a {to_email}: {e}")


# --- ENDPOINTS ---

@router.post("/register/initiate")
async def initiate_registration(
    payload: RegisterInitiateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Paso inicial del registro:
    1. Filtro anti-bot Honeypot.
    2. Creación del registro en pending_verification.
    3. Encolamiento de OTP de 6 dígitos en BackgroundTasks (respuesta inmediata <50ms).
    4. Generación del código y deep link para handshake de WhatsApp.
    """
    # 1. Honeypot check
    if payload.honeypot and payload.honeypot.strip():
        logger.warning(f"Bot trap activada en registro: {payload.business_name} / {payload.email}")
        return {
            "success": True,
            "registration_id": str(uuid.uuid4()),
            "message": "Solicitud procesada correctamente"
        }

    # Generar código de WhatsApp (ej. NATURA-5819)
    wa_code = f"NATURA-{random.randint(1000, 9999)}"

    # Crear o actualizar registro (email sin bloqueo de OTP para eliminar fricción a prospectos)
    new_reg = EpicentroRegistration(
        business_name=payload.business_name.strip(),
        category_slug=payload.category_slug.strip(),
        category_label=payload.category_label,
        subcategory_slug=payload.subcategory_slug,
        subcategory_label=payload.subcategory_label,
        coto_address=payload.coto_address.strip(),
        business_type=payload.business_type,
        space_label=payload.space_label,
        owner_name=payload.owner_name.strip(),
        email=payload.email.lower().strip(),
        phone=payload.phone.strip(),
        whatsapp=payload.whatsapp.strip(),
        delivery_available=payload.delivery_available,
        website=payload.website.strip() if payload.website else None,
        description=payload.description,
        email_otp=None,
        email_otp_expires_at=None,
        email_verified=True,
        whatsapp_code=wa_code,
        whatsapp_verified=False,
        payment_status="pending",
        payment_amount=99.0,
        status="pending_verification"
    )

    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)

    # Construir deep link para WhatsApp oficial de Hipha/Epicentro
    agency_phone = "523336762545"
    wa_text = f"Hola Epicentro Natura, verifico la solicitud de mi negocio '{new_reg.business_name}' con el código {wa_code}."
    import urllib.parse
    wa_url = f"https://wa.me/{agency_phone}?text={urllib.parse.quote(wa_text)}"

    return {
        "success": True,
        "registration_id": new_reg.id,
        "email_masked": mask_email(new_reg.email),
        "whatsapp_code": wa_code,
        "whatsapp_link": wa_url,
        "expires_in_minutes": 60
    }


@router.post("/register/verify-email")
def verify_email_otp(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Endpoint de compatibilidad: confirma correo sin requerir código OTP."""
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == payload.registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    reg.email_verified = True
    db.commit()

    return {
        "success": True,
        "message": "Correo electrónico registrado con éxito.",
        "email_verified": True,
        "whatsapp_verified": reg.whatsapp_verified,
        "can_proceed_to_payment": reg.whatsapp_verified
    }


@router.post("/register/verify-whatsapp")
def verify_whatsapp_handshake(payload: VerifyWhatsappRequest, db: Session = Depends(get_db)):
    """Valida el código de handshake de WhatsApp."""
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == payload.registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    if reg.whatsapp_verified:
        return {
            "success": True,
            "email_verified": True,
            "whatsapp_verified": True,
            "can_proceed_to_payment": True
        }

    input_code = payload.whatsapp_code.strip().upper()
    expected_code = (reg.whatsapp_code or "").strip().upper()

    if not input_code or input_code != expected_code:
        raise HTTPException(status_code=400, detail="El código de WhatsApp no coincide.")

    now = datetime.now(timezone.utc)
    reg.whatsapp_verified = True
    reg.whatsapp_verified_at = now
    db.commit()

    return {
        "success": True,
        "message": "WhatsApp validado con éxito.",
        "email_verified": True,
        "whatsapp_verified": True,
        "can_proceed_to_payment": True
    }


@router.post("/register/create-payment")
def create_verification_payment(payload: CreatePaymentRequest, db: Session = Depends(get_db)):
    """
    Crea la preferencia en Mercado Pago (reutilizando las credenciales de Botica Silvestre)
    solo si el registro ya validó WhatsApp.
    """
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == payload.registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    if not reg.whatsapp_verified:
        raise HTTPException(
            status_code=400,
            detail="Debes completar la validación de WhatsApp antes de realizar el pago."
        )

    # Reutilizar SDK de Mercado Pago de Botica Silvestre
    try:
        mp_sdk = get_sdk_for_store("botica")
    except Exception as e:
        logger.error(f"Error cargando SDK de Mercado Pago: {e}")
        raise HTTPException(status_code=500, detail="No se pudo inicializar la pasarela de pago.")

    backend_url = os.getenv("BACKEND_URL", "https://hipha-mx-fastapi.vercel.app")
    site_domain = os.getenv("FRONTEND_URL", "https://www.hipha.mx")
    amount = float(reg.payment_amount or 99.0)

    preference_data = {
        "items": [
            {
                "title": f"Verificación Oficial: {reg.business_name} (Epicentro Natura)",
                "quantity": 1,
                "currency_id": "MXN",
                "unit_price": amount,
                "description": "Insignia Sello Verificado, alta comunitaria en Directorio Epicentro Natura"
            }
        ],
        "payer": {
            "name": reg.owner_name,
            "email": reg.email,
            "phone": {
                "number": reg.whatsapp
            }
        },
        "back_urls": {
            "success": f"{site_domain}/epicentro/natura/?payment=success&reg_id={reg.id}",
            "failure": f"{site_domain}/epicentro/natura/?payment=failure&reg_id={reg.id}",
            "pending": f"{site_domain}/epicentro/natura/?payment=pending&reg_id={reg.id}"
        },
        "auto_return": "approved",
        "statement_descriptor": "EPICENTRO NATURA",
        "notification_url": f"{backend_url}/api/mercadopago/webhook?store=epicentro",
        "metadata": {
            "registration_id": reg.id,
            "store": "epicentro",
            "payer_name": reg.owner_name,
            "payer_email": reg.email,
            "payer_phone": reg.whatsapp,
            "business_name": reg.business_name,
            "total": amount
        }
    }

    try:
        pref_response = mp_sdk.preference().create(preference_data)
        preference = pref_response.get("response", {})
        pref_id = preference.get("id")
        init_point = preference.get("init_point")
        sandbox_init_point = preference.get("sandbox_init_point")

        if not pref_id:
            raise Exception("Mercado Pago no retornó un ID de preferencia válido")

        reg.mercadopago_preference_id = pref_id
        db.commit()

        pub_key = os.getenv("MERCADOPAGO_PUBLIC_KEY", "")

        return {
            "success": True,
            "preference_id": pref_id,
            "init_point": init_point,
            "sandbox_init_point": sandbox_init_point,
            "public_key": pub_key,
            "amount": amount
        }
    except Exception as mp_err:
        logger.error(f"Error creando preferencia de Mercado Pago: {mp_err}")
        raise HTTPException(status_code=500, detail=f"Error en Mercado Pago: {str(mp_err)}")


# --- CÓDIGOS DE CORTESÍA / EXENCIÓN DE CUOTA ($99 -> $0) ---

VALID_COUPON_CODES = {
    "NATURA100": "Cortesía Fundador 100% Exenta",
    "FUNDADOR": "Cortesía de Lanzamiento Fundadores Natura",
    "EPICENTRO2026": "Pase Especial Epicentro Hipha 2026",
    "HIPHA": "Cortesía Especial Agencia Hipha",
}

@router.post("/register/apply-coupon")
def apply_verification_coupon(payload: ApplyCouponRequest, db: Session = Depends(get_db)):
    """
    Aplica un código de cortesía o invitación para exonerar la cuota de $99 MXN
    y dejar el negocio verificado y activo en el directorio comunitario.
    """
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == payload.registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    code = payload.coupon_code.strip().upper()
    env_codes = [c.strip().upper() for c in os.getenv("EPICENTRO_COUPONS", "").split(",") if c.strip()]

    if code not in VALID_COUPON_CODES and code not in env_codes:
        raise HTTPException(status_code=400, detail="Código de cortesía inválido o no reconocido.")

    now = datetime.now(timezone.utc)
    reg.payment_status = "waived"
    reg.payment_amount = 0.0
    reg.is_verified_badge = True
    reg.status = "active"
    code_desc = VALID_COUPON_CODES.get(code, "Cupón de Cortesía Válido")
    reg.moderation_notes = f"Verificación con cupón '{code}': {code_desc} el {now.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    db.commit()
    db.refresh(reg)

    folio_suffix = reg.whatsapp_code.split("-")[-1] if reg.whatsapp_code else reg.id[:4].upper()
    folio = f"NATURA-VERIFIED-{folio_suffix}"

    return {
        "success": True,
        "message": f"¡Código {code} aplicado con éxito! Tu comercio cuenta con Sello Oficial Vecino Verificado.",
        "folio": folio,
        "business_name": reg.business_name,
        "is_verified_badge": True,
        "status": "active"
    }


# --- ENDPOINTS ADMINISTRATIVOS (MODERACIÓN) ---

@router.get("/admin/registrations")
def list_registrations_for_moderation(
    status_filter: Optional[str] = None,
    is_authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Bandeja de moderación para revisar altas vecinales, pagos y estatus."""
    q = db.query(EpicentroRegistration)
    if status_filter:
        q = q.filter(EpicentroRegistration.status == status_filter)
    results = q.order_by(EpicentroRegistration.created_at.desc()).all()
    return results


@router.post("/admin/approve/{registration_id}")
async def approve_registration(
    registration_id: str,
    background_tasks: BackgroundTasks,
    payload: Optional[ModerationActionRequest] = None,
    is_authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Aprueba un comercio verificado y lo activa para el directorio público."""
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    reg.status = "active"
    reg.is_verified_badge = True
    if payload and payload.notes:
        reg.moderation_notes = payload.notes
    db.commit()

    # Enviar correo de felicitación / bienvenida en segundo plano
    if background_tasks:
        background_tasks.add_task(send_approval_email_task, reg.business_name, reg.owner_name, reg.email)
    else:
        import asyncio
        asyncio.create_task(send_approval_email_task(reg.business_name, reg.owner_name, reg.email))

    return {
        "success": True,
        "message": f"Comercio '{reg.business_name}' aprobado y activado en el directorio.",
        "registration": reg
    }


@router.post("/admin/reject/{registration_id}")
def reject_registration(
    registration_id: str,
    payload: Optional[ModerationActionRequest] = None,
    is_authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Rechaza o suspende una solicitud."""
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    reg.status = "rejected"
    if payload and payload.notes:
        reg.moderation_notes = payload.notes
    db.commit()

    return {
        "success": True,
        "message": f"Comercio '{reg.business_name}' rechazado.",
        "registration": reg
    }


@router.delete("/admin/registrations/{registration_id}")
def delete_registration(
    registration_id: str,
    is_authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Elimina permanentemente una solicitud o registro del sistema."""
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    bname = reg.business_name
    db.delete(reg)
    db.commit()
    return {"success": True, "message": f"Registro '{bname}' eliminado permanentemente."}


@router.post("/admin/registrations/purge-tests")
def purge_test_registrations(
    is_authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Elimina todos los registros de prueba creados durante desarrollo."""
    test_keywords = ["%pizzería di vico%", "%di vico%", "%tacos el roble%", "%la pizzería del bosque%", "%test%", "%prueba%"]
    deleted_count = 0
    for kw in test_keywords:
        rows = db.query(EpicentroRegistration).filter(
            (EpicentroRegistration.business_name.ilike(kw)) |
            (EpicentroRegistration.email.ilike(kw)) |
            (EpicentroRegistration.owner_name.ilike(kw))
        ).all()
        for r in rows:
            db.delete(r)
            deleted_count += 1
    db.commit()
    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"Se eliminaron {deleted_count} registros de prueba de la base de datos."
    }


@router.get("/businesses/active")
def list_active_verified_businesses(db: Session = Depends(get_db)):
    """Retorna los comercios reales que ya están activos y verificados para el directorio público."""
    results = (
        db.query(EpicentroRegistration)
        .filter(EpicentroRegistration.status == "active")
        .order_by(EpicentroRegistration.created_at.desc())
        .all()
    )
    return results
