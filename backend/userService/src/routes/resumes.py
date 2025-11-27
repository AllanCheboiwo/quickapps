from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.utils.db import get_db
from src.routes.auth import get_current_user
from src.utils.auth_helpers import verify_profile_ownership, verify_resume_ownership
from src.utils.rate_limiter import ResumeRateLimiter
from src.models.users import User
from src.schemas.resumes import ResumeGenerateRequest, ResumeResponse, ResumeListResponse
from src.services.resume_service import ResumeService
from src.core.exceptions import RateLimitExceeded
import logging

logger = logging.getLogger(__name__)


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
    responses={404: {"description": "Not found"}},
)


resume_service = ResumeService()

@router.post("/generate", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def generate_resume(
    request: ResumeGenerateRequest,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Generate a tailored resume in LaTeX format for a specific profile and job description.
    Users can copy the LaTeX and compile to PDF using Overleaf or local LaTeX editor.
    
    Rate limited to 5 resumes per hour per user to prevent token waste.
    """
    try:
    
        ResumeRateLimiter.check_rate_limit(current_user.id, db)
        
        
        verify_profile_ownership(request.profile_id, current_user, db)
        
        generated_resume = await resume_service.generate_resume(
            user_id=current_user.id,
            profile_id=request.profile_id,
            job_description=request.job_description,
            db=db
        )
        
       
        ResumeRateLimiter.log_generation(current_user.id, request.profile_id, db)
        
        return generated_resume
    
    except RateLimitExceeded as e:
        raise e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Resume generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate resume"
        )

@router.get("", response_model=List[ResumeListResponse])
def get_user_resumes(
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get all generated resumes for the current user
    """
    try:
        resumes = resume_service.get_user_resumes(current_user.id, db)
        return resumes
    except Exception as e:
        logger.error(f"Error fetching user resumes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch resumes"
        )

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get a specific resume by ID
    """
    try:
    
        resume = verify_resume_ownership(resume_id, current_user, db)
        return resume
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch resume"
        )

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Delete a generated resume
    """
    try:
       
        resume = verify_resume_ownership(resume_id, current_user, db)
        db.delete(resume)
        db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resume"
        ) 