from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Annotated

from src.utils import db
from src.models import profiles as profile_model
from src.schemas import profiles as profile_schema
from src.routes.auth import get_current_user
from src.models.users import User

DbSession = Annotated[Session, Depends(db.get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    prefix="/profiles",
    tags=["Profile Management"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=profile_schema.ProfileOut, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile: profile_schema.ProfileCreate,
    db_session: DbSession,
    current_user: CurrentUser
):
    profile_data = profile.dict()
    profile_data["user_id"] = current_user.id
    db_profile = profile_model.Profile(**profile_data)
    db_session.add(db_profile)
    db_session.commit()
    db_session.refresh(db_profile)
    return db_profile

@router.get("", response_model=List[profile_schema.ProfileOut])
def read_profiles(
    db_session: DbSession,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
):
    profiles = db_session.query(profile_model.Profile).filter(
        profile_model.Profile.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return profiles

@router.get("/{profile_id}", response_model=profile_schema.ProfileOut)
def read_profile(
    profile_id: int,
    db_session: DbSession,
    current_user: CurrentUser
):
    db_profile = db_session.query(profile_model.Profile).filter(
        profile_model.Profile.id == profile_id,
        profile_model.Profile.user_id == current_user.id
    ).first()
    if db_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return db_profile

@router.get("/{profile_id}/details", response_model=profile_schema.ProfileDetailOut)
def read_profile_with_details(
    profile_id: int,
    db_session: DbSession,
    current_user: CurrentUser
):
    db_profile = db_session.query(profile_model.Profile).options(
        joinedload(profile_model.Profile.skills),
        joinedload(profile_model.Profile.experience),
        joinedload(profile_model.Profile.education),
        joinedload(profile_model.Profile.projects)
    ).filter(
        profile_model.Profile.id == profile_id,
        profile_model.Profile.user_id == current_user.id
    ).first()

    if db_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return db_profile

@router.get("/user/{user_id}", response_model=List[profile_schema.ProfileOut])
def read_profiles_by_user(user_id: int, db_session: Session = Depends(db.get_db)):
    profiles = db_session.query(profile_model.Profile).filter(profile_model.Profile.user_id == user_id).all()
    return profiles

@router.put("/{profile_id}", response_model=profile_schema.ProfileOut)
def update_profile(
    profile_id: int,
    profile_update: profile_schema.ProfileUpdate,
    db_session: DbSession,
    current_user: CurrentUser
):
    db_profile = db_session.query(profile_model.Profile).filter(
        profile_model.Profile.id == profile_id,
        profile_model.Profile.user_id == current_user.id
    ).first()
    if db_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)

    db_session.commit()
    db_session.refresh(db_profile)
    return db_profile

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    profile_id: int,
    db_session: DbSession,
    current_user: CurrentUser
):
    db_profile = db_session.query(profile_model.Profile).filter(
        profile_model.Profile.id == profile_id,
        profile_model.Profile.user_id == current_user.id
    ).first()
    if db_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    db_session.delete(db_profile)
    db_session.commit()
    return None 