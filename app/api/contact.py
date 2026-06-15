from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.chilechillon_lead import ChileChillonLead
from app.models.chilechillon_match import ChileChillonMatch
from app.core.mailer import (
    send_contract_followup_email,
    send_lead_followup_email, 
    send_lead_notification_to_team,
    send_newsletter_welcome,
    send_newsletter_notification_to_team,
    send_healthyice_order_customer,
    send_healthyice_order_team,
    send_healthyice_contract_customer,
    send_healthyice_contract_team,
    generate_healthyice_contract_pdf,
    send_whiteclean_confirmation_email,
    send_whiteclean_notification_team,
    send_chilechillon_confirmation_email,
    send_chilechillon_notification_team,
    send_grupogari_confirmation_email,
    send_grupogari_notification_team
)

router = APIRouter()

from typing import Optional

class ContactForm(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    mensaje: str = ""
    firma: Optional[str] = None
    fecha: Optional[str] = None
    fecha_pago: Optional[str] = None
    proyecto: Optional[str] = None
    forma_pago: Optional[str] = None

class HealthyIceContractForm(BaseModel):
    nombre: Optional[str] = None # Representante legal
    razon_social: Optional[str] = None
    rfc: Optional[str] = None
    domicilio: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    tipo_alianza: Optional[str] = "Punto de Venta"
    firma: Optional[str] = ""
    fecha: Optional[str] = None
    
    # Nuevos campos del contrato de colaboracion comercial
    nombre_establecimiento: Optional[str] = ""
    esquema_comercial: Optional[str] = "Compra directa"
    esquema_comercial_otro: Optional[str] = ""
    frecuencia_pagos: Optional[str] = "Semanal"
    metodo_pago: Optional[str] = "Transferencia bancaria"
    metodo_pago_otro: Optional[str] = ""
    vigencia_meses: Optional[int] = 12
    fecha_inicio_dia: Optional[int] = None
    fecha_inicio_mes: Optional[str] = ""
    fecha_inicio_anio: Optional[int] = None
    ciudad_jurisdiccion: Optional[str] = "Guadalajara, Jalisco"
    representante_healthyice: Optional[str] = "FRANCISCO DELGADILLO"
    llenado_manual: Optional[bool] = False

@router.post("/healthyice")
async def submit_healthyice_form(form_data: ContactForm):
    # Enviar correo de confirmación al cliente
    customer_email_sent = await send_healthyice_order_customer(form_data)
    
    # Enviar correo de notificación al equipo
    team_email_sent = await send_healthyice_order_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}

from fastapi import Response

@router.post("/healthyice/contract")
async def submit_healthyice_contract(form_data: HealthyIceContractForm):
    try:
        pdf_bytes = generate_healthyice_contract_pdf(form_data)
        razon_social = form_data.razon_social or "Formato_Manual"
        safe_name = razon_social.replace(' ', '_').replace('/', '_')
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Contrato_HealthyIce_{safe_name}.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")

@router.post("/submit")
async def submit_contact_form(form_data: ContactForm):
    is_contract = form_data.mensaje.startswith("ACEPTACIÓN DE CONTRATO VÍA WEB")
    
    # Enviar correo al lead
    if is_contract:
        lead_email_sent = await send_contract_followup_email(form_data)
    else:
        lead_email_sent = await send_lead_followup_email(form_data.nombre, form_data.email)
    
    # Enviar correo al equipo de HiphaMX
    team_email_sent = await send_lead_notification_to_team(form_data)
    
    if not lead_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}

class NewsletterForm(BaseModel):
    email: EmailStr

@router.post("/newsletter")
async def submit_newsletter_form(form_data: NewsletterForm):
    # Enviar correo de bienvenida al suscriptor
    subscriber_email_sent = await send_newsletter_welcome(form_data.email)
    
    # Enviar notificación al equipo
    team_email_sent = await send_newsletter_notification_to_team(form_data.email)
    
    if not subscriber_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al procesar suscripción")
        
    return {"message": "Suscripción exitosa"}

class WhiteCleanForm(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    servicio: str
    ubicacion: str
    mensaje: Optional[str] = ""

@router.post("/whiteclean")
async def submit_whiteclean_form(form_data: WhiteCleanForm):
    # Enviar correo de confirmación al prospecto
    customer_email_sent = await send_whiteclean_confirmation_email(form_data)
    
    # Enviar aviso con los detalles de la solicitud al equipo
    team_email_sent = await send_whiteclean_notification_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}

