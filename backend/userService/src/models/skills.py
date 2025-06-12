from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, func, DateTime, ForeignKey, Integer
from src.utils.db import Base

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    proficiency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationship
    profile: Mapped["Profile"] = relationship(back_populates="skills")
