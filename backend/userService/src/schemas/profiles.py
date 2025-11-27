from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


class ProfileCreate(BaseModel):
    name: str


class ProfileUpdate(BaseModel):
    name: Optional[str] = None

class ProfileBase(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileOut(ProfileBase):
    pass


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


class ProfileDetailOut(ProfileBase):
    skills: List[SkillOut] = []
    projects: List[ProjectOut] = []
    experience: List[ExperienceOut] = []
    education: List[EducationOut] = [] 