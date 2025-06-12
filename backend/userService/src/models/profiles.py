from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String,func,DateTime, ForeignKey
from src.utils.db import Base

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100),nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate = func.now(),nullable=False)

    user: Mapped["User"] = relationship(back_populates="profiles")
    education: Mapped[List["Education"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    experience: Mapped[List["Experience"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    projects: Mapped[List["Project"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    skills: Mapped[List["Skill"]] = relationship(back_populates="profile", cascade="all, delete-orphan")

    

