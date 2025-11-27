from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated

from src.utils import db
from src.models import education as education_model
from src.schemas import education as education_schema
from src.routes.auth import get_current_user
from src.models.users import User
from src.utils.auth_helpers import verify_profile_ownership

DbSession = Annotated[Session, Depends(db.get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    tags=["Profile Education"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=education_schema.EducationOut, status_code=status.HTTP_201_CREATED)
async def create_education_for_profile(
    profile_id: int, 
    education_in: education_schema.EducationCreateRequest, 
    db_session: DbSession,
    current_user: CurrentUser
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    education_data = education_in.dict()
    education_data["profile_id"] = profile_id
    db_education = education_model.Education(**education_data)
    db_session.add(db_education)
    db_session.commit()
    db_session.refresh(db_education)
    return db_education

@router.get("", response_model=List[education_schema.EducationOut])
async def read_educations_for_profile(
    profile_id: int, 
    db_session: DbSession,
    current_user: CurrentUser,
    skip: int = 0, 
    limit: int = 100
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    educations = db_session.query(education_model.Education).filter(
        education_model.Education.profile_id == profile_id
    ).offset(skip).limit(limit).all()
    return educations

@router.get("/{education_id}", response_model=education_schema.EducationOut)
async def read_education_for_profile(
    profile_id: int, 
    education_id: int, 
    db_session: DbSession,
    current_user: CurrentUser
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_education = db_session.query(education_model.Education).filter(
        education_model.Education.id == education_id,
        education_model.Education.profile_id == profile_id
    ).first()
    if db_education is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education record not found or not part of this profile")
    return db_education

@router.put("/{education_id}", response_model=education_schema.EducationOut)
async def update_education_for_profile(
    profile_id: int, 
    education_id: int, 
    education_update: education_schema.EducationUpdate, 
    db_session: DbSession,
    current_user: CurrentUser
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_education = db_session.query(education_model.Education).filter(
        education_model.Education.id == education_id,
        education_model.Education.profile_id == profile_id
    ).first()

    if db_education is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education record not found or not part of this profile")
    
    update_data = education_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_education, field, value)
    
    db_session.commit()
    db_session.refresh(db_education)
    return db_education

@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education_for_profile(
    profile_id: int, 
    education_id: int, 
    db_session: DbSession,
    current_user: CurrentUser
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_education = db_session.query(education_model.Education).filter(
        education_model.Education.id == education_id,
        education_model.Education.profile_id == profile_id
    ).first()

    if db_education is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education record not found or not part of this profile")
    
    db_session.delete(db_education)
    db_session.commit()
    return None

@router.post("/bulk", response_model=List[education_schema.EducationOut], status_code=status.HTTP_201_CREATED)
async def create_bulk_educations_for_profile(
    profile_id: int, 
    educations_in: List[education_schema.EducationCreateRequest], 
    db_session: DbSession,
    current_user: CurrentUser
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_educations = []
    for edu_in in educations_in:
        edu_data = edu_in.dict()
        edu_data["profile_id"] = profile_id
        db_educations.append(education_model.Education(**edu_data))
        
    db_session.add_all(db_educations)
    db_session.commit()
    for edu in db_educations:
        db_session.refresh(edu)
    return db_educations 