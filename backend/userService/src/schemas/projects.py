from pydantic import BaseModel
from datetime import date
from typing import Optional

# Schema for request body when creating a project
class ProjectCreate(BaseModel):
    profile_id: int
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[str] = None

# Schema for request body when creating a project for a profile_id from path
class ProjectCreateRequest(BaseModel):
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[str] = None

# Schema for request body when updating a project
class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[str] = None

# Schema for response body when returning a project
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