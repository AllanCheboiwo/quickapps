from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.models.profiles import Profile
from src.models.users import User
from src.models.generated_resumes import GeneratedResume

def verify_profile_ownership(profile_id: int, current_user: User, db_session: Session):
    """Helper function to verify that a profile belongs to the current user"""
    profile = db_session.query(Profile).filter(
        Profile.id == profile_id,
        Profile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Profile not found or access denied"
        )
    return profile

def verify_resume_ownership(resume_id: int, current_user: User, db_session: Session):
    """Helper function to verify that a resume belongs to the current user"""
    resume = db_session.query(GeneratedResume).filter(
        GeneratedResume.id == resume_id,
        GeneratedResume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Resume not found or access denied"
        )
    return resume

def get_user_profile_ids_subquery(current_user: User, db_session: Session):
    """Get a subquery of all profile IDs belonging to the current user"""
    return db_session.query(Profile.id).filter(
        Profile.user_id == current_user.id
    ).subquery() 