from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated

from src.utils import db
from src.models import experience as experience_model
# from src.models import profiles as profile_model # Not directly needed
from src.schemas import experience as experience_schema
from src.routes.auth import get_current_user
from src.models.users import User
from src.utils.auth_helpers import verify_profile_ownership#, get_user_profile_ids_subquery # get_user_profile_ids_subquery likely not needed here

# Reusable dependency annotations
DbSession = Annotated[Session, Depends(db.get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    # prefix="/experience", # Prefix is now handled in main.py
    tags=["Profile Experience"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=experience_schema.ExperienceOut, status_code=status.HTTP_201_CREATED)
async def create_experience_for_profile(
    profile_id: int, # Comes from path e.g. /profiles/{profile_id}/experience
    experience_in: experience_schema.ExperienceCreateRequest,
    db_session: DbSession,
    current_user: CurrentUser
):
    """Create a new experience entry for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    experience_data = experience_in.dict()
    experience_data["profile_id"] = profile_id # Add profile_id from path
    db_experience = experience_model.Experience(**experience_data)
    db_session.add(db_experience)
    db_session.commit()
    db_session.refresh(db_experience)
    return db_experience

@router.get("", response_model=List[experience_schema.ExperienceOut])
async def read_experiences_for_profile(
    profile_id: int, # Comes from path
    db_session: DbSession,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
):
    """Get all experience entries for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    experiences = db_session.query(experience_model.Experience).filter(
        experience_model.Experience.profile_id == profile_id
    ).offset(skip).limit(limit).all()
    return experiences

@router.get("/{experience_id}", response_model=experience_schema.ExperienceOut)
async def read_experience_for_profile(
    profile_id: int, # Comes from path
    experience_id: int,
    db_session: DbSession,
    current_user: CurrentUser
):
    """Get a specific experience by ID, for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_experience = db_session.query(experience_model.Experience).filter(
        experience_model.Experience.id == experience_id,
        experience_model.Experience.profile_id == profile_id # Ensure experience belongs to the profile in path
    ).first()
    if db_experience is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found or not part of this profile")
    return db_experience

@router.put("/{experience_id}", response_model=experience_schema.ExperienceOut)
async def update_experience_for_profile(
    profile_id: int, # Comes from path
    experience_id: int,
    experience_update: experience_schema.ExperienceUpdate,
    db_session: DbSession,
    current_user: CurrentUser
):
    """Update an experience for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_experience = db_session.query(experience_model.Experience).filter(
        experience_model.Experience.id == experience_id,
        experience_model.Experience.profile_id == profile_id # Ensure experience belongs to the profile in path
    ).first()

    if db_experience is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found or not part of this profile")
    
    update_data = experience_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_experience, field, value)
    
    db_session.commit()
    db_session.refresh(db_experience)
    return db_experience

@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience_for_profile(
    profile_id: int, # Comes from path
    experience_id: int,
    db_session: DbSession,
    current_user: CurrentUser
):
    """Delete an experience for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_experience = db_session.query(experience_model.Experience).filter(
        experience_model.Experience.id == experience_id,
        experience_model.Experience.profile_id == profile_id # Ensure experience belongs to the profile in path
    ).first()

    if db_experience is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found or not part of this profile")
    
    db_session.delete(db_experience)
    db_session.commit()
    return None

@router.post("/bulk", response_model=List[experience_schema.ExperienceOut], status_code=status.HTTP_201_CREATED)
async def create_bulk_experiences_for_profile(
    profile_id: int, # Comes from path
    experiences_in: List[experience_schema.ExperienceCreateRequest],
    db_session: DbSession,
    current_user: CurrentUser
):
    """Create multiple experiences at once for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_experiences = []
    for exp_in in experiences_in:
        exp_data = exp_in.dict()
        exp_data["profile_id"] = profile_id # Add profile_id from path
        db_experiences.append(experience_model.Experience(**exp_data))
        
    db_session.add_all(db_experiences)
    db_session.commit()
    for exp in db_experiences:
        db_session.refresh(exp) # Refresh each object
    return db_experiences 