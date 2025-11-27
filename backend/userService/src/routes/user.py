from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated

from src.utils import db # Database utilities (get_db)
from src.models import users as user_model # SQLAlchemy model
from src.schemas import users as user_schema # Pydantic schemas
from src.routes.auth import get_current_user
from src.models.users import User

CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    prefix="/users",
    tags=["User Management"],
    responses={404: {"description": "Not found"}},
)

@router.get("/me", response_model=user_schema.UserOut)
def read_current_user(current_user: CurrentUser):

    return current_user
