from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated

from src.utils import db
from src.models import projects as project_model
from src.schemas import projects as project_schema
from src.routes.auth import get_current_user
from src.models.users import User
from src.utils.auth_helpers import verify_profile_ownership

# Reusable dependency annotations
DbSession = Annotated[Session, Depends(db.get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    # prefix="/projects", # Prefix is now handled in main.py
    tags=["Profile Projects"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=project_schema.ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project_for_profile(
    profile_id: int, # Comes from path
    project_in: project_schema.ProjectCreateRequest, 
    db_session: DbSession,
    current_user: CurrentUser
):
    """Create a new project for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    project_data = project_in.dict()
    project_data["profile_id"] = profile_id
    db_project = project_model.Project(**project_data)
    db_session.add(db_project)
    db_session.commit()
    db_session.refresh(db_project)
    return db_project

@router.get("", response_model=List[project_schema.ProjectOut])
async def read_projects_for_profile(
    profile_id: int, # Comes from path
    db_session: DbSession,
    current_user: CurrentUser,
    skip: int = 0, 
    limit: int = 100
):
    """Get all projects for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    projects = db_session.query(project_model.Project).filter(
        project_model.Project.profile_id == profile_id
    ).offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=project_schema.ProjectOut)
async def read_project_for_profile(
    profile_id: int, # Comes from path
    project_id: int, 
    db_session: DbSession,
    current_user: CurrentUser
):
    """Get a specific project by ID, for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_project = db_session.query(project_model.Project).filter(
        project_model.Project.id == project_id,
        project_model.Project.profile_id == profile_id
    ).first()
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or not part of this profile")
    return db_project

@router.put("/{project_id}", response_model=project_schema.ProjectOut)
async def update_project_for_profile(
    profile_id: int, # Comes from path
    project_id: int, 
    project_update: project_schema.ProjectUpdate, 
    db_session: DbSession,
    current_user: CurrentUser
):
    """Update a project for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_project = db_session.query(project_model.Project).filter(
        project_model.Project.id == project_id,
        project_model.Project.profile_id == profile_id
    ).first()

    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or not part of this profile")
    
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db_session.commit()
    db_session.refresh(db_project)
    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_for_profile(
    profile_id: int, # Comes from path
    project_id: int, 
    db_session: DbSession,
    current_user: CurrentUser
):
    """Delete a project for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_project = db_session.query(project_model.Project).filter(
        project_model.Project.id == project_id,
        project_model.Project.profile_id == profile_id
    ).first()

    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or not part of this profile")
    
    db_session.delete(db_project)
    db_session.commit()
    return None

@router.post("/bulk", response_model=List[project_schema.ProjectOut], status_code=status.HTTP_201_CREATED)
async def create_bulk_projects_for_profile(
    profile_id: int, # Comes from path
    projects_in: List[project_schema.ProjectCreateRequest], 
    db_session: DbSession,
    current_user: CurrentUser
):
    """Create multiple projects at once for a specific profile owned by the user."""
    verify_profile_ownership(profile_id, current_user, db_session)
    
    db_projects = []
    for proj_in in projects_in:
        proj_data = proj_in.dict()
        proj_data["profile_id"] = profile_id
        db_projects.append(project_model.Project(**proj_data))
        
    db_session.add_all(db_projects)
    db_session.commit()
    for proj in db_projects:
        db_session.refresh(proj)
    return db_projects 