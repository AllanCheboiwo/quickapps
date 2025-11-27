from pydantic import BaseModel
from datetime import date
from typing import Optional


class ExperienceCreate(BaseModel):
    profile_id: int
    company: str
    position: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class ExperienceCreateRequest(BaseModel):
    company: str
    position: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

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