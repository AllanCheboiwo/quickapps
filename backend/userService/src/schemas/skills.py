from pydantic import BaseModel
from typing import Optional

# Schema for request body when creating a skill (original, when profile_id is in body)
class SkillCreate(BaseModel):
    profile_id: int
    name: str
    proficiency: Optional[str] = None

# Schema for request body when creating a skill for a profile_id from path
class SkillCreateRequest(BaseModel):
    name: str
    proficiency: Optional[str] = None

# Schema for request body when updating a skill
class SkillUpdate(BaseModel):
    name: Optional[str] = None
    proficiency: Optional[str] = None

# Schema for response body when returning a skill
class SkillOut(BaseModel):
    id: int
    profile_id: int
    name: str
    proficiency: Optional[str] = None

    class Config:
        from_attributes = True 