class ChileChillonForm(BaseModel):
    nombre: str
    apellido: Optional[str] = ""
    email: EmailStr
    telefono: str
    perfil: str
    mensaje: Optional[str] = ""

@router.post("/chilechillon")
async def submit_chilechillon_form(form_data: ChileChillonForm):
    customer_email_sent = await send_chilechillon_confirmation_email(form_data)
    team_email_sent = await send_chilechillon_notification_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}

class GrupoGariForm(BaseModel):
    nombre: str
    apellido: Optional[str] = ""
    email: EmailStr
    telefono: str
    rol: str
    empleados: str
    industria: str
    servicio: str
    mensaje: Optional[str] = ""

@router.post("/grupogari")
async def submit_grupogari_form(form_data: GrupoGariForm):
    customer_email_sent = await send_grupogari_confirmation_email(form_data)
    team_email_sent = await send_grupogari_notification_team(form_data)
    
    if not customer_email_sent and not team_email_sent:
        raise HTTPException(status_code=500, detail="Error al enviar correos")
        
    return {"message": "Formulario recibido correctamente"}


import time
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Mem cache for reviews
_cached_reviews = None
_cached_time = 0.0

@router.get("/reviews/chilechillon")
async def get_chile_chillon_reviews():
    global _cached_reviews, _cached_time
    
    CACHE_DURATION = 86400.0  # 24 hours
    current_time = time.time()
    
    if _cached_reviews and (current_time - _cached_time < CACHE_DURATION):
        return _cached_reviews
        
    api_key = settings.GOOGLE_PLACES_API_KEY
    if not api_key:
        return get_fallback_reviews()
        
    try:
        async with httpx.AsyncClient() as client:
            # 1. Search for Place ID
            search_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
            search_params = {
                "input": "Chile Chillón, Ocotlán, Jalisco",
                "inputtype": "textquery",
                "fields": "place_id",
                "key": api_key
            }
            search_res = await client.get(search_url, params=search_params)
            search_data = search_res.json()
            
            if search_data.get("status") != "OK" or not search_data.get("candidates"):
                logger.error(f"Google Place Search failed: {search_data}")
                return get_fallback_reviews()
                
            place_id = search_data["candidates"][0]["place_id"]
            
            # 2. Get Place Details
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                "place_id": place_id,
                "fields": "reviews,rating,user_ratings_total",
                "key": api_key,
                "hl": "es"
            }
            details_res = await client.get(details_url, params=details_params)
            details_data = details_res.json()
            
            if details_data.get("status") != "OK":
                logger.error(f"Google Place Details failed: {details_data}")
                return get_fallback_reviews()
                
            result = details_data.get("result", {})
            rating = result.get("rating", 5.0)
            user_ratings_total = result.get("user_ratings_total", 0)
            api_reviews = result.get("reviews", [])
            
            formatted_reviews = []
            for r in api_reviews:
                name = r.get("author_name", "Usuario de Google")
                parts = name.split()
                initials = "".join([p[0].upper() for p in parts if p])[:2] if parts else "G"
                
                formatted_reviews.append({
                    "name": name,
                    "initials": initials,
                    "tag": f"Cliente Google &middot; {r.get('relative_time_description', 'Hace poco')}",
                    "stars": r.get("rating", 5),
                    "text": r.get("text", "")
                })
            
            # Merge Google reviews with local JSON reviews
            local_reviews = get_local_reviews()
            merged_dict = {}
            
            # Seed with local reviews
            for r in local_reviews:
                key = (r["name"].strip().lower(), r["text"].strip().lower()[:50])
                merged_dict[key] = r
                
            # Overwrite or add Google reviews (fresher)
            for r in formatted_reviews:
                key = (r["name"].strip().lower(), r["text"].strip().lower()[:50])
                merged_dict[key] = r
                
            combined_reviews = list(merged_dict.values())
            
            # Fallback to local if no combined reviews
            if not combined_reviews:
                combined_reviews = local_reviews
                
            response_data = {
                "rating": rating,
                "user_ratings_total": max(user_ratings_total, len(combined_reviews)),
                "reviews": combined_reviews
            }
            
            _cached_reviews = response_data
            _cached_time = current_time
            return response_data
            
    except Exception as e:
        logger.error(f"Exception fetching reviews: {str(e)}")
        return get_fallback_reviews()

