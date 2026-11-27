import os
import re
import json
import logging
import unicodedata
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.epicentro_registration import EpicentroRegistration, EpicentroBlacklist
from app.api.mercadopago import refund_mercadopago_payment
from app.core.mailer import (
    send_epizentro_suspension_email_merchant,
    send_epizentro_sentinel_alert_team
)

logger = logging.getLogger(__name__)

# Palabras clave y patrones de tolerancia cero en México
ZERO_TOLERANCE_PATTERNS = {
    "armas_violencia": [
        r"\barmas?\s+de\s+fuego\b",
        r"\bpistolas?\b",
        r"\brifles?\b",
        r"\bescopetas?\b",
        r"\bmunicion(es)?\b",
        r"\bcartuchos?\s+calibre\b",
        r"\bgranadas?\b",
        r"\bsilenciador(es)?\b",
        r"\bsicari(ato|o|os)\b",
        r"\bexplosivos?\b",
        r"\bchalecos?\s+antibalas\b",
        r"\bventa\s+de\s+armas?\b"
    ],
    "sustancias_ilicitas": [
        r"\bcocaina\b",
        r"\bcristal\s+meth\b",
        r"\bfentanilo\b",
        r"\bmetanfetaminas?\b",
        r"\bestupefacientes?\b",
        r"\btachas\b",
        r"\bextasis\b",
        r"\bpoppers\b",
        r"\bhongos\s+alucinogenos\b",
        r"\bvapeadores?\s+sin\s+cofepris\b",
        r"\bdrogas?\s+a\s+domicilio\b"
    ],
    "servicios_sexuales_adultos": [
        r"\bprostitucion\b",
        r"\bprostitutas?\b",
        r"\bdamas?\s+de\s+compania\b",
        r"\bescorts?\b",
        r"\bmasajes?\s+con\s+final\s+feliz\b",
        r"\bmasajes?\s+eroticos?\b",
        r"\bservicios?\s+eroticos?\b",
        r"\bpornografia\b",
        r"\bmaterial\s+explicito\b",
        r"\bwebcam\s+erotica\b",
        r"\bstriptease\s+privado\b",
        r"\bcarinosas\b",
        r"\bprepagos?\b",
        r"\bsexo\s+por\s+dinero\b"
    ],
    "apuestas_fraudes": [
        r"\bpeleas?\s+de\s+gallos\s+clandestinas?\b",
        r"\bapuestas?\s+clandestinas?\b",
        r"\bcasino\s+clandestino\b",
        r"\bprestamos?\s+gota\s+a\s+gota\b",
        r"\bclonacion\s+de\s+tarjetas\b",
        r"\blavado\s+de\s+dinero\b",
        r"\bpiramide\s+financiera\b"
    ]
}


def normalize_text(text: Optional[str]) -> str:
    """Normaliza texto eliminando acentos, diacríticos y convirtiendo a minúsculas."""
    if not text:
        return ""
    text_clean = unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8')
    return text_clean.lower()


def inspect_text_heuristics(text_corpus: str) -> List[str]:
    """Evalúa el texto contra las expresiones regulares de tolerancia cero."""
    normalized = normalize_text(text_corpus)
    violations = []

    category_labels = {
        "armas_violencia": "Armas de fuego o violencia armada",
        "sustancias_ilicitas": "Narcóticos o sustancias ilegales",
        "servicios_sexuales_adultos": "Servicios sexuales o contenido para adultos",
        "apuestas_fraudes": "Apuestas clandestinas o esquemas ilícitos"
    }

    for cat, patterns in ZERO_TOLERANCE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, normalized):
                violations.append(f"{category_labels.get(cat, cat)}: coincide con patrón '{pat}'")

    return violations


