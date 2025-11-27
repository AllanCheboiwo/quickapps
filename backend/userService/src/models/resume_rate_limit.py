"""
Model for tracking resume generation rate limits
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, DateTime, func, ForeignKey
from src.utils.db import Base


class ResumeRateLimit(Base):
    
    __tablename__ = "resume_rate_limits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    def __repr__(self):
        return f"<ResumeRateLimit(id={self.id}, user_id={self.user_id}, profile_id={self.profile_id})>"

