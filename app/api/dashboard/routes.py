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
    WorkflowMoveRequest,
    WorkflowAddRevisionRequest,
    WorkflowMonthlyReport,
    WorkflowMonthlyClientSummary
)
import datetime

def _derive_month_id(week_id: Optional[str]) -> str:
    if week_id and "-W" in week_id:
        try:
            parts = week_id.split("-W")
            year = int(parts[0])
            week = int(parts[1])
            d = datetime.date.fromisocalendar(year, week, 1)
            return d.strftime("%Y-%m")
        except Exception:
            pass
    return datetime.datetime.now().strftime("%Y-%m")


def _derive_task_date(week_id: Optional[str], day: Optional[str]) -> str:
    day_map = {"monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4, "friday": 5}
    if week_id and "-W" in week_id:
        try:
            parts = week_id.split("-W")
            year = int(parts[0])
            week = int(parts[1])
            day_num = day_map.get((day or "").lower(), 1)
            d = datetime.date.fromisocalendar(year, week, day_num)
            return d.strftime("%Y-%m-%d")
        except Exception:
            pass
    return datetime.date.today().strftime("%Y-%m-%d")



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
    week: Optional[str] = "current",
    month: Optional[str] = None,
    client: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Obtiene las tareas de diseño filtradas por semana, mes o cliente."""
    query = db.query(WorkflowTask)
    if week and week != "all":
        query = query.filter(WorkflowTask.week_id == week)
    if month and month != "all":
        query = query.filter(WorkflowTask.month_id == month)
    if client and client != "all":
        query = query.filter(WorkflowTask.client_name == client)
    return query.order_by(WorkflowTask.order_index.asc(), WorkflowTask.id.asc()).all()


@router.post("/workflow/tasks", response_model=WorkflowTaskSchema)
def create_workflow_task(
    task_in: WorkflowTaskCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Crea una nueva tarea de diseño en el flujo semanal."""
    m_id = task_in.month_id or _derive_month_id(task_in.week_id)
    t_date = task_in.task_date or _derive_task_date(task_in.week_id, task_in.day)
    task = WorkflowTask(
        week_id=task_in.week_id,
        day=task_in.day,
        client_name=task_in.client_name,
        title=task_in.title,
        estimated_hours=task_in.estimated_hours,
        revision_hours=task_in.revision_hours or 0.0,
        revisions_count=task_in.revisions_count or 0,
        month_id=m_id,
        task_date=t_date,
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
        
    if not task.month_id and task.week_id:
        task.month_id = _derive_month_id(task.week_id)
    if not task.task_date and task.week_id:
        task.task_date = _derive_task_date(task.week_id, task.day)

    db.commit()
    db.refresh(task)
    return task


@router.post("/workflow/tasks/{task_id}/add-revision", response_model=WorkflowTaskSchema)
def add_revision_to_task(
    task_id: int,
    revision_in: WorkflowAddRevisionRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Añade tiempo de cambios/revisiones en lapsos de media hora (+0.5h)."""
    task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    delta = float(revision_in.delta_hours or 0.5)
    current_rev = float(task.revision_hours or 0.0)
    task.revision_hours = max(0.0, current_rev + delta)

    if delta > 0:
        task.revisions_count = (task.revisions_count or 0) + 1
    elif delta < 0 and task.revisions_count and task.revisions_count > 0:
        task.revisions_count = max(0, task.revisions_count - 1)

    if revision_in.note:
        clean_note = revision_in.note.strip()
        timestamp = datetime.datetime.now().strftime("%d/%m %H:%M")
        addition = f"\n[Ajuste +{delta:.1f}h - {timestamp}]: {clean_note}"
        task.notes = (task.notes or "") + addition

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
    """Mueve rápidamente una tarea entre días."""
    task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task.day = move_data.target_day
    task.task_date = _derive_task_date(task.week_id, task.day)
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


@router.get("/workflow/monthly-report", response_model=WorkflowMonthlyReport)
def get_workflow_monthly_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    month: Optional[str] = None,
    client: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Genera el reporte consolidado de horas trabajadas por cliente para un rango de fechas o mes."""
    import calendar

    # Resolver rango de fechas
    if not start_date or not end_date:
        target_month = month if (month and month != "all") else datetime.datetime.now().strftime("%Y-%m")
        try:
            year, m = map(int, target_month.split("-"))
            first_day = datetime.date(year, m, 1)
            _, last_day_num = calendar.monthrange(year, m)
            last_day = datetime.date(year, m, last_day_num)
            s_date = first_day.strftime("%Y-%m-%d")
            e_date = last_day.strftime("%Y-%m-%d")
        except Exception:
            s_date = datetime.date.today().replace(day=1).strftime("%Y-%m-%d")
            e_date = datetime.date.today().strftime("%Y-%m-%d")
    else:
        s_date = start_date
        e_date = end_date
        target_month = s_date[:7]

    query = db.query(WorkflowTask)
    if client and client != "all":
        query = query.filter(WorkflowTask.client_name == client)

    all_tasks = query.order_by(WorkflowTask.id.desc()).all()

    # Filtrar por rango de fechas
    filtered_tasks = []
    for t in all_tasks:
        d_str = t.task_date or _derive_task_date(t.week_id, t.day)
        if s_date <= d_str <= e_date:
            t.task_date = d_str
            filtered_tasks.append(t)

    # Agrupar por cliente
    client_map = {}
    total_period_hours = 0.0
    total_base_hours = 0.0
    total_rev_hours = 0.0
    completed_tasks_count = 0

    for t in filtered_tasks:
        c_name = t.client_name or "General"
        if c_name not in client_map:
            client_map[c_name] = {
                "client_name": c_name,
                "base_hours": 0.0,
                "revision_hours": 0.0,
                "total_hours": 0.0,
                "tasks_count": 0,
                "completed_count": 0
            }
        b_hours = float(t.estimated_hours or 0.0)
        r_hours = float(t.revision_hours or 0.0)
        t_hours = b_hours + r_hours

        client_map[c_name]["base_hours"] += b_hours
        client_map[c_name]["revision_hours"] += r_hours
        client_map[c_name]["total_hours"] += t_hours
        client_map[c_name]["tasks_count"] += 1

        total_base_hours += b_hours
        total_rev_hours += r_hours
        total_period_hours += t_hours

        if t.status == "completed":
            client_map[c_name]["completed_count"] += 1
            completed_tasks_count += 1

    clients_list = [
        WorkflowMonthlyClientSummary(
            client_name=data["client_name"],
            total_hours=round(data["total_hours"], 2),
            base_hours=round(data["base_hours"], 2),
            revision_hours=round(data["revision_hours"], 2),
            tasks_count=data["tasks_count"],
            completed_count=data["completed_count"]
        )
        for data in sorted(client_map.values(), key=lambda x: x["total_hours"], reverse=True)
    ]

    return WorkflowMonthlyReport(
        month=target_month,
        start_date=s_date,
        end_date=e_date,
        total_hours=round(total_period_hours, 2),
        base_hours=round(total_base_hours, 2),
        revision_hours=round(total_rev_hours, 2),
        total_tasks=len(filtered_tasks),
        completed_tasks=completed_tasks_count,
        clients=clients_list,
        tasks=filtered_tasks
    )



