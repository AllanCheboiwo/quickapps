from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.utils.db import get_db
from src.routes.auth import get_current_user
from src.utils.auth_helpers import verify_profile_ownership, verify_resume_ownership
from src.models.users import User
from src.schemas.resumes import ResumeGenerateRequest, ResumeResponse, ResumeListResponse
from src.services.resume_service import ResumeService, PDF_OUTPUT_DIR_IN_CONTAINER
import logging
import os
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

# Dependency annotations
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
    responses={404: {"description": "Not found"}},
)

# Initialize resume service
resume_service = ResumeService()

@router.post("/generate", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def generate_resume(
    request: ResumeGenerateRequest,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Generate a tailored resume using AI for a specific profile and job description
    """
    try:
        # Verify profile ownership before generating resume
        verify_profile_ownership(request.profile_id, current_user, db)
        
        generated_resume = await resume_service.generate_resume(
            user_id=current_user.id,
            profile_id=request.profile_id,
            job_description=request.job_description,
            db=db
        )
        return generated_resume
    
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
        # Verify resume ownership before retrieving
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

@router.get("/{resume_id}/pdf")
async def download_resume_pdf(
    resume_id: int,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Download the generated PDF for a specific resume.
    """
    try:
        resume = verify_resume_ownership(resume_id, current_user, db)
        
        if not resume.pdf_file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF not available for this resume. It might be processing or generation might have failed."
            )
        
        # Construct the full path to the PDF file within the container
        # PDF_OUTPUT_DIR_IN_CONTAINER is an absolute path like "/app/generated_pdfs"
        # resume.pdf_file_path is relative like "generated_pdfs/resume_u1_p1_timestamp.pdf"
        # We need to ensure the file path is correctly constructed and secure.
        # For security, os.path.basename is used on the filename part from db.
        
        pdf_filename = os.path.basename(resume.pdf_file_path) 
        # Reconstruct full path using the known base directory and the sanitized filename
        full_pdf_path = os.path.join(PDF_OUTPUT_DIR_IN_CONTAINER, pdf_filename)

        if not os.path.isfile(full_pdf_path):
            logger.error(f"PDF file not found at path: {full_pdf_path} for resume_id: {resume_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF file not found on server."
            )
        
        # Sanitize filename for Content-Disposition header
        # Simple sanitization, more robust might be needed for complex filenames
        safe_filename = pdf_filename.replace("..", "").replace("/", "_").replace("\\", "_")

        return FileResponse(
            path=full_pdf_path,
            media_type='application/pdf',
            filename=safe_filename
            # Use content_disposition_type="inline" for preview in browser if desired, default is "attachment"
            # content_disposition_type="inline" 
        )

    except ValueError as e: # From verify_resume_ownership
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Error serving PDF for resume_id {resume_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not serve PDF file."
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
        # Verify resume ownership before deleting
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