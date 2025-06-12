from pydantic import BaseModel
from datetime import date
from typing import Optional

# Schema for request body when creating an experience
class ExperienceCreate(BaseModel):
    profile_id: int
    company: str
    position: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

# Schema for request body when creating an experience for a profile_id from path
class ExperienceCreateRequest(BaseModel):
    company: str
    position: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

# Schema for request body when updating an experience
class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

# Schema for response body when returning an experience
class ExperienceOut(BaseModel):
    id: int
    profile_id: int
    company: str
    position: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True 