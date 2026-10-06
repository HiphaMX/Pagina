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
    get_audience_breakdown,
    get_discovered_clients,
    CLIENTS
)
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from app.core.database import get_db
from app.models.chilechillon_lead import ChileChillonLead
from app.models.workflow_task import WorkflowTask
from app.models.client import AgencyClient
from app.models.email_log import SentEmailLog
from app.schemas.workflow import (
    WorkflowTask as WorkflowTaskSchema,
    WorkflowTaskCreate,
    WorkflowTaskUpdate,
    WorkflowMoveRequest,
    WorkflowAddRevisionRequest,
    WorkflowMonthlyReport,
    WorkflowMonthlyClientSummary,
    WorkflowRolloverRequest,
    WorkflowRolloverResponse
)
from app.schemas.client import (
    AgencyClient as AgencyClientSchema,
    AgencyClientCreate,
    AgencyClientUpdate,
    SendAgencyEmailRequest,
    SentEmailLogResponse
)
from app.core.mailer import send_custom_agency_email
import datetime

def _get_current_iso_week_id() -> str:
    today = datetime.date.today()
    iso_year, iso_week, _ = today.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _get_next_iso_week_id(week_id: Optional[str]) -> str:
    if week_id and "-W" in week_id:
        try:
            parts = week_id.split("-W")
            year = int(parts[0])
            week = int(parts[1])
            monday = datetime.date.fromisocalendar(year, week, 1)
            next_monday = monday + datetime.timedelta(days=7)
            iso_year, iso_week, _ = next_monday.isocalendar()
            return f"{iso_year}-W{iso_week:02d}"
        except Exception:
            pass
    today = datetime.date.today()
    next_day = today + datetime.timedelta(days=7)
    iso_year, iso_week, _ = next_day.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


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
def list_clients(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Devuelve la lista unificada de clientes disponibles para el dashboard."""
    clients = get_discovered_clients()
    combined = {name: {"name": name, "property_id": prop_id, "source": "ga4"} for name, prop_id in clients.items()}
    
    try:
        db_clients = db.query(AgencyClient).filter(AgencyClient.status == "active").all()
        for c in db_clients:
            if c.name not in combined:
                combined[c.name] = {
                    "name": c.name,
                    "property_id": c.ga4_property_id or "",
                    "source": "database",
                    "client_id": c.id
                }
            else:
                combined[c.name]["client_id"] = c.id
                if c.ga4_property_id:
                    combined[c.name]["property_id"] = c.ga4_property_id
    except Exception as e:
        print(f"Warning: could not merge db clients in list_clients: {e}")

    return list(combined.values())

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
    try:
        clients = get_discovered_clients()

        def fetch_client(item):
            client_name, prop_id = item
            try:
                data = get_basic_metrics(prop_id, start_date, end_date)
                return {
                    "name": client_name,
                    "property_id": prop_id,
                    "summary": data.get("summary", {"newUsers": 0, "activeUsers": 0, "views": 0}),
                    "trend": data.get("trend", [])
                }
            except Exception as e:
                print(f"Error procesando cliente {client_name} ({prop_id}): {e}")
                return {
                    "name": client_name,
                    "property_id": prop_id,
                    "summary": {"newUsers": 0, "activeUsers": 0, "views": 0},
                    "trend": [],
                    "error": str(e)
                }

        with ThreadPoolExecutor(max_workers=10) as executor:
            overview_data = list(executor.map(fetch_client, clients.items()))
            
        # Ordenar por nuevos usuarios de mayor a menor
        overview_data.sort(key=lambda x: x.get("summary", {}).get("newUsers", 0), reverse=True)
        return {"data": overview_data}
    except Exception as e:
        print(f"Error general en get_dashboard_overview: {e}")
        return {"data": [], "error": str(e)}

@router.get("/metrics/client/{property_id}")
def get_client_details(
    property_id: str, 
    start_date: str = "30daysAgo", 
    end_date: str = "today",
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Obtiene el detalle completo para un solo cliente."""
    try:
        clients = get_discovered_clients()
        client_name = next((name for name, pid in clients.items() if pid == property_id), "Desconocido")
        
        metrics_data = get_basic_metrics(property_id, start_date, end_date)
        top_sections = get_top_sections(property_id, start_date, end_date)
        traffic_sources = get_traffic_sources(property_id, start_date, end_date)
        audience_data = get_audience_breakdown(property_id, start_date, end_date)
        
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
            "traffic_sources": traffic_sources,
            "audience": audience_data
        }
    except Exception as e:
        print(f"Error general en get_client_details para {property_id}: {e}")
        return {
            "client": {"name": "Desconocido", "property_id": property_id},
            "period": {"start": start_date, "end": end_date},
            "metrics": {"summary": {"newUsers": 0, "activeUsers": 0, "views": 0}, "trend": []},
            "top_sections": [],
            "traffic_sources": [],
            "audience": {"devices": [], "demographics": {"gender": [], "age": []}, "locations": []},
            "error": str(e)
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
    auto_rollover: bool = True,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Obtiene las tareas de diseño filtradas por semana, mes o cliente."""
    resolved_week = week
    curr_week_id = _get_current_iso_week_id()
    if resolved_week == "current":
        resolved_week = curr_week_id

    # Regla: Cualquier diseño de semanas anteriores que no se haya marcado como completado
    # se transfiere automáticamente al lunes de la semana actual al consultar la semana en curso
    if auto_rollover and resolved_week == curr_week_id:
        past_incomplete = db.query(WorkflowTask).filter(
            WorkflowTask.week_id < curr_week_id,
            WorkflowTask.status != "completed"
        ).all()
        if past_incomplete:
            for t in past_incomplete:
                t.week_id = curr_week_id
                t.day = "monday"
                t.task_date = _derive_task_date(curr_week_id, "monday")
                t.month_id = _derive_month_id(curr_week_id)
            db.commit()

    query = db.query(WorkflowTask)
    if resolved_week and resolved_week != "all":
        query = query.filter(WorkflowTask.week_id == resolved_week)
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
        actual_hours=task_in.actual_hours,
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


@router.post("/workflow/tasks/rollover", response_model=WorkflowRolloverResponse)
def rollover_incomplete_workflow_tasks(
    req: Optional[WorkflowRolloverRequest] = None,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Mueve todas las tareas de diseño no completadas de la semana origen al Lunes de la semana destino."""
    from_week = (req.from_week_id if req and req.from_week_id else None) or _get_current_iso_week_id()
    target_week = (req.target_week_id if req and req.target_week_id else None) or _get_next_iso_week_id(from_week)

    incomplete_tasks = db.query(WorkflowTask).filter(
        WorkflowTask.week_id == from_week,
        WorkflowTask.status != "completed"
    ).order_by(WorkflowTask.order_index.asc(), WorkflowTask.id.asc()).all()

    moved_tasks = []
    for t in incomplete_tasks:
        t.week_id = target_week
        t.day = "monday"
        t.task_date = _derive_task_date(target_week, "monday")
        t.month_id = _derive_month_id(target_week)
        moved_tasks.append(t)

    db.commit()
    for t in moved_tasks:
        db.refresh(t)

    return WorkflowRolloverResponse(
        ok=True,
        from_week_id=from_week,
        target_week_id=target_week,
        moved_count=len(moved_tasks),
        tasks=moved_tasks
    )


@router.patch("/workflow/tasks/{task_id}/move-to-next-monday", response_model=WorkflowTaskSchema)
def move_task_to_next_monday(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Mueve una tarea de diseño específica directamente al Lunes de la próxima semana."""
    task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    target_week = _get_next_iso_week_id(task.week_id)
    task.week_id = target_week
    task.day = "monday"
    task.task_date = _derive_task_date(target_week, "monday")
    task.month_id = _derive_month_id(target_week)

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
        if t.status in ("review", "completed") and t.actual_hours is not None:
            b_hours = float(t.actual_hours)
        else:
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


# --- Endpoints de Gestión de Clientes, Fechas de Corte y Cobros ---

@router.get("/clients/directory", response_model=List[AgencyClientSchema])
def get_clients_directory(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Retorna el listado completo de clientes registrados con sus fechas de corte y montos."""
    try:
        query = db.query(AgencyClient)
        if status and status != "all":
            query = query.filter(AgencyClient.status == status)
        return query.order_by(AgencyClient.name.asc()).all()
    except Exception as e:
        print(f"Error querying clients directory: {e}")
        # En caso de columna faltante en base de datos externa, forzar inicialización y reintentar
        try:
            from app.core.database import ensure_db_initialized
            db.rollback()
            ensure_db_initialized()
            query = db.query(AgencyClient)
            if status and status != "all":
                query = query.filter(AgencyClient.status == status)
            return query.order_by(AgencyClient.name.asc()).all()
        except Exception as e2:
            print(f"Error fatal consultando clientes: {e2}")
            raise HTTPException(status_code=500, detail=f"Error al consultar clientes: {str(e2)}")


@router.post("/clients/directory", response_model=AgencyClientSchema)
def create_agency_client(
    client_in: AgencyClientCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Da de alta un nuevo cliente de la agencia."""
    existing = db.query(AgencyClient).filter(AgencyClient.name.ilike(client_in.name.strip())).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un cliente registrado con el nombre '{client_in.name}'."
        )

    try:
        db_client = AgencyClient(
            name=client_in.name.strip(),
            contact_name=client_in.contact_name,
            contact_email=client_in.contact_email,
            contact_phone=client_in.contact_phone,
            service_type=client_in.service_type or "design_subscription",
            billing_period=client_in.billing_period or "monthly",
            billing_day=client_in.billing_day or 1,
            monthly_fee=float(client_in.monthly_fee or 0.0),
            requires_invoice=bool(client_in.requires_invoice),
            apply_tax_retention=bool(client_in.apply_tax_retention),
            tax_retention_rate=float(client_in.tax_retention_rate if client_in.tax_retention_rate is not None else 1.25),
            start_date=client_in.start_date,
            status=client_in.status or "active",
            website_url=client_in.website_url,
            ga4_property_id=client_in.ga4_property_id,
            notes=client_in.notes
        )
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    except Exception as e:
        db.rollback()
        print(f"Error creando cliente: {e}")
        # Reintentar asegurando migración si fue error de esquema
        try:
            from app.core.database import ensure_db_initialized
            ensure_db_initialized()
            db_client = AgencyClient(
                name=client_in.name.strip(),
                contact_name=client_in.contact_name,
                contact_email=client_in.contact_email,
                contact_phone=client_in.contact_phone,
                service_type=client_in.service_type or "design_subscription",
                billing_period=client_in.billing_period or "monthly",
                billing_day=client_in.billing_day or 1,
                monthly_fee=float(client_in.monthly_fee or 0.0),
                requires_invoice=bool(client_in.requires_invoice),
                apply_tax_retention=bool(client_in.apply_tax_retention),
                tax_retention_rate=float(client_in.tax_retention_rate if client_in.tax_retention_rate is not None else 1.25),
                start_date=client_in.start_date,
                status=client_in.status or "active",
                website_url=client_in.website_url,
                ga4_property_id=client_in.ga4_property_id,
                notes=client_in.notes
            )
            db.add(db_client)
            db.commit()
            db.refresh(db_client)
            return db_client
        except Exception as e2:
            db.rollback()
            print(f"Error fatal guardando cliente: {e2}")
            raise HTTPException(status_code=500, detail=f"Error al guardar cliente: {str(e2)}")


@router.put("/clients/directory/{client_id}", response_model=AgencyClientSchema)
def update_agency_client(
    client_id: int,
    client_in: AgencyClientUpdate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Actualiza la información, fecha de corte o cuota mensual de un cliente."""
    client = db.query(AgencyClient).filter(AgencyClient.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    try:
        update_data = client_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "name" and value:
                value = value.strip()
            setattr(client, field, value)

        db.commit()
        db.refresh(client)
        return client
    except Exception as e:
        db.rollback()
        print(f"Error actualizando cliente: {e}")
        try:
            from app.core.database import ensure_db_initialized
            ensure_db_initialized()
            update_data = client_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if field == "name" and value:
                    value = value.strip()
                setattr(client, field, value)
            db.commit()
            db.refresh(client)
            return client
        except Exception as e2:
            db.rollback()
            print(f"Error fatal actualizando cliente: {e2}")
            raise HTTPException(status_code=500, detail=f"Error al actualizar cliente: {str(e2)}")


@router.delete("/clients/directory/{client_id}")
def delete_agency_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Elimina o da de baja un cliente."""
    client = db.query(AgencyClient).filter(AgencyClient.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(client)
    db.commit()
    return {"success": True, "detail": f"Cliente '{client.name}' eliminado con éxito"}


@router.post("/clients/send-email")
async def send_email_to_client(
    email_req: SendAgencyEmailRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Envía un correo directamente desde hola@hipha.mx hacia el cliente con diseño institucional y registra el histórico."""
    if not email_req.to_email or "@" not in email_req.to_email:
        raise HTTPException(status_code=400, detail="Dirección de correo electrónico inválida")
    if not email_req.subject.strip():
        raise HTTPException(status_code=400, detail="El asunto del correo no puede estar vacío")
    msg_content = (email_req.message or email_req.message_body or "").strip()
    if not msg_content:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

    # Resolver cliente vinculado si no se especificó ID explícito
    client_id = email_req.client_id
    client_name = (email_req.client_name or "").strip()
    if not client_id:
        matched_client = None
        if client_name:
            matched_client = db.query(AgencyClient).filter(AgencyClient.name.ilike(client_name)).first()
        if not matched_client and email_req.to_email:
            matched_client = db.query(AgencyClient).filter(AgencyClient.contact_email.ilike(email_req.to_email.strip())).first()
        if matched_client:
            client_id = matched_client.id
            if not client_name:
                client_name = matched_client.name

    has_att = bool(email_req.attachments and len(email_req.attachments) > 0)
    att_names = ", ".join([a.filename for a in email_req.attachments if a.filename]) if has_att else None

    # Registrar en bitácora de correos
    sender_user = getattr(current_user, "email", "admin@hipha.mx")
    log_entry = SentEmailLog(
        client_id=client_id,
        client_name=client_name or None,
        to_email=email_req.to_email.strip(),
        subject=email_req.subject.strip(),
        message_body=msg_content,
        sender_email="hola@hipha.mx",
        sent_by_user=sender_user,
        has_attachments=has_att,
        attachment_names=att_names,
        status="sent"
    )
    db.add(log_entry)

    try:
        success = await send_custom_agency_email(
            to_email=email_req.to_email.strip(),
            subject=email_req.subject.strip(),
            message_body=msg_content,
            client_name=email_req.client_name or "",
            attachments=email_req.attachments
        )
        if success:
            log_entry.status = "sent"
            db.commit()
            db.refresh(log_entry)
            return {
                "success": True,
                "detail": f"Correo enviado exitosamente a {email_req.to_email}",
                "log_id": log_entry.id
            }
        else:
            log_entry.status = "failed"
            log_entry.error_message = "No se pudo entregar el correo"
            db.commit()
            raise HTTPException(status_code=500, detail="No se pudo entregar el correo electrónico")
    except Exception as e:
        log_entry.status = "failed"
        log_entry.error_message = str(e)
        db.commit()
        print(f"Error enviando correo institucional: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el servidor de correo: {str(e)}")


@router.get("/clients/email-history", response_model=List[SentEmailLogResponse])
def get_email_history(
    client_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Consulta el historial de correos enviados desde el dashboard con soporte para búsqueda y filtrado por cliente."""
    query = db.query(SentEmailLog)
    if client_id is not None:
        query = query.filter(SentEmailLog.client_id == client_id)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (SentEmailLog.client_name.ilike(term)) |
            (SentEmailLog.to_email.ilike(term)) |
            (SentEmailLog.subject.ilike(term)) |
            (SentEmailLog.message_body.ilike(term)) |
            (SentEmailLog.attachment_names.ilike(term))
        )
    return query.order_by(SentEmailLog.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/clients/email-history/{log_id}", response_model=SentEmailLogResponse)
def get_email_history_detail(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Consulta el detalle y cuerpo completo de un correo enviado registrado en el historial."""
    log_entry = db.query(SentEmailLog).filter(SentEmailLog.id == log_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Registro de correo no encontrado")
    return log_entry
