from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str 
    firstName: Optional[str] = None
    lastName: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    created_at: datetime
    updated_at: datetime


    class Config:
        from_attributes = True 
