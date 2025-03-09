from typing import Optional

from pydantic import BaseModel, Field

class TaskEstimateBase(BaseModel):
    task_id: int = Field(..., title='Task ID')
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=2000)

class TaskEstimateRequest(TaskEstimateBase):
    pass

class TaskEstimateResponse(TaskEstimateBase):
    estimated_time: float