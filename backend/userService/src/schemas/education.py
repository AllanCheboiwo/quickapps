from pydantic import BaseModel
from datetime import date
from typing import Optional

# Schema for request body when creating an education
class EducationCreate(BaseModel):
    profile_id: int
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

# Schema for request body when creating education for a profile_id from path
class EducationCreateRequest(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

# Schema for request body when updating an education
class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

# Schema for response body when returning an education
class EducationOut(BaseModel):
    id: int
    profile_id: int
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True 