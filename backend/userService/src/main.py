from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import user 
from src.routes import auth 
from src.routes import profiles
from src.routes import skills
from src.routes import projects
from src.routes import experience
from src.routes import education
from src.routes import resumes
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
    title="Resume Service API",
    description="API for managing users, profiles, and resume components for AI-powered resume generation.",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(profiles.router)
app.include_router(resumes.router)

# Include nested routers under profiles
app.include_router(skills.router, prefix="/profiles/{profile_id}/skills", tags=["Profile Skills"])
app.include_router(experience.router, prefix="/profiles/{profile_id}/experience", tags=["Profile Experience"])
app.include_router(education.router, prefix="/profiles/{profile_id}/education", tags=["Profile Education"])
app.include_router(projects.router, prefix="/profiles/{profile_id}/projects", tags=["Profile Projects"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume Service API"}