def get_local_reviews():
    import os
    import json
    
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_path, "assets", "chilechillon_reviews.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error reading reviews JSON database: {str(e)}")
        
    return [
        {
            "name": "Rogelio Chávez",
            "initials": "RC",
            "tag": "Cliente Google &middot; Hace 2 semanas",
            "stars": 5,
            "text": "Es la primera salsa que realmente no solo pica por picar, sino que amplifica el sabor real de las botanas. En mi mesa de fin de semana ya no puede faltar el Habanero."
        },
        {
            "name": "Chef Mario Cárdenas",
            "initials": "MC",
            "tag": "Cliente Google &middot; Hace 1 mes",
            "stars": 5,
            "text": "Implementamos las tres salsas de Chile Chillón directamente en nuestra barra de especialidad. La consistencia del sabor y picor lote por lote nos da total seguridad en la cocina."
        },
        {
            "name": "Alejandra Gutiérrez",
            "initials": "AG",
            "tag": "Cliente Google &middot; Hace 3 semanas",
            "stars": 5,
            "text": "La rotación de producto es fantástica. El cliente final regresa buscando exactamente el mismo lote debido a la calidad. Ha sido una excelente adición comercial a nuestro catálogo."
        },
        {
            "name": "Daniel Moreno",
            "initials": "DM",
            "tag": "Cliente Google &middot; Hace 2 meses",
            "stars": 5,
            "text": "Compré el paquete de las 4 salsas (Árbol, Habanero, Tatemado y Negra) y están increíbles. La salsa Negra con soya y ajo asado le dio un toque único a mis mariscos."
        },
        {
            "name": "Sofía Palacios",
            "initials": "SP",
            "tag": "Cliente Google &middot; Hace 1 semana",
            "stars": 5,
            "text": "El servicio y la rapidez de entrega son excepcionales. Además, las botellas llegaron en perfecto estado. Recomiendo ampliamente la salsa Habanero Tatemado."
        },
        {
            "name": "Héctor Ruiz",
            "initials": "HR",
            "tag": "Cliente Google &middot; Hace 4 semanas",
            "stars": 5,
            "text": "La salsa de Árbol tiene el picor exacto que buscaba, bien equilibrado y con ingredientes totalmente naturales. Ya se volvió mi favorita para los tacos del diario."
        }
    ]

def get_fallback_reviews():
    local_reviews = get_local_reviews()
    total = len(local_reviews)
    rating = 5.0
    if total > 0:
        rating = sum(r.get("stars", 5) for r in local_reviews) / total
    return {
        "rating": round(rating, 1),
        "user_ratings_total": total,
        "reviews": local_reviews
    }

