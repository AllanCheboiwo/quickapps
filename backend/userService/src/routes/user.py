from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.utils import db # Database utilities (get_db)
from src.models import users as user_model # SQLAlchemy model
from src.schemas import users as user_schema # Pydantic schemas

router = APIRouter(
    prefix="/users",
    tags=["User Management"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[user_schema.UserOut])
def read_users(skip: int = 0, limit: int = 100, db_session: Session = Depends(db.get_db)):
    """Get all users (admin endpoint)"""
    users = db_session.query(user_model.User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=user_schema.UserOut)
def read_user(user_id: int, db_session: Session = Depends(db.get_db)):
    """Get user by ID (admin endpoint)"""
    db_user = db_session.query(user_model.User).filter(user_model.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user
