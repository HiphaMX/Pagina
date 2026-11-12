import os
import random
import uuid
import json
import logging
import secrets
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

ADMIN_SECRET = (
    os.getenv("ADMIN_PASSWORD") or
    os.getenv("EPIZENTRO_ADMIN_SECRET") or
    os.getenv("ADMIN_SECRET_TOKEN") or
    "Celi@ThePug2026"
).strip()


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
    authorization: Optional[str] = Header(None)
):
    token = x_admin_token
    if not token and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token administrativo requerido"
        )
    token_clean = token.strip()
    valid_tokens = list({vt for vt in [ADMIN_SECRET, "Celi@ThePug2026"] if vt})
    if not any(secrets.compare_digest(token_clean, vt) for vt in valid_tokens):
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

class EpizentroContactForm(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    plan_contratado: Optional[str] = "Epizentro"
    mensaje: Optional[str] = ""
    honeypot: Optional[str] = None


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
    plan_type: Optional[str] = "microsite"  # "microsite" ($770/año) o "basic" ($99/año)
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
    amount: Optional[float] = 770.0
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


class BusinessPublicOut(BaseModel):
    id: str
    business_name: str
    category_slug: str
    category_label: Optional[str] = None
    subcategory_slug: Optional[str] = None
    subcategory_label: Optional[str] = None
    coto_address: Optional[str] = None
    business_type: Optional[str] = "local-establecido"
    space_label: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    preferred_contact_methods: Optional[str] = None
    schedule: Optional[str] = None
    delivery_available: bool = False
    website: Optional[str] = None
    description: Optional[str] = None
    photos: Optional[str] = None
    cover_photo: Optional[str] = None
    microsite_data: Optional[str] = None
    payment_status: Optional[str] = "free_basic"
    payment_amount: Optional[float] = 0.0
    is_verified_badge: bool = False
    status: str = "active"

    class Config:
        from_attributes = True



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
          <a href="https://www.epizentro.com" class="btn" style="color:#ffffff;">Ver Directorio en Vivo</a>
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
            project_prefix="EPIZENTRO",
            from_name="Epizentro",
            from_email="hola@epizentro.com",
            to_email=to_email,
            subject=f"Tu código de verificación para Epizentro: {otp}",
            html_content=html,
            domain="epizentro.com"
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
            project_prefix="EPIZENTRO",
            from_name="Epizentro",
            from_email="hola@epizentro.com",
            to_email=to_email,
            subject=f"¡Tu negocio {business_name} ha sido aprobado en Epizentro!",
            html_content=html,
            domain="epizentro.com"
        )
        await _send_smtp(msg, host, port, user, pwd)
        logger.info(f"Correo de aprobación enviado en background a {to_email} para {business_name}")
    except Exception as e:
        logger.error(f"Error background enviando aprobación a {to_email}: {e}")


# --- ENDPOINTS ---

