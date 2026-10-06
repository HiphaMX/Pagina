from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class WorkflowTaskBase(BaseModel):
    week_id: str  # e.g. "2026-W40"
    day: str  # "monday", "tuesday", "wednesday", "thursday", "friday"
    client_name: str
    title: str
    estimated_hours: float = 1.0
    actual_hours: Optional[float] = None
    revision_hours: float = 0.0
    revisions_count: int = 0
    month_id: Optional[str] = None  # e.g. "2026-09"
    task_date: Optional[str] = None  # e.g. "2026-09-29"
    status: str = "pending"  # "pending", "in_progress", "review", "completed"
    notes: Optional[str] = None
    order_index: int = 0


class WorkflowTaskCreate(WorkflowTaskBase):
    pass


class WorkflowTaskUpdate(BaseModel):
    week_id: Optional[str] = None
    day: Optional[str] = None
    client_name: Optional[str] = None
    title: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    revision_hours: Optional[float] = None
    revisions_count: Optional[int] = None
    month_id: Optional[str] = None
    task_date: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    order_index: Optional[int] = None


class WorkflowTask(WorkflowTaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WorkflowMoveRequest(BaseModel):
    task_id: int
    target_day: str
    target_order_index: Optional[int] = 0


class WorkflowAddRevisionRequest(BaseModel):
    delta_hours: float = 0.5
    note: Optional[str] = None


class WorkflowMonthlyClientSummary(BaseModel):
    client_name: str
    total_hours: float
    base_hours: float
    revision_hours: float
    tasks_count: int
    completed_count: int


class WorkflowMonthlyReport(BaseModel):
    month: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_hours: float
    base_hours: float
    revision_hours: float
    total_tasks: int
    completed_tasks: int
    clients: List[WorkflowMonthlyClientSummary]
    tasks: List[WorkflowTask]


class WorkflowRolloverRequest(BaseModel):
    from_week_id: Optional[str] = None
    target_week_id: Optional[str] = None


class WorkflowRolloverResponse(BaseModel):
    ok: bool
    from_week_id: str
    target_week_id: str
    moved_count: int
    tasks: List[WorkflowTask]

