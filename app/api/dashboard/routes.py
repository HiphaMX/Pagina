from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, List
from sqlalchemy.orm import Session
import io
import csv

from app.services.analytics import (
    get_basic_metrics,
    get_top_sections,
    get_traffic_sources,
    get_discovered_clients,
    CLIENTS
)
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from app.core.database import get_db
from app.models.chilechillon_lead import ChileChillonLead
from app.models.workflow_task import WorkflowTask
from app.schemas.workflow import (
    WorkflowTask as WorkflowTaskSchema,
    WorkflowTaskCreate,
    WorkflowTaskUpdate,
    WorkflowMoveRequest
)

router = APIRouter()

@router.get("/clients")
def list_clients(current_user: UserSchema = Depends(get_current_active_user)):
    """Devuelve la lista de clientes disponibles para el dashboard."""
    clients = get_discovered_clients()
    return [{"name": name, "property_id": prop_id} for name, prop_id in clients.items()]

from concurrent.futures import ThreadPoolExecutor

@router.get("/metrics/overview")
def get_dashboard_overview(
    start_date: str = "30daysAgo", 
    end_date: str = "today",
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Recorre todos los clientes para obtener su resumen general.
    Ejecuta las llamadas a Google Analytics en paralelo para respuesta ultra-rápida.
    """
    clients = get_discovered_clients()

    def fetch_client(item):
        client_name, prop_id = item
        data = get_basic_metrics(prop_id, start_date, end_date)
        return {
            "name": client_name,
            "property_id": prop_id,
            "summary": data.get("summary", {}),
            "trend": data.get("trend", [])
        }

    with ThreadPoolExecutor(max_workers=10) as executor:
        overview_data = list(executor.map(fetch_client, clients.items()))
        
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
    clients = get_discovered_clients()
    client_name = next((name for name, pid in clients.items() if pid == property_id), "Desconocido")
    
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

@router.get("/chilechillon/quiniela/export")
def export_chilechillon_leads(db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_active_user)):
    """Genera un archivo CSV con todos los leads registrados para la quiniela."""
    leads = db.query(ChileChillonLead).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Fecha Registro", "Nombre", "Email", "Telefono", "Prediccion Campeon"])
    for lead in leads:
        writer.writerow([
            lead.id,
            lead.created_at.strftime("%Y-%m-%d %H:%M:%S") if lead.created_at else "",
            lead.nombre,
            lead.email,
            lead.telefono,
            lead.prediccion_campeon.upper()
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=chilechillon_quiniela_leads.csv"}
    )


# --- Endpoints de Flujo de Trabajo Semanal (Workflow) ---

@router.get("/workflow/tasks", response_model=List[WorkflowTaskSchema])
def get_workflow_tasks(
    week: str = "current",
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Obtiene las tareas de diseño para una semana específica o todas."""
    query = db.query(WorkflowTask)
    if week and week != "all":
        query = query.filter(WorkflowTask.week_id == week)
    return query.order_by(WorkflowTask.order_index.asc(), WorkflowTask.id.asc()).all()


@router.post("/workflow/tasks", response_model=WorkflowTaskSchema)
def create_workflow_task(
    task_in: WorkflowTaskCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Crea una nueva tarea de diseño en el flujo semanal."""
    task = WorkflowTask(
        week_id=task_in.week_id,
        day=task_in.day,
        client_name=task_in.client_name,
        title=task_in.title,
        estimated_hours=task_in.estimated_hours,
        status=task_in.status,
        notes=task_in.notes,
        order_index=task_in.order_index
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/workflow/tasks/{task_id}", response_model=WorkflowTaskSchema)
def update_workflow_task(
    task_id: int,
    task_in: WorkflowTaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Actualiza una tarea existente."""
    task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    for field, val in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, val)
        
    db.commit()
    db.refresh(task)
    return task


@router.patch("/workflow/tasks/{task_id}/move", response_model=WorkflowTaskSchema)
def move_workflow_task(
    task_id: int,
    move_data: WorkflowMoveRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Mueve rápidamente una tarea entre días o en el backlog."""
    task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task.day = move_data.target_day
    if move_data.target_order_index is not None:
        task.order_index = move_data.target_order_index
        
    db.commit()
    db.refresh(task)
    return task


@router.delete("/workflow/tasks/{task_id}")
def delete_workflow_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Elimina una tarea del flujo semanal."""
    task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    db.delete(task)
    db.commit()
    return {"ok": True, "message": "Tarea eliminada exitosamente"}