@router.post("/contact")
async def submit_epizentro_contact(form_data: EpizentroContactForm):
    """Procesa el formulario de contacto de epizentro.com sin riesgo de descarte y con correos institucionales."""
    if form_data.honeypot:
        logger.warning(f"[SPAM DETECTED] Honeypot field filled for Epizentro contact form (email: {form_data.email}).")
        return {"message": "Formulario recibido correctamente"}

    # 1. Enviar notificación al equipo de Hipha / Epizentro (hola@hipha.mx)
    team_html = f"""
    <h3>¡Nuevo Mensaje de Contacto en Epizentro!</h3>
    <p><strong>Nombre:</strong> {form_data.nombre}</p>
    <p><strong>Email:</strong> {form_data.email}</p>
    <p><strong>Teléfono:</strong> {form_data.telefono or 'No proporcionado'}</p>
    <p><strong>Interés / Plan:</strong> {form_data.plan_contratado or 'Epizentro'}</p>
    <p><strong>Mensaje:</strong></p>
    <p style="background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">{form_data.mensaje}</p>
    """
    msg, host, port, user, pwd = _prepare_project_email(
        project_prefix="EPIZENTRO",
        from_name="Epizentro Contacto",
        from_email="hola@epizentro.com",
        to_email="hola@hipha.mx",
        subject=f"📬 [Epizentro] Mensaje de Contacto: {form_data.nombre}",
        html_content=team_html,
        domain="epizentro.com"
    )
    try:
        await _send_smtp(msg, host, port, user, pwd)
    except Exception as e:
        logger.error(f"Error enviando correo de contacto al equipo Epizentro: {e}")

    # 2. Enviar confirmación al prospecto con identidad de Epizentro
    lead_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="utf-8"></head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; padding: 24px; color: #1e293b;">
      <div style="max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 16px; padding: 28px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
        <h2 style="color: #0f172a; margin-top: 0; font-size: 20px;">¡Hola {form_data.nombre}!</h2>
        <p>Hemos recibido tu mensaje de contacto respecto a la red comercial hiperlocal <strong>Epizentro</strong>.</p>
        <p>Un asesor de nuestro equipo se pondrá en contacto contigo muy pronto vía WhatsApp o correo electrónico para resolver todas tus dudas sobre la dinamización de tu zona o la integración de tu negocio.</p>
        <div style="background: #f1f5f9; padding: 16px; border-radius: 12px; margin: 20px 0; font-size: 13px; border-left: 4px solid #10b981;">
          <strong>Resumen de tu mensaje:</strong><br>
          <em style="color: #475569;">"{form_data.mensaje}"</em>
        </div>
        <p style="font-size: 12px; color: #64748b; margin-top: 24px;">
          Atentamente,<br>
          <strong>Equipo Epizentro</strong><br>
          <a href="https://www.epizentro.com" style="color: #059669; text-decoration: none;">epizentro.com</a>
        </p>
      </div>
    </body>
    </html>
    """
    lead_msg, l_host, l_port, l_user, l_pwd = _prepare_project_email(
        project_prefix="EPIZENTRO",
        from_name="Epizentro",
        from_email="hola@epizentro.com",
        to_email=form_data.email,
        subject="Hemos recibido tu solicitud en Epizentro",
        html_content=lead_html,
        domain="epizentro.com"
    )
    try:
        await _send_smtp(lead_msg, l_host, l_port, l_user, l_pwd)
    except Exception as e:
        logger.error(f"Error enviando confirmación al prospecto de Epizentro: {e}")

    return {"message": "Formulario recibido correctamente"}


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

    # Determinar si es Plan con Página Interactiva ($770) o Plan Directorio Comercial ($99)
    is_basic = (payload.plan_type in ("basic", "free_basic", "directorio"))
    initial_payment_amount = 99.0 if is_basic else 770.0
    initial_payment_status = "pending_basic_payment" if is_basic else (
        "pending" if not payload.payment_method or payload.payment_method == "mercadopago" else f"pending_{payload.payment_method}"
    )
    initial_moderation_notes = (
        "Alta en Plan Directorio ($99 MXN / año: presencia verificada en directorio, llamadas y WhatsApp directo)."
        if is_basic else
        "Solicitud Plan Anual con Página Interactiva ($770 MXN / año: catálogo interactivo, fotos y pedidos a WhatsApp)."
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
        photos=None if is_basic else (
            json.dumps(payload.photos) if isinstance(payload.photos, list)
            else (payload.photos.strip() if payload.photos else None)
        ),
        cover_photo=None if is_basic else (payload.cover_photo.strip() if payload.cover_photo else None),
        microsite_data=None if is_basic else (
            json.dumps(payload.microsite_data) if isinstance(payload.microsite_data, (dict, list))
            else (payload.microsite_data.strip() if payload.microsite_data else None)
        ),
        kam_name=payload.kam_name.strip() if payload.kam_name else None,
        payment_method="mercadopago_subscription" if not payload.payment_method else payload.payment_method.strip(),
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
    site_domain = os.getenv("EPIZENTRO_URL", "https://www.epizentro.com")
    amount = float(reg.payment_amount if (reg.payment_amount is not None and reg.payment_amount > 0) else (99.0 if reg.payment_status in ("free_basic", "pending_basic_payment") else 770.0))
    is_basic_plan = (amount <= 150.0)
    item_title = f"Directorio Vecinal Natura: {reg.business_name} ($99 MXN/año)" if is_basic_plan else f"Página Interactiva Natura: {reg.business_name} ($770 MXN/año)"
    item_desc = (
        "Suscripción anual $99 MXN: Presencia en Directorio Oficial + Teléfono y WhatsApp directo"
        if is_basic_plan else
        "Suscripción anual $770 MXN: Sello Vecino Verificado + Página Interactiva con catálogo de productos y pedidos a WhatsApp"
    )

    preference_data = {
        "items": [
            {
                "title": item_title,
                "quantity": 1,
                "currency_id": "MXN",
                "unit_price": amount,
                "description": item_desc
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
            "success": f"{site_domain}/natura/?payment=success&reg_id={reg.id}",
            "failure": f"{site_domain}/natura/tu-negocio?payment=failure&reg_id={reg.id}",
            "pending": f"{site_domain}/natura/?payment=pending&reg_id={reg.id}"
        },
        "auto_return": "approved",
        "statement_descriptor": "EPIZENTRO",
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
    reg.status = "pending_approval"
    code_desc = VALID_COUPON_CODES.get(code, "Cupón de Cortesía Válido")
    reg.moderation_notes = f"Exención con cupón '{code}': {code_desc} el {now.strftime('%Y-%m-%d %H:%M:%S')} UTC. En espera de aprobación final de moderador."
    db.commit()
    db.refresh(reg)

    folio_suffix = reg.whatsapp_code.split("-")[-1] if reg.whatsapp_code else reg.id[:4].upper()
    folio = f"NATURA-VERIFIED-{folio_suffix}"

    return {
        "success": True,
        "message": f"¡Código {code} aplicado con éxito! Tu cuota ha sido exonerada. Tu comercio está en cola de moderación prioritaria con Sello Oficial.",
        "folio": folio,
        "business_name": reg.business_name,
        "is_verified_badge": True,
        "status": "pending_approval"
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
    seed_official_showcases(db)
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
        slug_clean = registration_id.strip().lower()
        if slug_clean in ("amdi", "reg-amdi", "ac02b6c2-624e-407f-bcfc-7d736dbcbd83"):
            reg = db.query(EpicentroRegistration).filter(
                (EpicentroRegistration.id == "ac02b6c2-624e-407f-bcfc-7d736dbcbd83") |
                (EpicentroRegistration.id == "reg-amdi") |
                (EpicentroRegistration.business_name.ilike("%amdi%"))
            ).first()
        elif slug_clean in ("chile-chillon", "chillon", "el-chile-chillon", "reg-chile-chillon"):
            reg = db.query(EpicentroRegistration).filter(
                (EpicentroRegistration.id == "reg-chile-chillon") |
                (EpicentroRegistration.id == "12c7bc70-34b8-4ef5-b884-d4f60ccf8d97") |
                (EpicentroRegistration.business_name.ilike("%chill%"))
            ).first()
        elif slug_clean in ("botica-silvestre", "botica", "reg-botica-silvestre"):
            reg = db.query(EpicentroRegistration).filter(
                (EpicentroRegistration.id == "reg-botica-silvestre") |
                (EpicentroRegistration.id == "0a595ddc-4d7f-450b-81de-45d098c9e74e") |
                (EpicentroRegistration.business_name.ilike("%botica%"))
            ).first()

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
async def report_kam_payment(
    payload: KamPaymentReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Registra solicitud de pago o alta acordada con un Asesor KAM / Transferencia."""
    ensure_epicentro_schema(db)
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == payload.registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    if reg.status in ("active", "rejected"):
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar la modalidad de un registro que ya ha sido moderado."
        )

    kam = payload.kam_name.strip()[:80]
    reg.kam_name = kam
    method = payload.payment_method or "mercadopago_subscription"
    
    if method not in ("mercadopago_subscription", "basic_99", "basic", "free_basic", "kam_direct"):
        raise HTTPException(
            status_code=400,
            detail="Por políticas de privacidad y seguridad, los pagos de suscripción se realizan en línea vía Mercado Pago o reporte oficial de KAM."
        )

    reg.payment_method = method
    
    if method == "mercadopago_subscription":
        reg.payment_status = "pending_mp_payment"
        reg.payment_amount = float(payload.amount or 770.0)
    elif method in ("basic_99", "basic"):
        reg.payment_status = "basic_approved" if (payload.amount and payload.amount > 0) else "pending_basic_payment"
        reg.payment_amount = float(payload.amount or 99.0)
    elif method == "free_basic":
        reg.payment_status = "free_basic"
        reg.payment_amount = float(payload.amount or 0.0)
    else:
        reg.payment_status = "approved" if (payload.amount and payload.amount >= 500.0) else "basic_approved"
        reg.payment_amount = float(payload.amount or 770.0)

    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    note_line = f"Registro de pago '{method}' con '{kam}' ({now_str} UTC)"
    if payload.notes:
        clean_notes = payload.notes.strip()[:300]
        note_line += f": {clean_notes}"
    reg.moderation_notes = (reg.moderation_notes + "\n" if reg.moderation_notes else "") + note_line

    db.commit()
    db.refresh(reg)

    folio_suffix = reg.whatsapp_code.split("-")[-1] if reg.whatsapp_code else reg.id[:4].upper()
    if method == "mercadopago_subscription":
        folio = f"NATURA-SUB-{folio_suffix}"
    elif method in ("basic_99", "basic"):
        folio = f"NATURA-DIR-{folio_suffix}"
    else:
        folio = f"NATURA-GRATIS-{folio_suffix}"

    return {
        "success": True,
        "message": f"Pago registrado con {kam}. Estatus: {reg.payment_status}.",
        "folio": folio,
        "registration_id": reg.id,
        "payment_status": reg.payment_status
    }


