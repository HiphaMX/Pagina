from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class WorkflowTaskBase(BaseModel):
    week_id: str  # e.g. "2026-W40"
    day: str  # "backlog", "monday", "tuesday", "wednesday", "thursday", "friday"
    client_name: str
    title: str
    estimated_hours: float = 1.0
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
