from sqlalchemy import Column, DateTime, Integer, String, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base

class WorkflowTask(Base):
    __tablename__ = "workflow_tasks"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(String, index=True, nullable=False)  # ej. "2026-W40"
    day = Column(String, nullable=False, default="monday")  # "monday", "tuesday", "wednesday", "thursday", "friday"
    client_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    estimated_hours = Column(Float, default=1.0)
    actual_hours = Column(Float, nullable=True, default=None)
    revision_hours = Column(Float, default=0.0)
    revisions_count = Column(Integer, default=0)
    month_id = Column(String, index=True, nullable=True)  # ej. "2026-09"
    task_date = Column(String(10), index=True, nullable=True)  # ej. "2026-09-29"
    status = Column(String, default="pending")  # "pending", "in_progress", "review", "completed"
    notes = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

