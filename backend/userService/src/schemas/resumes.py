from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ResumeGenerateRequest(BaseModel):
    """Request schema for generating a resume"""
    profile_id: int
    job_description: str

class ResumeResponse(BaseModel):
    """Response schema for resume data"""
    id: int
    user_id: int
    profile_id: int
    job_description: str
    latex_content: str
    pdf_file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResumeListResponse(BaseModel):
    """Response schema for listing resumes"""
    id: int
    profile_id: int
    job_description: str
    created_at: datetime
    # Exclude large latex_content from list view

    class Config:
        from_attributes = True 