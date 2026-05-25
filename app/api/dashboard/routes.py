from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.services.analytics import get_basic_metrics, get_top_sections, get_traffic_sources, CLIENTS
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/clients")
def list_clients(current_user: UserSchema = Depends(get_current_active_user)):
    """Devuelve la lista de clientes disponibles para el dashboard."""
    return [{"name": name, "property_id": prop_id} for name, prop_id in CLIENTS.items()]

@router.get("/metrics/overview")
def get_dashboard_overview(
    start_date: str = "30daysAgo", 
    end_date: str = "today",
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Recorre todos los clientes para obtener su resumen general.
    Ideal para llenar la tabla principal del dashboard.
    (Nota: En producción, esto podría ser lento si hay muchos clientes, 
    lo ideal es cachear esta respuesta).
    """
    overview_data = []
    
    for client_name, prop_id in CLIENTS.items():
        data = get_basic_metrics(prop_id, start_date, end_date)
        overview_data.append({
            "name": client_name,
            "property_id": prop_id,
            "summary": data.get("summary", {}),
            "trend": data.get("trend", [])
        })
        
    # Ordenar por nuevos usuarios de mayor a menor
    overview_data.sort(key=lambda x: x["summary"].get("newUsers", 0), reverse=True)
    return {"data": overview_data}

@router.get("/metrics/client/{property_id}")
def get_client_details(
    property_id: str, 
    start_date: str = "30daysAgo", 
    end_date: str = "today",
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Obtiene el detalle completo para un solo cliente."""
    # Buscar el nombre del cliente
    client_name = next((name for name, pid in CLIENTS.items() if pid == property_id), "Desconocido")
    
    metrics_data = get_basic_metrics(property_id, start_date, end_date)
    top_sections = get_top_sections(property_id, start_date, end_date)
    traffic_sources = get_traffic_sources(property_id, start_date, end_date)
    
    return {
        "client": {
            "name": client_name,
            "property_id": property_id
        },
        "period": {
            "start": start_date,
            "end": end_date
        },
        "metrics": metrics_data,
        "top_sections": top_sections,
        "traffic_sources": traffic_sources
        # Aquí después agregaremos eventos de FB/IG y clics a botones
    }

