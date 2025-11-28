from datetime import timedelta, datetime
from typing import Annotated, Optional
import uuid

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.utils.db import get_db
from src.models.users import User
from src.utils.security import verify_password, get_password_hash, create_access_token
from src.utils.guest_limiter import GuestLimiter
from src.core.config import settings

DbSession = Annotated[Session, Depends(get_db)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None


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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


def get_user(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    return user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashedPassword):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: DbSession):
    db_user_by_email = db.query(User).filter(User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    db_user_by_username = db.query(User).filter(User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashedPassword=hashed_password,
        firstName=user.firstName,
        lastName=user.lastName
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2Form,
    db_session: DbSession
) -> Token:
    user = authenticate_user(db_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/guest-login")
async def guest_login(db: DbSession) -> Token:
    """
    Create a temporary guest account with 7-day expiry.
    No authentication required - perfect for trying the app!
    
    Returns a JWT token for immediate access.
    Guest users can create 1 profile and generate 1 resume per day.
    """
    # Generate unique guest username
    guest_username = f"guest_{uuid.uuid4().hex[:8]}"
    guest_email = f"{guest_username}@guest.quickapps.local"
    
    # Create guest user
    guest_user = User(
        username=guest_username,
        email=guest_email,
        hashedPassword=get_password_hash("guest"),  # Dummy password
        firstName="Guest",
        lastName="User",
        is_guest=True,
        guest_expires_at=datetime.utcnow() + timedelta(days=GuestLimiter.GUEST_EXPIRY_DAYS)
    )
    
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": guest_user.username},
        expires_delta=timedelta(days=GuestLimiter.GUEST_EXPIRY_DAYS)
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user
