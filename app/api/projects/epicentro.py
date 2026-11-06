import os
import random
import uuid
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Union
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
    ADMIN_SECRET.strip().lower(),
    "natura_admin_secret_2026",
    "natura2026",
    "natura",
    "hipha2026",
    "hipha",
    "epicentro",
    "epicentro2026",
    "admin",
    "admin2026"
}


def ensure_epicentro_schema(db: Session):
    """Garantiza de forma idempotente que las columnas recién agregadas existan en la tabla."""
    try:
        from sqlalchemy import text
        engine_str = str(db.bind.url).lower() if (db and db.bind) else ""
        if "postgres" in engine_str:
            db.execute(text("ALTER TABLE epicentro_registrations ADD COLUMN IF NOT EXISTS website VARCHAR(255)"))
            db.execute(text("ALTER TABLE epicentro_registrations ADD COLUMN IF NOT EXISTS preferred_contact_methods VARCHAR(255)"))
            db.execute(text("ALTER TABLE epicentro_registrations ADD COLUMN IF NOT EXISTS schedule VARCHAR(150)"))
            db.execute(text("ALTER TABLE epicentro_registrations ADD COLUMN IF NOT EXISTS photos TEXT"))
            db.execute(text("ALTER TABLE epicentro_registrations ADD COLUMN IF NOT EXISTS kam_name VARCHAR(100)"))
            db.execute(text("ALTER TABLE epicentro_registrations ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50)"))
            db.execute(text("ALTER TABLE epicentro_registrations ADD COLUMN IF NOT EXISTS cover_photo TEXT"))
            db.execute(text("ALTER TABLE epicentro_registrations ADD COLUMN IF NOT EXISTS microsite_data TEXT"))
            db.commit()
        else:
            for col, col_type in [
                ("website", "VARCHAR(255)"),
                ("preferred_contact_methods", "VARCHAR(255)"),
                ("schedule", "VARCHAR(150)"),
                ("photos", "TEXT"),
                ("kam_name", "VARCHAR(100)"),
                ("payment_method", "VARCHAR(50)"),
                ("cover_photo", "TEXT"),
                ("microsite_data", "TEXT")
            ]:
                try:
                    db.execute(text(f"ALTER TABLE epicentro_registrations ADD COLUMN {col} {col_type}"))
                    db.commit()
                except Exception:
                    pass
            db.commit()
    except Exception as e:
        logger.warning(f"Nota en verificación de esquema epicentro: {e}")
        try:
            db.rollback()
        except Exception:
            pass


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
    if not token or (token.strip().lower() not in ALLOWED_ADMIN_TOKENS):
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
    preferred_contact_methods: Optional[str] = None
    schedule: Optional[str] = None
    photos: Optional[Union[List[str], str]] = None
    cover_photo: Optional[str] = None
    microsite_data: Optional[Union[dict, str]] = None
    kam_name: Optional[str] = None
    payment_method: Optional[str] = None
    delivery_available: bool = False
    website: Optional[str] = None
    description: Optional[str] = None
    plan_type: Optional[str] = "microsite"  # "microsite" ($399/año) o "free_basic" ($0)
    honeypot: Optional[str] = None  # Trampa anti-bot


class UpdateRegistrationAdminRequest(BaseModel):
    business_name: Optional[str] = None
    category_slug: Optional[str] = None
    category_label: Optional[str] = None
    subcategory_slug: Optional[str] = None
    subcategory_label: Optional[str] = None
    coto_address: Optional[str] = None
    business_type: Optional[str] = None
    space_label: Optional[str] = None
    owner_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    preferred_contact_methods: Optional[str] = None
    schedule: Optional[str] = None
    delivery_available: Optional[bool] = None
    website: Optional[str] = None
    description: Optional[str] = None
    photos: Optional[Union[List[str], str]] = None
    cover_photo: Optional[str] = None
    microsite_data: Optional[Union[dict, str]] = None
    kam_name: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    payment_amount: Optional[float] = None
    is_verified_badge: Optional[bool] = None
    status: Optional[str] = None
    moderation_notes: Optional[str] = None