async def inspect_with_gemini(business_data: Dict[str, Any]) -> Dict[str, Any]:
    """Consulta la API de Gemini para análisis semántico profundo si hay API key configurada."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"available": False}

    prompt = f"""
    Eres el Agente Centinela de Moderación para 'Epizentro Natura', un directorio comercial comunitario en cotos residenciales de Zapopan, Jalisco, México.
    Tu objetivo es salvaguardar a la comunidad residencial detectando negocios o publicaciones ilegales, armas, drogas, prostitución, servicios sexuales para adultos, pornografía o estafas.

    Datos del Comercio:
    - Nombre Comercial: {business_data.get('business_name')}
    - Giro: {business_data.get('category_label')} ({business_data.get('subcategory_label')})
    - Descripción: {business_data.get('description')}
    - Productos / Catálogo: {business_data.get('products')}
    - Ubicación / Coto: {business_data.get('coto_address')}
    - Sitio Web: {business_data.get('website')}

    Responde ÚNICAMENTE un objeto JSON válido con este formato:
    {{
      "verdict": "SAFE" | "SUSPICIOUS" | "CRITICAL_VIOLATION",
      "reasons": ["motivo 1", "motivo 2"],
      "confidence": 0.95
    }}
    """

    try:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
                parsed = json.loads(raw_text)
                return {"available": True, "data": parsed}
    except Exception as e:
        logger.warning(f"[SENTINEL] Error consultando Gemini: {e}")

    return {"available": False}


def check_is_blacklisted(db: Session, phone: Optional[str] = None, email: Optional[str] = None) -> Optional[EpicentroBlacklist]:
    """Verifica si un teléfono o correo está registrado en la lista negra."""
    if not phone and not email:
        return None

    query = db.query(EpicentroBlacklist)
    filters = []
    if phone:
        phone_clean = re.sub(r"\D", "", phone)[-10:]
        if phone_clean:
            filters.append(EpicentroBlacklist.phone.ilike(f"%{phone_clean}%"))
    if email:
        email_clean = email.strip().lower()
        if email_clean:
            filters.append(EpicentroBlacklist.email == email_clean)

    if filters:
        from sqlalchemy import or_
        return query.filter(or_(*filters)).first()
    return None


async def run_sentinel_audit(
    registration_id: str,
    db: Session,
    refund_on_violation: bool = True
) -> Dict[str, Any]:
    """
    Ejecuta la auditoría automatizada en tiempo récord:
    1. Heurísticas duras (<10ms).
    2. Análisis semántico con Gemini si aplica.
    3. Si se detecta infracción crítica: activa el Kill-Switch, suspende la ficha, reembolsa 100% y banea.
    """
    reg = db.query(EpicentroRegistration).filter(EpicentroRegistration.id == registration_id).first()
    if not reg:
        return {"status": "error", "message": "Registro no encontrado"}

    # Recopilar corpus de texto del comercio
    corpus_parts = [
        reg.business_name or "",
        reg.description or "",
        reg.category_label or "",
        reg.subcategory_label or "",
        reg.coto_address or "",
        reg.website or ""
    ]

    # Extraer nombres y descripciones de productos del JSON si existen
    if reg.microsite_data:
        try:
            mdata = json.loads(reg.microsite_data)
            prods = mdata.get("products", [])
            for p in prods:
                corpus_parts.append(p.get("name", ""))
                corpus_parts.append(p.get("description", ""))
        except Exception:
            pass

    full_corpus = " \n ".join(corpus_parts)

    # 1. Auditoría heurística
    heuristic_violations = inspect_text_heuristics(full_corpus)

    # 2. Auditoría IA complementaria
    gemini_result = await inspect_with_gemini({
        "business_name": reg.business_name,
        "category_label": reg.category_label,
        "subcategory_label": reg.subcategory_label,
        "description": reg.description,
        "products": full_corpus,
        "coto_address": reg.coto_address,
        "website": reg.website
    })

    # Determinar veredicto
    verdict = "SAFE"
    reasons = []

    if heuristic_violations:
        verdict = "CRITICAL_VIOLATION"
        reasons.extend(heuristic_violations)

    if gemini_result.get("available"):
        gdata = gemini_result.get("data", {})
        gverdict = gdata.get("verdict", "SAFE").upper()
        greasons = gdata.get("reasons", [])
        if gverdict == "CRITICAL_VIOLATION":
            verdict = "CRITICAL_VIOLATION"
            reasons.extend(greasons)
        elif gverdict == "SUSPICIOUS" and verdict != "CRITICAL_VIOLATION":
            verdict = "SUSPICIOUS"
            reasons.extend(greasons)

    now = datetime.now(timezone.utc)
    reg.ai_moderated_at = now

    # ACCIONES SEGÚN VEREDICTO:
    if verdict == "CRITICAL_VIOLATION":
        logger.warning(f"[SENTINEL] 🚨 KILL-SWITCH ACTIVADO para {reg.business_name} ({reg.id}). Motivos: {reasons}")
        
        # 1. Suspender publicación
        reg.status = "suspended"
        reg.ai_moderation_status = "violation"
        reg.ai_moderation_notes = "Infracción crítica detectada por Centinela IA:\n" + "\n".join(reasons)
        reg.moderation_notes = (reg.moderation_notes or "") + f"\n[Centinela Kill-Switch {now.isoformat()}]: Suspensión automática."

        # 2. Agregar a Lista Negra (Blacklist)
        try:
            bl_entry = EpicentroBlacklist(
                phone=reg.whatsapp or reg.phone,
                email=reg.email,
                business_name=reg.business_name,
                reason=f"Violación de T&C: {'; '.join(reasons[:2])}"
            )
            db.add(bl_entry)
        except Exception as bl_err:
            logger.error(f"[SENTINEL] Error agregando a Blacklist: {bl_err}")

        # 3. Devolución automática 100% en Mercado Pago si pagó
        refund_done = False
        if refund_on_violation and reg.mercadopago_payment_id:
            try:
                ref_res = refund_mercadopago_payment(reg.mercadopago_payment_id)
                if ref_res.get("success"):
                    reg.payment_status = "refunded"
                    refund_done = True
                    logger.info(f"[SENTINEL] Reembolso 100% exitoso en MP para {reg.business_name} (Payment: {reg.mercadopago_payment_id})")
                else:
                    logger.error(f"[SENTINEL] Falla al ejecutar reembolso en MP: {ref_res.get('error')}")
            except Exception as ref_err:
                logger.error(f"[SENTINEL] Excepción en reembolso de MP: {ref_err}")

        db.commit()
        db.refresh(reg)

        # 4. Enviar correos de notificación
        try:
            summary_reason = "; ".join(reasons[:2]) if reasons else "Giro restringido o contenido inapropiado según normas comunitarias."
            await send_epizentro_suspension_email_merchant(reg, reason=summary_reason, refund_issued=refund_done)
        except Exception as mail_err:
            logger.error(f"[SENTINEL] Error enviando correo de suspensión: {mail_err}")

        try:
            await send_epizentro_sentinel_alert_team(reg, {"reasons": reasons, "refund_issued": refund_done}, level="critical")
        except Exception as mail_err:
            logger.error(f"[SENTINEL] Error enviando alerta de centinela al equipo: {mail_err}")

        return {
            "status": "suspended",
            "verdict": verdict,
            "reasons": reasons,
            "refund_issued": refund_done
        }

    elif verdict == "SUSPICIOUS":
        logger.info(f"[SENTINEL] ⚠️ Comercio sospechoso marcado para revisión: {reg.business_name} ({reg.id})")
        reg.ai_moderation_status = "flagged"
        reg.ai_moderation_notes = "Alerta Centinela (Requiere revisión humana):\n" + "\n".join(reasons)
        db.commit()

        try:
            await send_epizentro_sentinel_alert_team(reg, {"reasons": reasons}, level="warning")
        except Exception as mail_err:
            logger.error(f"[SENTINEL] Error enviando alerta preventiva al equipo: {mail_err}")

        return {
            "status": "active_flagged",
            "verdict": verdict,
            "reasons": reasons
        }

    else:
        # SAFE
        reg.ai_moderation_status = "passed"
        reg.ai_moderation_notes = "Auditoría de contenido superada exitosamente."
        db.commit()
        return {
            "status": "active",
            "verdict": "SAFE"
        }
