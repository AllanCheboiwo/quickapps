from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Schema for request body when creating a user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str # Client sends plain password
    firstName: Optional[str] = None
    lastName: Optional[str] = None

# Schema for request body when updating a user (example, can be more specific)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    is_active: Optional[bool] = None

# Schema for response body when returning a user (omitting password)
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # If you have an is_active field in your model and want to return it:
    # is_active: bool 

    class Config:
        from_attributes = True # For Pydantic V2 (replaces orm_mode = True)
