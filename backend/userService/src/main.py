from fastapi import FastAPI
from src.routes import user 
from src.routes import auth 
from src.utils.db import Base, engine 
from src.models.users import User

Base.metadata.create_all(bind=engine) 

app = FastAPI(
    title="User Service API",
    description="API for managing users and profiles.",
    version="0.1.0"
)


app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the User Service"}
