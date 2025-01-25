from typing import Optional

from datetime import datetime

from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=255)
    assigned_user: Optional[str] = Field(None, min_length=1, max_length=255)
    priority: Optional[str] = Field(None, min_length=1, max_length=7)

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(TaskBase):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, min_length=1, max_length=50)
    estimated_time: float = 0.0
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    project_id: Optional[int]


class TaskRead(TaskBase):
    id: int
    status: str
    estimated_time: float
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True