class QuinielaRegisterForm(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    prediccion_campeon: str

class QuinielaVoteForm(BaseModel):
    email: EmailStr
    match_id: int
    voto: str # 'A' or 'B'

@router.post("/chilechillon/quiniela/register")
async def register_chilechillon_quiniela(form_data: QuinielaRegisterForm, db: Session = Depends(get_db)):
    try:
        import json
        db_lead = db.query(ChileChillonLead).filter(ChileChillonLead.email == form_data.email).first()
        
        existing_votes = {}
        
        if db_lead:
            # Keep original name and phone updates, but KEEP original prediction
            db_lead.nombre = form_data.nombre
            db_lead.telefono = form_data.telefono
            
            # If they already had a prediction in database, keep it to prevent manipulation
            if not db_lead.prediccion_campeon:
                db_lead.prediccion_campeon = form_data.prediccion_campeon
                
            pred_campeon = db_lead.prediccion_campeon
            if db_lead.votos:
                try:
                    existing_votes = json.loads(db_lead.votos)
                except Exception:
                    existing_votes = {}
        else:
            new_lead = ChileChillonLead(
                nombre=form_data.nombre,
                email=form_data.email,
                telefono=form_data.telefono,
                prediccion_campeon=form_data.prediccion_campeon,
                votos="{}"
            )
            db.add(new_lead)
            pred_campeon = form_data.prediccion_campeon
            
        db.commit()
        return {
            "message": "Registro exitoso",
            "prediccion_campeon": pred_campeon,
            "votos": existing_votes
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar participante: {str(e)}")

@router.post("/chilechillon/quiniela/vote")
async def register_chilechillon_vote(form_data: QuinielaVoteForm, db: Session = Depends(get_db)):
    try:
        import json
        db_lead = db.query(ChileChillonLead).filter(ChileChillonLead.email == form_data.email).first()
        if not db_lead:
            raise HTTPException(status_code=404, detail="Usuario no registrado")
        
        votes = {}
        if db_lead.votos:
            try:
                votes = json.loads(db_lead.votos)
            except Exception:
                votes = {}
                
        match_id_str = str(form_data.match_id)
        
        # Prevent modifying votes
        if match_id_str in votes:
            raise HTTPException(status_code=400, detail="Ya has votado en este partido y no se puede modificar")
            
        votes[match_id_str] = form_data.voto
        db_lead.votos = json.dumps(votes)
        db.commit()
        
        return {"message": "Voto registrado exitosamente", "votos": votes}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar voto: {str(e)}")

@router.get("/chilechillon/quiniela/results")
async def get_quiniela_results(db: Session = Depends(get_db)):
    try:
        import json
        leads = db.query(ChileChillonLead).all()
        
        # Initialize counts for matches 1 to 13
        results = {str(i): {"A": 0, "B": 0} for i in range(1, 14)}
        
        for lead in db.query(ChileChillonLead).all():
            if lead.votos:
                try:
                    user_votes = json.loads(lead.votos)
                    for match_id, opt in user_votes.items():
                        if match_id in results and opt in ["A", "B"]:
                            results[match_id][opt] += 1
                except Exception:
                    continue
                    
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resultados: {str(e)}")

@router.get("/chilechillon/quiniela/leaderboard")
async def get_quiniela_leaderboard(email: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        import json
        leads = db.query(ChileChillonLead).all()
        leaderboard_data = []
        
        current_user_email = email.lower().strip() if email else ""
        
        for lead in leads:
            lead_email_lower = lead.email.lower().strip()
            email_parts = lead_email_lower.split("@")
            if len(email_parts) == 2:
                local_part, domain = email_parts
                masked_local = local_part[:2] + "***" if len(local_part) > 2 else local_part + "***"
                masked_email = f"{masked_local}@{domain}"
            else:
                masked_email = "***"
            
            try:
                votes_dict = json.loads(lead.votos) if lead.votos else {}
            except Exception:
                votes_dict = {}
                
            leaderboard_data.append({
                "name": lead.nombre,
                "email": masked_email,
                "fav": lead.prediccion_campeon,
                "votes": votes_dict,
                "is_me": (lead_email_lower == current_user_email)
            })
        return leaderboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tabla de posiciones: {str(e)}")

@router.get("/chilechillon/quiniela/user")
async def get_quiniela_user(email: str, db: Session = Depends(get_db)):
    try:
        import json
        email = email.lower().strip()
        lead = db.query(ChileChillonLead).filter(ChileChillonLead.email == email).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Usuario no registrado")
        
        try:
            votes_dict = json.loads(lead.votos) if lead.votos else {}
        except Exception:
            votes_dict = {}
            
        return {
            "nombre": lead.nombre,
            "email": lead.email,
            "prediccion_campeon": lead.prediccion_campeon,
            "votos": votes_dict
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos del usuario: {str(e)}")

INITIAL_MATCHES = [
    { "id": 1, "phase": "grupo", "teamA": "arb", "teamB": "neg", "scoreA": None, "scoreB": None, "status": "active" },
    { "id": 2, "phase": "grupo", "teamA": "hab", "teamB": "tat", "scoreA": None, "scoreB": None, "status": "active" },
    { "id": 3, "phase": "grupo", "teamA": "ser", "teamB": "arb", "scoreA": None, "scoreB": None, "status": "active" },
    { "id": 4, "phase": "grupo", "teamA": "neg", "teamB": "hab", "scoreA": None, "scoreB": None, "status": "active" },
    { "id": 5, "phase": "grupo", "teamA": "tat", "teamB": "ser", "scoreA": None, "scoreB": None, "status": "active" },
    { "id": 6, "phase": "grupo", "teamA": "arb", "teamB": "hab", "scoreA": None, "scoreB": None, "status": "active" },
    { "id": 7, "phase": "grupo", "teamA": "neg", "teamB": "tat", "scoreA": None, "scoreB": None, "status": "active" },
    { "id": 8, "phase": "grupo", "teamA": "ser", "teamB": "hab", "scoreA": None, "scoreB": None, "status": "active" },
    { "id": 9, "phase": "grupo", "teamA": "arb", "teamB": "tat", "scoreA": None, "scoreB": None, "status": "active" },
    { "id": 10, "phase": "grupo", "teamA": "neg", "teamB": "ser", "scoreA": None, "scoreB": None, "status": "active" },
    { "id": 11, "phase": "semifinal", "teamA": None, "teamB": None, "scoreA": None, "scoreB": None, "status": "upcoming" },
    { "id": 12, "phase": "semifinal", "teamA": None, "teamB": None, "scoreA": None, "scoreB": None, "status": "upcoming" },
    { "id": 13, "phase": "final", "teamA": None, "teamB": None, "scoreA": None, "scoreB": None, "status": "upcoming" }
]

class QuinielaMatchUpdateForm(BaseModel):
    email: str
    password: str
    id: int
    phase: str
    teamA: Optional[str] = None
    teamB: Optional[str] = None
    scoreA: Optional[int] = None
    scoreB: Optional[int] = None
    status: str

class QuinielaMatchResetForm(BaseModel):
    email: str
    password: str

class QuinielaAdminVerifyForm(BaseModel):
    email: str
    password: str

@router.post("/chilechillon/quiniela/admin/verify")
async def verify_quiniela_admin(form_data: QuinielaAdminVerifyForm):
    email = form_data.email.lower().strip()
    if email == "efe.creativo@gmail.com" and form_data.password == "SoyElWero":
        return {"status": "ok", "message": "Autenticación exitosa"}
    raise HTTPException(status_code=401, detail="Usuario o contraseña de administrador incorrectos")

@router.get("/chilechillon/quiniela/matches")
async def get_quiniela_matches(db: Session = Depends(get_db)):
    try:
        matches = db.query(ChileChillonMatch).order_by(ChileChillonMatch.id.asc()).all()
        if not matches:
            for m_data in INITIAL_MATCHES:
                db_match = ChileChillonMatch(
                    id=m_data["id"],
                    phase=m_data["phase"],
                    teamA=m_data["teamA"],
                    teamB=m_data["teamB"],
                    scoreA=m_data["scoreA"],
                    scoreB=m_data["scoreB"],
                    status=m_data["status"]
                )
                db.add(db_match)
            db.commit()
            matches = db.query(ChileChillonMatch).order_by(ChileChillonMatch.id.asc()).all()
            
        return [
            {
                "id": m.id,
                "phase": m.phase,
                "teamA": m.teamA,
                "teamB": m.teamB,
                "scoreA": m.scoreA,
                "scoreB": m.scoreB,
                "status": m.status
            }
            for m in matches
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener partidos: {str(e)}")

@router.post("/chilechillon/quiniela/matches/update")
async def update_quiniela_match(form_data: QuinielaMatchUpdateForm, db: Session = Depends(get_db)):
    try:
        email = form_data.email.lower().strip()
        if email != "efe.creativo@gmail.com" or form_data.password != "SoyElWero":
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar partidos")
            
        db_match = db.query(ChileChillonMatch).filter(ChileChillonMatch.id == form_data.id).first()
        if not db_match:
            raise HTTPException(status_code=404, detail="Partido no encontrado")
            
        db_match.phase = form_data.phase
        db_match.teamA = form_data.teamA
        db_match.teamB = form_data.teamB
        db_match.scoreA = form_data.scoreA
        db_match.scoreB = form_data.scoreB
        db_match.status = form_data.status
        
        db.commit()
        return {"message": "Partido actualizado exitosamente"}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar partido: {str(e)}")

@router.post("/chilechillon/quiniela/matches/reset")
async def reset_quiniela_matches(form_data: QuinielaMatchResetForm, db: Session = Depends(get_db)):
    try:
        email = form_data.email.lower().strip()
        if email != "efe.creativo@gmail.com" or form_data.password != "SoyElWero":
            raise HTTPException(status_code=403, detail="No tienes permisos para reiniciar partidos")
            
        db.query(ChileChillonMatch).delete()
        
        for m_data in INITIAL_MATCHES:
            db_match = ChileChillonMatch(
                id=m_data["id"],
                phase=m_data["phase"],
                teamA=m_data["teamA"],
                teamB=m_data["teamB"],
                scoreA=m_data["scoreA"],
                scoreB=m_data["scoreB"],
                status=m_data["status"]
            )
            db.add(db_match)
            
        leads = db.query(ChileChillonLead).all()
        for lead in leads:
            lead.votos = "{}"
            
        db.commit()
        return {"message": "Partidos y votos reiniciados exitosamente"}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al reiniciar partidos: {str(e)}")


