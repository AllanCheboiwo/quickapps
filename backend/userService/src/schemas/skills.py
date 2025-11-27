from pydantic import BaseModel
from typing import Optional

class SkillCreate(BaseModel):
    profile_id: int
    name: str
    proficiency: Optional[str] = None

class SkillCreateRequest(BaseModel):
    name: str
    proficiency: Optional[str] = None


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    proficiency: Optional[str] = None


class SkillOut(BaseModel):
    id: int
    profile_id: int
    name: str
    proficiency: Optional[str] = None

    class Config:
        from_attributes = True 