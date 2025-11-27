from pydantic import BaseModel
from datetime import date
from typing import Optional


class ProjectCreate(BaseModel):
    profile_id: int
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[str] = None


class ProjectCreateRequest(BaseModel):
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    profile_id: int
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[str] = None

    class Config:
        from_attributes = True 