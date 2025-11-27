from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from src.utils.db import get_db
from src.routes.auth import get_current_user
from src.models.users import User

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