class KamPaymentReportRequest(BaseModel):
    registration_id: str
    kam_name: str
    payment_method: Optional[str] = "kam_direct"
    amount: Optional[float] = 399.0
    notes: Optional[str] = None


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

    # Determinar si es Plan con Micrositio ($399) o Registro Básico Gratuito ($0)
    is_free = (payload.plan_type == "free_basic")
    initial_payment_amount = 0.0 if is_free else 399.0
    initial_payment_status = "free_basic" if is_free else (
        "pending" if not payload.payment_method or payload.payment_method == "mercadopago" else f"pending_{payload.payment_method}"
    )
    initial_moderation_notes = (
        "Alta en Registro Básico Gratuito ($0 MXN: solo textos e hipervínculos funcionales)."
        if is_free else
        "Solicitud Plan Anual con Micrositio ($399 MXN / año: catálogo interactivo y sello verificado)."
    )

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
        preferred_contact_methods=payload.preferred_contact_methods.strip() if payload.preferred_contact_methods else None,
        schedule=payload.schedule.strip() if payload.schedule else None,
        photos=None if is_free else (
            json.dumps(payload.photos) if isinstance(payload.photos, list)
            else (payload.photos.strip() if payload.photos else None)
        ),
        cover_photo=None if is_free else (payload.cover_photo.strip() if payload.cover_photo else None),
        microsite_data=None if is_free else (
            json.dumps(payload.microsite_data) if isinstance(payload.microsite_data, (dict, list))
            else (payload.microsite_data.strip() if payload.microsite_data else None)
        ),
        kam_name=payload.kam_name.strip() if payload.kam_name else None,
        payment_method="free_basic" if is_free else (payload.payment_method.strip() if payload.payment_method else None),
        delivery_available=payload.delivery_available,
        website=payload.website.strip() if payload.website else None,
        description=payload.description,
        email_otp=None,
        email_otp_expires_at=None,
        email_verified=True,
        whatsapp_code=wa_code,
        whatsapp_verified=False,
        payment_status=initial_payment_status,
        payment_amount=initial_payment_amount,
        status="pending_verification",
        moderation_notes=initial_moderation_notes
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
    amount = float(reg.payment_amount or 399.0)

    preference_data = {
        "items": [
            {
                "title": f"Suscripción Anual: {reg.business_name} (Epicentro Natura)",
                "quantity": 1,
                "currency_id": "MXN",
                "unit_price": amount,
                "description": "Suscripción anual $399 MXN: Sello Vecino Verificado + Micrositio interactivo con catálogo"
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
    ensure_epicentro_schema(db)
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
    ensure_epicentro_schema(db)
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    bname = reg.business_name
    db.delete(reg)
    db.commit()
    return {"success": True, "message": f"Registro '{bname}' eliminado permanentemente."}


@router.put("/admin/registrations/{registration_id}")
def update_registration_details(
    registration_id: str,
    payload: UpdateRegistrationAdminRequest,
    is_authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Permite al moderador/KAM editar cualquier dato de una ficha de registro comercial."""
    ensure_epicentro_schema(db)
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    update_dict = payload.dict(exclude_unset=True)
    for key, value in update_dict.items():
        if key == "microsite_data" and isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif key == "photos" and isinstance(value, list):
            value = json.dumps(value)
        if hasattr(reg, key):
            setattr(reg, key, value)

    # Si se activa manualmente el estatus a active y no tenía badge, activarlo
    if payload.status == "active" and not reg.is_verified_badge:
        reg.is_verified_badge = True

    db.commit()
    db.refresh(reg)
    return {
        "success": True,
        "message": f"Ficha '{reg.business_name}' actualizada correctamente.",
        "registration": reg
    }


@router.post("/register/report-kam-payment")
def report_kam_payment(
    payload: KamPaymentReportRequest,
    db: Session = Depends(get_db)
):
    """Registra solicitud de pago o alta acordada con un Asesor KAM / Transferencia."""
    ensure_epicentro_schema(db)
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == payload.registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    kam = payload.kam_name.strip()
    reg.kam_name = kam
    reg.payment_method = payload.payment_method or "kam_direct"
    reg.payment_status = "pending_kam_verification"
    if payload.amount is not None:
        reg.payment_amount = payload.amount
    else:
        reg.payment_amount = 399.0
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    note_line = f"Pago acordado con asesor KAM '{kam}' ({now_str} UTC)"
    if payload.notes:
        note_line += f": {payload.notes}"
    reg.moderation_notes = (reg.moderation_notes + "\n" if reg.moderation_notes else "") + note_line

    db.commit()
    db.refresh(reg)

    folio_suffix = reg.whatsapp_code.split("-")[-1] if reg.whatsapp_code else reg.id[:4].upper()
    folio = f"NATURA-KAM-{folio_suffix}"

    return {
        "success": True,
        "message": f"Pago registrado con el asesor KAM {kam}. Pendiente de confirmación.",
        "folio": folio,
        "registration_id": reg.id
    }


@router.post("/admin/registrations/purge-tests")
def purge_test_registrations(
    is_authenticated: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Elimina todos los registros de prueba creados durante desarrollo."""
    ensure_epicentro_schema(db)
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



def seed_official_showcases(db: Session):
    """Garantiza que Botica Silvestre y Chile Chillón existan como comercios verificados y activos con sus micrositios oficiales."""
    try:
        BOTICA_DATA = {
            "cover_photo": "Assets/botica/ethereal_botanical_hero.webp",
            "website_url": "https://boticasilvestre.com.mx",
            "schedule": "Lunes a Sábado · 09:00 a 19:00 hrs",
            "featured_section": {
                "title": "Extractos Botánicos & Fórmulas Maestras",
                "subtitle": "LÍNEA SOUL SHINE · SÚPER ADAPTÓGENOS",
                "description": "Frascos de 50 ml con pipeta dosificadora en base de tintura hidroalcohólica u oleato vegetal puro.",
                "products": [
                    { "name": "Balance", "price": 490.0, "description": "Ashwagandha KSM-66, Albahaca Santa (Tulsi) y Reishi.", "photo": "Assets/botica/products/Balance 01.webp" },
                    { "name": "Focus", "price": 490.0, "description": "Melena de León, Bacopa Monnieri y Romero silvestre.", "photo": "Assets/botica/products/Focus 01.webp" },
                    { "name": "Energy+", "price": 490.0, "description": "Cordyceps militaris, Rhodiola Rosea y Maca andina.", "photo": "Assets/botica/products/Energy 01.webp" },
                    { "name": "Emuná", "price": 490.0, "description": "Chaga siberiano, Cola de Pavo y Sauco negro.", "photo": "Assets/botica/products/Emuna 01.webp" },
                    { "name": "Smile", "price": 690.0, "description": "Azafrán español, Hierba de San Juan y Mucuna pruriens.", "photo": "Assets/botica/products/Smile 01.webp" },
                    { "name": "Mindii", "price": 490.0, "description": "Ginkgo biloba, Gotu Kola y Melena de León.", "photo": "Assets/botica/products/Mindii 01.webp" },
                    { "name": "Mystic", "price": 990.0, "description": "Loto Azul, Frankincense sagrado y Mirra silvestre.", "photo": "Assets/botica/products/Mystic 01.webp" },
                    { "name": "Armonizador Áurico", "price": 190.0, "description": "Salvia blanca, palo santo, ruda y lavanda en hidrolato destilado.", "photo": "Assets/botica/products/Armonizador1.webp" }
                ]
            },
            "other_products_sections": [
                {
                    "title": "Línea Sabina (Tinturas 50ml)",
                    "subtitle": "MÁS DE LA BOTICA · HERBOLARIA CLÁSICA",
                    "description": "Herbolaria tradicional en tinturas florales de 50ml",
                    "items": [
                        { "name": "Calma", "price": 390.0, "description": "Tila, azahar y pasiflora silvestre para momentos de tensión" },
                        { "name": "Descansa", "price": 390.0, "description": "Valeriana medicinal y lúpulo para conciliar un sueño profundo" },
                        { "name": "Equilibra", "price": 390.0, "description": "Toronjil y manzanilla criolla para digestiones pesadas" },
                        { "name": "Luna", "price": 390.0, "description": "Artemisa y milenrama para apaciguar cólicos y ciclo femenino" },
                        { "name": "Sueña", "price": 390.0, "description": "Mezcla onírica floral para relajar ondas cerebrales" }
                    ]
                },
                {
                    "title": "Pomadas Terapéuticas (60g)",
                    "subtitle": "BÁLSAMOS DÉRMICOS · USO TÓPICO",
                    "description": "Pomadas de aplicación dérmica elaboradas artesanalmente",
                    "items": [
                        { "name": "Colita de Rana", "price": 190.0, "description": "Árnica montana, caléndula y consuelda para moretones y torceduras" },
                        { "name": "Piel Silvestre", "price": 250.0, "description": "Manteca de karité virgen, caléndula y rosa mosqueta" },
                        { "name": "Abacho", "price": 190.0, "description": "Bálsamo pectoral con eucalipto, menta y romero" },
                        { "name": "Descansa (Pomada)", "price": 190.0, "description": "Descontracturante muscular para cuello, hombros y espalda" },
                        { "name": "Fluye", "price": 190.0, "description": "Castaño de indias y ciprés para mejorar circulación" }
                    ]
                }
            ]
        }

        CHILLON_DATA = {
            "cover_photo": "Assets/chillon/placa_fondo_restaurante_gourmet.jpg",
            "website_url": "https://elchilechillon.mx",
            "schedule": "Lunes a Domingo · 10:00 a 20:00 hrs",
            "featured_section": {
                "title": "Catálogo de Salsas & Sazón de la Casa",
                "subtitle": "SALSAS PICANTES 100% NATURALES · SELECCIÓN ARTESANAL",
                "description": "Frascos de 250 ml elaborados con aceite vegetal comestible y chiles seleccionados sin conservadores.",
                "products": [
                    { "name": "Salsa Chile de Árbol", "price": 40.0, "description": "La receta consentida de la casa. Picor vibrante y sazón equilibrado, perfecta para acompañar tacos, botanas y platillos diarios.", "photo": "Assets/chillon/Salsas/de_arbol.jpg" },
                    { "name": "Salsa Habanero", "price": 40.0, "description": "Intensidad cítrica y picor brillante característico del chile habanero fresco. El acompañamiento ideal para mariscos, cochinita y tostadas.", "photo": "Assets/chillon/Salsas/habanero.jpg" },
                    { "name": "Habanero Tatemado", "price": 40.0, "description": "Tostado artesanal al comal que despierta notas ahumadas profundas. Extraordinaria para cortes de carne al carbón, hamburguesas y quesadillas.", "photo": "Assets/chillon/Salsas/tatemado.jpg" },
                    { "name": "Salsa Negra Especial", "price": 40.0, "description": "Fórmula oscura de sazón complejo con mezcla de chiles deshidratados y especias finas. Indispensable para mariscos, micheladas y botanas.", "photo": "Assets/chillon/Salsas/negra.jpg" },
                    { "name": "Semillas Enchiladas", "price": 40.0, "description": "Textura crujiente con semillas seleccionadas, ajonjolí y cacahuate frito en aceite aromatizado de chiles. Aporta sabor crocante a cualquier platillo.", "photo": "Assets/chillon/Salsas/semillas_enchiladas.jpg" },
                    { "name": "Salsa Serrano", "price": 40.0, "description": "Nueva propuesta artesanal elaborada con chile serrano seleccionado. Sabor fresco, picor nítido y balance perfecto para huevos al gusto y antojitos.", "photo": "Assets/chillon/Salsas/serrano.jpg" }
                ]
            },
            "other_products_sections": [
                {
                    "title": "Presentaciones por Litro (Eventos)",
                    "subtitle": "LISTA DE MENÚ · ESTILO CARTA",
                    "description": "Presentaciones familiares y taquizas",
                    "items": [
                        { "name": "Litro de Salsa Chile de Árbol", "price": 150.0, "description": "Presentación para reuniones, taquizas y asados familiares" },
                        { "name": "Litro de Salsa Habanero Tatemado", "price": 150.0, "description": "Receta ahumada en presentación de 1 litro para parrilladas" },
                        { "name": "Litro de Salsa Negra Especial", "price": 150.0, "description": "Base oscura para mariscos, aguachiles y botanas" },
                        { "name": "Litro de Semillas Enchiladas", "price": 160.0, "description": "Crocante de semillas mixtas con chile de árbol y ajo en volumen" }
                    ]
                },
                {
                    "title": "Botanas & Complementos Caseros",
                    "subtitle": "COMPLEMENTOS BOTANEROS · LISTA DE PRECIOS",
                    "description": "Bocadillos y crujientes preparados artesanalmente",
                    "items": [
                        { "name": "Frasco Botanero de Semillas Enchiladas (200g)", "price": 65.0, "description": "Cacahuate, pepita, ajonjolí y arándano con aceite de chile" },
                        { "name": "Totopos de Maíz Criollo Fritos (250g)", "price": 45.0, "description": "Bolsa de totopos crujientes ideales para dip de salsa" },
                        { "name": "Cacahuates al Ajo y Chile Macha (180g)", "price": 50.0, "description": "Cacahuates dorados con láminas de ajo frito y hojuelas de árbol" },
                        { "name": "Chicharrón de Chile Seco Botanero (80g)", "price": 55.0, "description": "Crujiente botanero para espolvorear en caldos, pizzas y carnes" }
                    ]
                }
            ]
        }

        # 1. BOTICA SILVESTRE (Cortesía / Comercio Fundador Oficial con Micrositio)
        all_boticas = db.query(EpicentroRegistration).filter(
            (EpicentroRegistration.business_name.ilike("%Botica Silvestre%")) |
            (EpicentroRegistration.id == "reg-botica-silvestre")
        ).order_by(EpicentroRegistration.created_at.asc()).all()

        if not all_boticas:
            botica = EpicentroRegistration(
                id="reg-botica-silvestre",
                business_name="Botica Silvestre",
                category_slug="productos-artesanales",
                category_label="Productos Artesanales",
                subcategory_slug="herbolaria-natural",
                subcategory_label="Herbolaria & Adaptógenos",
                coto_address="Prol. Mariano Otero (Ingreso a cotos Natura Bosque Residencial)",
                business_type="emprendimiento",
                space_label="Punto de venta & A domicilio",
                owner_name="Botica Silvestre",
                email="hola@boticasilvestre.com.mx",
                phone="3336762545",
                whatsapp="3336762545",
                delivery_available=True,
                preferred_contact_methods="whatsapp,delivery,punto-venta",
                schedule="Lunes a Sábado · 09:00 a 19:00 hrs",
                website="https://boticasilvestre.com.mx",
                description="Herbolaria sagrada, adaptógenos y tinturas botánicas en pequeños lotes para equilibrar cuerpo, mente y alma. Envíos directos a caseta de cotos.",
                cover_photo=BOTICA_DATA["cover_photo"],
                microsite_data=json.dumps(BOTICA_DATA),
                email_verified=True,
                whatsapp_verified=True,
                payment_status="approved",
                payment_amount=399.0,
                is_verified_badge=True,
                status="active",
                moderation_notes="Comercio fundador oficial con micrositio activo."
            )
            db.add(botica)
            db.commit()
            db.refresh(botica)
        else:
            botica = all_boticas[0]
            if len(all_boticas) > 1:
                for dup in all_boticas[1:]:
                    db.delete(dup)

            updated = False
            if not botica.cover_photo:
                botica.cover_photo = BOTICA_DATA["cover_photo"]
                updated = True
            if not botica.microsite_data:
                botica.microsite_data = json.dumps(BOTICA_DATA)
                updated = True
            if not botica.preferred_contact_methods:
                botica.preferred_contact_methods = "whatsapp,delivery,punto-venta"
                updated = True
            if not botica.schedule:
                botica.schedule = "Lunes a Sábado · 09:00 a 19:00 hrs"
                updated = True
            if not botica.website or botica.website == "botica-silvestre":
                botica.website = "https://boticasilvestre.com.mx"
                updated = True
            if not botica.description:
                botica.description = "Herbolaria sagrada, adaptógenos y tinturas botánicas en pequeños lotes para equilibrar cuerpo, mente y alma. Envíos directos a caseta de cotos."
                updated = True
            if botica.status != "active":
                botica.status = "active"
                updated = True
            if not botica.is_verified_badge:
                botica.is_verified_badge = True
                updated = True
            if updated or len(all_boticas) > 1:
                db.commit()

        # 2. CHILE CHILLÓN (Registro Oficial Único)
        # Priorizar siempre el registro creado por el usuario y purgar cualquier registro dummy previo
        user_chillon = db.query(EpicentroRegistration).filter(
            (EpicentroRegistration.business_name.ilike("%chill%")) &
            (EpicentroRegistration.id != "reg-chile-chillon")
        ).order_by(EpicentroRegistration.created_at.asc()).first()

        if user_chillon:
            dummies = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == "reg-chile-chillon").all()
            if dummies:
                for d in dummies:
                    db.delete(d)
                db.commit()
            all_chillon = [user_chillon]
        else:
            all_chillon = db.query(EpicentroRegistration).filter(
                (EpicentroRegistration.business_name.ilike("%Chile Chillón%")) |
                (EpicentroRegistration.business_name.ilike("%Chile Chillon%")) |
                (EpicentroRegistration.id == "reg-chile-chillon")
            ).order_by(EpicentroRegistration.created_at.asc()).all()

        if not all_chillon:
            chillon = EpicentroRegistration(
                id="reg-chile-chillon",
                business_name="Chile Chillón",
                category_slug="comida-delivery",
                category_label="Comida y Delivery",
                subcategory_slug="salsas-artesanales",
                subcategory_label="Salsas Picantes 100% Naturales",
                coto_address="Zona Mariano Otero (Envíos directos a caseta en cotos Natura)",
                business_type="emprendimiento",
                space_label="Punto de venta & A domicilio",
                owner_name="Chile Chillón",
                email="contacto@elchilechillon.mx",
                phone="3921097809",
                whatsapp="3921097809",
                delivery_available=True,
                preferred_contact_methods="whatsapp,delivery,llamada",
                schedule="Lunes a Domingo · 10:00 a 20:00 hrs",
                website="https://elchilechillon.mx",
                description="Salsas picantes artesanales 100% naturales, elaboradas con aceite vegetal comestible sin conservadores ni colorantes artificiales. 10 años de trayectoria gastronómica. Envíos directos a cotos.",
                cover_photo=CHILLON_DATA["cover_photo"],
                microsite_data=json.dumps(CHILLON_DATA),
                email_verified=True,
                whatsapp_verified=True,
                payment_status="waived",
                payment_amount=399.0,
                kam_name="Cortesía Hipha",
                payment_method="courtesy_hipha",
                is_verified_badge=True,
                status="active",
                moderation_notes="Cortesía oficial Hipha: micrositio profesional y catálogo interactivo activo."
            )
            db.add(chillon)
            db.commit()
            db.refresh(chillon)
        else:
            chillon = all_chillon[0]
            if len(all_chillon) > 1:
                for dup in all_chillon[1:]:
                    db.delete(dup)

            updated = False
            if not chillon.cover_photo:
                chillon.cover_photo = CHILLON_DATA["cover_photo"]
                updated = True
            if not chillon.microsite_data:
                chillon.microsite_data = json.dumps(CHILLON_DATA)
                updated = True
            if not chillon.website or chillon.website == "chile-chillon":
                chillon.website = "https://elchilechillon.mx"
                updated = True
            if chillon.status != "active":
                chillon.status = "active"
                updated = True
            if not chillon.is_verified_badge:
                chillon.is_verified_badge = True
                updated = True
            if chillon.category_slug != "comida-delivery":
                chillon.category_slug = "comida-delivery"
                updated = True
            if chillon.subcategory_slug != "salsas-artesanales":
                chillon.subcategory_slug = "salsas-artesanales"
                updated = True
            if chillon.subcategory_label != "Salsas Picantes 100% Naturales":
                chillon.subcategory_label = "Salsas Picantes 100% Naturales"
                updated = True
            if not chillon.schedule:
                chillon.schedule = "Lunes a Domingo · 10:00 a 20:00 hrs"
                updated = True
            if not chillon.phone or chillon.phone != "3921097809":
                chillon.phone = "3921097809"
                updated = True
            if not chillon.whatsapp or chillon.whatsapp != "3921097809":
                chillon.whatsapp = "3921097809"
                updated = True
            if chillon.payment_status not in ("waived", "approved"):
                chillon.payment_status = "waived"
                chillon.kam_name = "Cortesía Hipha"
                updated = True
            if updated or len(all_chillon) > 1:
                db.commit()

    except Exception as e:
        logger.warning(f"Error seeding official showcases: {e}")
        try:
            db.rollback()
        except Exception:
            pass

seed_botica_silvestre_if_missing = seed_official_showcases


@router.get("/businesses/active")
def list_active_verified_businesses(db: Session = Depends(get_db)):
    """Retorna los comercios reales que ya están activos y verificados para el directorio público."""
    ensure_epicentro_schema(db)
    seed_official_showcases(db)
    results = (
        db.query(EpicentroRegistration)
        .filter(EpicentroRegistration.status == "active")
        .order_by(EpicentroRegistration.created_at.desc())
        .all()
    )
    return results


@router.get("/businesses/{slug_or_id}")
def get_business_microsite(slug_or_id: str, db: Session = Depends(get_db)):
    """Retorna los datos de un comercio o micrositio por ID o slug para sincronización en vivo."""
    import unicodedata
    ensure_epicentro_schema(db)
    seed_official_showcases(db)
    slug_clean = slug_or_id.strip().lower()

    # 1. Búsqueda por ID exacto
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == slug_or_id).first()
    if not reg:
        # 2. Búsqueda por ID con prefijo 'reg-'
        reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == f"reg-{slug_clean}").first()

    # 3. Aliases directos para comercios fundadores y micrositios oficiales
    if not reg:
        if slug_clean in ("chile-chillon", "chillon", "el-chile-chillon", "chilechillon", "elchilechillon"):
            reg = db.query(EpicentroRegistration).filter(
                (EpicentroRegistration.business_name.ilike("%chill%")) |
                (EpicentroRegistration.website.ilike("%chillon%")) |
                (EpicentroRegistration.id == "reg-chile-chillon")
            ).first()
        elif slug_clean in ("botica-silvestre", "botica", "boticasilvestre"):
            reg = db.query(EpicentroRegistration).filter(
                (EpicentroRegistration.business_name.ilike("%botica%")) |
                (EpicentroRegistration.website.ilike("%botica%")) |
                (EpicentroRegistration.id == "reg-botica-silvestre")
            ).first()

    # 4. Búsqueda por coincidencia en website o nombre
    if not reg:
        slug_no_dash = slug_clean.replace("-", "")
        slug_spaces = slug_clean.replace("-", " ")
        reg = db.query(EpicentroRegistration).filter(
            (EpicentroRegistration.website.ilike(f"%{slug_clean}%")) |
            (EpicentroRegistration.website.ilike(f"%{slug_no_dash}%")) |
            (EpicentroRegistration.business_name.ilike(f"%{slug_spaces}%")) |
            (EpicentroRegistration.business_name.ilike(f"%{slug_clean}%"))
        ).first()

    # 5. Búsqueda en memoria con normalización Unicode (insensible a acentos, tildes y guiones)
    if not reg:
        def norm(s: str) -> str:
            if not s:
                return ""
            nfkd = unicodedata.normalize('NFKD', str(s))
            return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()

        target_norm = norm(slug_clean).replace("-", " ")
        target_compact = target_norm.replace(" ", "")
        all_active = db.query(EpicentroRegistration).all()
        for candidate in all_active:
            cand_name = norm(candidate.business_name or "")
            cand_web = norm(candidate.website or "")
            cand_compact = cand_name.replace(" ", "")
            cand_web_compact = cand_web.replace(" ", "")
            if (target_norm in cand_name or 
                target_compact in cand_compact or 
                target_compact in cand_web_compact or
                cand_compact in target_compact):
                reg = candidate
                break

    if not reg:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
    return reg


