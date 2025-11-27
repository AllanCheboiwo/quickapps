from pydantic import BaseModel
from datetime import datetime


class ResumeGenerateRequest(BaseModel):
    profile_id: int
    job_description: str


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    profile_id: int
    job_description: str
    latex_content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    id: int
    profile_id: int
    job_description: str
    created_at: datetime

    class Config:
        from_attributes = True