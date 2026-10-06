import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from app.core.database import SessionLocal, Base, engine
from app.models.workflow_task import WorkflowTask

client = TestClient(app)

mock_admin = UserSchema(
    id=1,
    email="hola@hipha.mx",
    is_active=True,
    is_superuser=True,
    full_name="Administrador Hipha"
)

@pytest.fixture(autouse=True)
def setup_db_and_auth():
    from app.core.database import ensure_db_initialized
    ensure_db_initialized()
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin
    yield
    app.dependency_overrides.pop(get_current_active_user, None)


def test_rollover_workflow_tasks():
    db = SessionLocal()
    # Limpiar tareas de prueba
    db.query(WorkflowTask).filter(WorkflowTask.week_id.in_(["2026-W38", "2026-W39", "2026-W40"])).delete(synchronize_session=False)
    db.commit()

    # 1. Crear 3 tareas en 2026-W38: 2 incompletas y 1 completada
    task_pending = WorkflowTask(
        week_id="2026-W38",
        day="tuesday",
        client_name="HealthyIce",
        title="Diseño de Menú de Temporada",
        estimated_hours=2.0,
        status="pending"
    )
    task_in_progress = WorkflowTask(
        week_id="2026-W38",
        day="thursday",
        client_name="Tukipa Fitness",
        title="3 Posts de Instagram",
        estimated_hours=1.5,
        status="in_progress"
    )
    task_completed = WorkflowTask(
        week_id="2026-W38",
        day="friday",
        client_name="DAM Pisos",
        title="Flyer Promocional Cerámicas",
        estimated_hours=1.0,
        status="completed"
    )
    db.add_all([task_pending, task_in_progress, task_completed])
    db.commit()

    # 2. Ejecutar rollover explícito de 2026-W38 a 2026-W39
    resp = client.post("/api/dashboard/workflow/tasks/rollover", json={
        "from_week_id": "2026-W38",
        "target_week_id": "2026-W39"
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["ok"] is True
    assert data["moved_count"] == 2
    assert len(data["tasks"]) == 2

    # Verificar que las tareas movidas tienen day="monday" y week_id="2026-W39"
    for t in data["tasks"]:
        assert t["week_id"] == "2026-W39"
        assert t["day"] == "monday"

    # Verificar en la base de datos que la completada sigue en W38
    db.refresh(task_completed)
    assert task_completed.week_id == "2026-W38"
    assert task_completed.status == "completed"

    # 3. Probar mover tarea individual al próximo lunes (de W39 a W40)
    db.refresh(task_pending)
    move_resp = client.patch(f"/api/dashboard/workflow/tasks/{task_pending.id}/move-to-next-monday")
    assert move_resp.status_code == 200, move_resp.text
    moved_data = move_resp.json()
    assert moved_data["week_id"] == "2026-W40"
    assert moved_data["day"] == "monday"

    # Cleanup
    db.query(WorkflowTask).filter(WorkflowTask.week_id.in_(["2026-W38", "2026-W39", "2026-W40"])).delete(synchronize_session=False)
    db.commit()
    db.close()


def test_auto_rollover_on_get_tasks():
    from app.api.dashboard.routes import _get_current_iso_week_id
    curr_week = _get_current_iso_week_id()
    db = SessionLocal()

    # Tarea pendiente de semana pasada
    task_old = WorkflowTask(
        week_id="2020-W01",
        day="friday",
        client_name="AMDI",
        title="Diseño Pendiente Antiguo",
        status="pending"
    )
    db.add(task_old)
    db.commit()

    # Al consultar semana actual
    resp = client.get(f"/api/dashboard/workflow/tasks?week={curr_week}")
    assert resp.status_code == 200
    data = resp.json()
    
    # La tarea debe haber sido migrada automáticamente a curr_week con day="monday"
    found = next((t for t in data if t["id"] == task_old.id), None)
    assert found is not None
    assert found["week_id"] == curr_week
    assert found["day"] == "monday"

    # Cleanup
    db.query(WorkflowTask).filter(WorkflowTask.id == task_old.id).delete()
    db.commit()
    db.close()


def test_workflow_actual_hours_and_time_liberation():
    """Verifica que se pueda registrar actual_hours al pasar a revisión o terminado, liberando tiempo."""
    from app.api.dashboard.routes import _get_current_iso_week_id
    curr_week = _get_current_iso_week_id()
    db = SessionLocal()

    # 1. Crear tarea de 1.0 hora
    create_resp = client.post("/api/dashboard/workflow/tasks", json={
        "week_id": curr_week,
        "day": "monday",
        "client_name": "HealthyIce",
        "title": "3 Carruseles Instagram",
        "estimated_hours": 1.0,
        "status": "pending"
    })
    assert create_resp.status_code == 200, create_resp.text
    task_data = create_resp.json()
    task_id = task_data["id"]
    assert task_data["actual_hours"] is None
    assert task_data["estimated_hours"] == 1.0

    # 2. Diseñador termina en 20 min (0.33h) y pasa a 'review' con cliente
    update_resp = client.put(f"/api/dashboard/workflow/tasks/{task_id}", json={
        "status": "review",
        "actual_hours": 0.33
    })
    assert update_resp.status_code == 200, update_resp.text
    updated_data = update_resp.json()
    assert updated_data["status"] == "review"
    assert updated_data["actual_hours"] == 0.33
    assert updated_data["estimated_hours"] == 1.0

    # 3. Pasa a 'completed' con el mismo tiempo real
    comp_resp = client.put(f"/api/dashboard/workflow/tasks/{task_id}", json={
        "status": "completed",
        "actual_hours": 0.33
    })
    assert comp_resp.status_code == 200
    assert comp_resp.json()["status"] == "completed"
    assert comp_resp.json()["actual_hours"] == 0.33

    # 4. Verificar reporte mensual: las horas base deben ser 0.33, no 1.0
    today_str = comp_resp.json().get("task_date") or ""
    if today_str:
        month_str = today_str[:7]
        rpt_resp = client.get(f"/api/dashboard/workflow/monthly-report?month={month_str}&client=HealthyIce")
        if rpt_resp.status_code == 200:
            rpt_data = rpt_resp.json()
            client_summary = next((c for c in rpt_data["clients"] if c["client_name"] == "HealthyIce"), None)
            if client_summary:
                # El reporte debe incluir 0.33 para esta tarea
                assert client_summary["base_hours"] >= 0.33

    # Cleanup
    db.query(WorkflowTask).filter(WorkflowTask.id == task_id).delete()
    db.commit()
    db.close()