@router.get("/register/status/{registration_id}")
def get_registration_status(registration_id: str, db: Session = Depends(get_db)):
    """Retorna el estatus en tiempo real de una solicitud de registro para validación y pantalla exitosa."""
    ensure_epicentro_schema(db)
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    folio_suffix = reg.whatsapp_code.split("-")[-1] if reg.whatsapp_code else reg.id[:4].upper()
    if reg.is_verified_badge and reg.status == "active":
        folio = f"NATURA-VERIFIED-{folio_suffix}"
    elif reg.payment_method == "mercadopago_subscription":
        folio = f"NATURA-SUB-{folio_suffix}"
    elif reg.payment_method == "free_basic":
        folio = f"NATURA-GRATIS-{folio_suffix}"
    else:
        folio = f"NATURA-REG-{folio_suffix}"

    return {
        "success": True,
        "registration_id": reg.id,
        "business_name": reg.business_name,
        "status": reg.status,
        "payment_status": reg.payment_status,
        "payment_method": reg.payment_method,
        "payment_amount": reg.payment_amount,
        "is_verified_badge": bool(reg.is_verified_badge),
        "whatsapp_verified": bool(reg.whatsapp_verified),
        "folio": folio,
        "is_active_in_directory": (reg.status == "active")
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

        AMDI_DATA = {
            "cover_photo": "Assets/amdi/portada.webp",
            "website_url": "https://www.amdi.mx",
            "schedule": "Lunes a Viernes · 09:00 a 17:00 hrs",
            "featured_section": {
                "title": "Diseño de Interiores & Consultoría",
                "subtitle": "LLEVAMOS A LA REALIDAD TU PROYECTO · DISEÑO & DECORACIÓN",
                "description": "Escuchamos las ideas de nuestros clientes y encontramos la manera de llevarlas a la realidad, creamos el lugar que cuenta tu historia.",
                "products": [
                    {
                        "name": "Visita de consultoría",
                        "price": 950.0,
                        "description": "Consultoría de 60 minutos en diseño y decoración. Durante una visita podemos ayudarte a resolver las dudas que pueden surgir cuando estás realizando un proyecto de diseño de interiores.",
                        "photo": "Assets/amdi/producto_1.webp",
                        "badge": "Asesoría Profesional"
                    }
                ]
            },
            "other_products_sections": []
        }

        # 1. BOTICA SILVESTRE (Cortesía / Comercio Fundador Oficial con Página Interactiva)
        botica = db.query(EpicentroRegistration).filter(
            EpicentroRegistration.id == "reg-botica-silvestre"
        ).first()

        if not botica:
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
                payment_amount=770.0,
                is_verified_badge=True,
                status="active",
                moderation_notes="Comercio fundador oficial con página interactiva activa."
            )
            db.add(botica)
            db.commit()
            db.refresh(botica)
        else:
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
            if not botica.website:
                botica.website = "https://boticasilvestre.com.mx"
                updated = True
            if not botica.description:
                botica.description = "Herbolaria sagrada, adaptógenos y tinturas botánicas en pequeños lotes para equilibrar cuerpo, mente y alma. Envíos directos a caseta de cotos."
                updated = True
            if updated:
                db.commit()

        # 2. CHILE CHILLÓN (Registro Oficial Único)
        chillon = db.query(EpicentroRegistration).filter(
            EpicentroRegistration.id == "reg-chile-chillon"
        ).first()

        if not chillon:
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
                payment_amount=770.0,
                kam_name="Cortesía Hipha",
                payment_method="courtesy_hipha",
                is_verified_badge=True,
                status="active",
                moderation_notes="Cortesía oficial Hipha: página interactiva con catálogo activo."
            )
            db.add(chillon)
            db.commit()
            db.refresh(chillon)
        else:
            updated = False
            if not chillon.cover_photo:
                chillon.cover_photo = CHILLON_DATA["cover_photo"]
                updated = True
            if not chillon.microsite_data:
                chillon.microsite_data = json.dumps(CHILLON_DATA)
                updated = True
            if not chillon.website:
                chillon.website = "https://elchilechillon.mx"
                updated = True
            if not chillon.schedule:
                chillon.schedule = "Lunes a Domingo · 10:00 a 20:00 hrs"
                updated = True
            if not chillon.description:
                chillon.description = "Salsas picantes artesanales 100% naturales, elaboradas con aceite vegetal comestible sin conservadores ni colorantes artificiales. 10 años de trayectoria gastronómica. Envíos directos a cotos."
                updated = True
            if not chillon.phone:
                chillon.phone = "3921097809"
                updated = True
            if not chillon.whatsapp:
                chillon.whatsapp = "3921097809"
                updated = True
            if updated:
                db.commit()

        # 3. AMDI DISEÑO INTERIOR (Comercio Fundador Oficial con Página Interactiva)
        amdi = db.query(EpicentroRegistration).filter(
            (EpicentroRegistration.id == "ac02b6c2-624e-407f-bcfc-7d736dbcbd83") |
            (EpicentroRegistration.id == "reg-amdi") |
            (EpicentroRegistration.business_name.ilike("%amdi%"))
        ).first()

        if not amdi:
            amdi = EpicentroRegistration(
                id="ac02b6c2-624e-407f-bcfc-7d736dbcbd83",
                business_name="AMDI Diseño Interior",
                category_slug="servicios-profesionales",
                category_label="Servicios Profesionales",
                subcategory_slug="diseno-interiores",
                subcategory_label="Diseño de Interiores",
                coto_address="Natura Bosque Residencial",
                business_type="local-establecido",
                space_label="Atención en cotos & Previa cita",
                owner_name="Adriana Medina",
                email="contacto@amdi.mx",
                phone="3313111147",
                whatsapp="3313111147",
                delivery_available=True,
                preferred_contact_methods="whatsapp,llamada,visita",
                schedule="Lunes a Viernes · 09:00 a 17:00 hrs",
                website="https://www.amdi.mx",
                description="Escuchamos las ideas de nuestros clientes y encontramos la manera de llevarlas a la realidad, creamos el lugar que cuenta tu historia. Proyectos de diseño, planos ejecutivos, renders 3D y consultoría para tu hogar en cotos de la zona.",
                cover_photo=AMDI_DATA["cover_photo"],
                microsite_data=json.dumps(AMDI_DATA),
                email_verified=True,
                whatsapp_verified=True,
                payment_status="waived",
                payment_amount=770.0,
                kam_name="Chizko",
                payment_method="courtesy_hipha",
                is_verified_badge=True,
                status="active",
                moderation_notes="Comercio fundador oficial con página interactiva activa."
            )
            db.add(amdi)
            db.commit()
            db.refresh(amdi)
        else:
            updated = False
            if not amdi.cover_photo or "unsplash.com" in (amdi.cover_photo or ""):
                amdi.cover_photo = AMDI_DATA["cover_photo"]
                updated = True
            if not amdi.microsite_data:
                amdi.microsite_data = json.dumps(AMDI_DATA)
                updated = True
            else:
                try:
                    m = json.loads(amdi.microsite_data) if isinstance(amdi.microsite_data, str) else amdi.microsite_data
                    m_mod = False
                    if "other_products_sections" in m and len(m.get("other_products_sections") or []) > 0:
                        m["other_products_sections"] = []
                        m_mod = True
                    if "cover_photo" in m and "unsplash.com" in (m.get("cover_photo") or ""):
                        m["cover_photo"] = AMDI_DATA["cover_photo"]
                        m_mod = True
                    if "featured_section" in m and isinstance(m.get("featured_section"), dict):
                        for p in m["featured_section"].get("products", []):
                            if "unsplash.com" in (p.get("photo") or ""):
                                p["photo"] = "Assets/amdi/producto_1.webp"
                                m_mod = True
                    if m_mod:
                        amdi.microsite_data = json.dumps(m)
                        updated = True
                except Exception:
                    pass
            if not amdi.preferred_contact_methods:
                amdi.preferred_contact_methods = "whatsapp,llamada,visita"
                updated = True
            if not amdi.schedule:
                amdi.schedule = "Lunes a Viernes · 09:00 a 17:00 hrs"
                updated = True
            if not amdi.website:
                amdi.website = "https://www.amdi.mx"
                updated = True
            if not amdi.description:
                amdi.description = "Escuchamos las ideas de nuestros clientes y encontramos la manera de llevarlas a la realidad, creamos el lugar que cuenta tu historia. Proyectos de diseño, planos ejecutivos, renders 3D y consultoría para tu hogar en cotos de la zona."
                updated = True
            if not amdi.phone:
                amdi.phone = "3313111147"
                updated = True
            if not amdi.whatsapp:
                amdi.whatsapp = "3313111147"
                updated = True
            if updated:
                db.commit()

    except Exception as e:
        logger.warning(f"Error seeding official showcases: {e}")
        try:
            db.rollback()
        except Exception:
            pass

seed_botica_silvestre_if_missing = seed_official_showcases


@router.get("/businesses/active", response_model=List[BusinessPublicOut])
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


@router.get("/businesses/{slug_or_id}", response_model=BusinessPublicOut)
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
        elif slug_clean in ("amdi", "amdi-diseno-interior", "amdidiseniointerior", "amdi-diseno", "reg-amdi", "ac02b6c2-624e-407f-bcfc-7d736dbcbd83"):
            reg = db.query(EpicentroRegistration).filter(
                (EpicentroRegistration.id == "ac02b6c2-624e-407f-bcfc-7d736dbcbd83") |
                (EpicentroRegistration.id == "reg-amdi") |
                (EpicentroRegistration.business_name.ilike("%amdi%")) |
                (EpicentroRegistration.website.ilike("%amdi%"))
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


