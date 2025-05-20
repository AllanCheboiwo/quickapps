from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.utils import db # Database utilities (get_db)
from src.models import users as user_model # SQLAlchemy model
from src.schemas import users as user_schema # Pydantic schemas

# You'll need a proper password hashing utility
# For now, a placeholder. Replace with e.g. passlib.context.CryptContext
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    # return pwd_context.hash(password)
    return password + "_very_hashed" # Replace this placeholder!

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=user_schema.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: user_schema.UserCreate, db_session: Session = Depends(db.get_db)):
    db_user_by_email = db_session.query(user_model.User).filter(user_model.User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db_user_by_username = db_session.query(user_model.User).filter(user_model.User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    # Note: Your User model uses Mapped, so attribute names match your model definition
    new_user = user_model.User(
        username=user.username,
        email=user.email,
        hashedPassword=hashed_password, # Matches your model's hashedPassword field
        firstName=user.firstName,
        lastName=user.lastName
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return new_user

@router.get("/", response_model=List[user_schema.UserOut])
def read_users(skip: int = 0, limit: int = 100, db_session: Session = Depends(db.get_db)):
    users = db_session.query(user_model.User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=user_schema.UserOut)
def read_user(user_id: int, db_session: Session = Depends(db.get_db)):
    db_user = db_session.query(user_model.User).filter(user_model.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user
