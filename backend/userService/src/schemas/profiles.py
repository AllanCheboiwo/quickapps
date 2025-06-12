from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

# Schema for request body when creating a profile
class ProfileCreate(BaseModel):
    name: str

# Schema for request body when updating a profile
class ProfileUpdate(BaseModel):
    name: Optional[str] = None

# Base schema for profile without relationships
class ProfileBase(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema for response body when returning a profile (without nested relationships)
class ProfileOut(ProfileBase):
    pass

# Forward declarations for nested schemas
class SkillOut(BaseModel):
    id: int
    name: str
    proficiency: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProjectOut(BaseModel):
    id: int
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[str] = None
    
    class Config:
        from_attributes = True

class ExperienceOut(BaseModel):
    id: int
    company: str
    position: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class EducationOut(BaseModel):
    id: int
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

# Schema for response body with all nested relationships
class ProfileDetailOut(ProfileBase):
    skills: List[SkillOut] = []
    projects: List[ProjectOut] = []
    experience: List[ExperienceOut] = []
    education: List[EducationOut] = [] 