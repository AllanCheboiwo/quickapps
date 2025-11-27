from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated

from src.utils import db
from src.models import skills as skill_model

from src.schemas import skills as skill_schema
from src.routes.auth import get_current_user
from src.models.users import User
from src.utils.auth_helpers import verify_profile_ownership #, get_user_profile_ids_subquery # get_user_profile_ids_subquery may not be needed for these routes

DbSession = Annotated[Session, Depends(db.get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    # prefix="/skills", # Prefix is now handled in main.py
    tags=["Profile Skills"], # Tags can be set here or in main.py
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=skill_schema.SkillOut, status_code=status.HTTP_201_CREATED)
async def create_skill_for_profile(
    profile_id: int, # Comes from path e.g. /profiles/{profile_id}/skills
    skill_in: skill_schema.SkillCreateRequest, 
    db_session: DbSession,
    current_user: CurrentUser
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    skill_data = skill_in.dict()
    skill_data["profile_id"] = profile_id # Add profile_id from path
    db_skill = skill_model.Skill(**skill_data)
    db_session.add(db_skill)
    db_session.commit()
    db_session.refresh(db_skill)
    return db_skill

@router.get("", response_model=List[skill_schema.SkillOut])
async def read_skills_for_profile(
    profile_id: int, # Comes from path
    db_session: DbSession,
    current_user: CurrentUser,
    skip: int = 0, 
    limit: int = 100
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    skills = db_session.query(skill_model.Skill).filter(
        skill_model.Skill.profile_id == profile_id
    ).offset(skip).limit(limit).all()
    return skills

@router.get("/{skill_id}", response_model=skill_schema.SkillOut)
async def read_skill_for_profile(
    profile_id: int, # Comes from path
    skill_id: int,
    db_session: DbSession,
    current_user: CurrentUser
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_skill = db_session.query(skill_model.Skill).filter(
        skill_model.Skill.id == skill_id,
        skill_model.Skill.profile_id == profile_id # Ensure skill belongs to the profile in path
    ).first()
    if db_skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found or not part of this profile")
    return db_skill

@router.put("/{skill_id}", response_model=skill_schema.SkillOut)
async def update_skill_for_profile(
    profile_id: int, # Comes from path
    skill_id: int, 
    skill_update: skill_schema.SkillUpdate, 
    db_session: DbSession,
    current_user: CurrentUser
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_skill = db_session.query(skill_model.Skill).filter(
        skill_model.Skill.id == skill_id,
        skill_model.Skill.profile_id == profile_id # Ensure skill belongs to the profile in path
    ).first()

    if db_skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found or not part of this profile")
    
    update_data = skill_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_skill, field, value)
    
    db_session.commit()
    db_session.refresh(db_skill)
    return db_skill

@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill_for_profile(
    profile_id: int, # Comes from path
    skill_id: int, 
    db_session: DbSession,
    current_user: CurrentUser
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_skill = db_session.query(skill_model.Skill).filter(
        skill_model.Skill.id == skill_id,
        skill_model.Skill.profile_id == profile_id # Ensure skill belongs to the profile in path
    ).first()

    if db_skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found or not part of this profile")
    
    db_session.delete(db_skill)
    db_session.commit()
    return None

@router.post("/bulk", response_model=List[skill_schema.SkillOut], status_code=status.HTTP_201_CREATED)
async def create_bulk_skills_for_profile(
    profile_id: int, # Comes from path
    skills_in: List[skill_schema.SkillCreateRequest], 
    db_session: DbSession,
    current_user: CurrentUser
):

    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_skills = []
    for skill_data_in in skills_in:
        skill_data = skill_data_in.dict()
        skill_data["profile_id"] = profile_id # Add profile_id from path
        db_skills.append(skill_model.Skill(**skill_data))
        
    db_session.add_all(db_skills)
    db_session.commit()
    for skill in db_skills:
        db_session.refresh(skill) # Refresh each object to get its ID and other db-generated fields
    return db_skills 