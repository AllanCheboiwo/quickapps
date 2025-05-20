from fastapi import FastAPI
from src.routes import user as user_router # User router
# from src.routes import profile as profile_router # If you have a profile router
from src.utils.db import Base, engine # For DB initialization
from src.models import users # Import models to ensure they are registered with Base

# This is important: Call this to create tables if they don't exist.
# In a production app, you'd typically use Alembic for migrations.
# Ensure all your models are imported by src.utils.db.create_db_and_tables or here before calling this.
Base.metadata.create_all(bind=engine) # Creates tables based on models registered with Base

app = FastAPI(
    title="User Service API",
    description="API for managing users and profiles.",
    version="0.1.0"
)

# Include your routers
app.include_router(user_router.router)
# app.include_router(profile_router.router) # If you have a profile router

@app.get("/")
def read_root():
    return {"message": "Welcome to the User Service"}

# To run this app (from backend/userService directory):
# uvicorn src.main:app --reload
