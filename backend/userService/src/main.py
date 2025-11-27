from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.core.config import settings
from src.routes import user, auth, profiles, skills, projects, experience, education, resumes
from src.utils.db import Base, engine
from src.models.users import User
from src.models.profiles import Profile
from src.models.skills import Skill
from src.models.projects import Project
from src.models.experience import Experience
from src.models.education import Education
from src.models.generated_resumes import GeneratedResume
from src.models.llm_requests import LLMRequest


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API for managing users, profiles, and resume components for AI-powered resume generation.",
    version=settings.app_version,
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(profiles.router)
app.include_router(resumes.router)
app.include_router(skills.router, prefix="/profiles/{profile_id}/skills", tags=["Profile Skills"])
app.include_router(experience.router, prefix="/profiles/{profile_id}/experience", tags=["Profile Experience"])
app.include_router(education.router, prefix="/profiles/{profile_id}/education", tags=["Profile Education"])
app.include_router(projects.router, prefix="/profiles/{profile_id}/projects", tags=["Profile Projects"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume Service API", "version": settings.app_version}


@app.get("/health")
def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "environment": settings.environment,
            "app": settings.app_name,
            "version": settings.app_version
        }
    )
