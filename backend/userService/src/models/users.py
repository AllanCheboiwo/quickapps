from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String,func,DateTime
from src.utils.db import Base


class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50),unique=True,index=True,nullable=False)
    email: Mapped[str] = mapped_column(unique=True,nullable=False,index=True)
    hashedPassword: Mapped[str] = mapped_column(nullable=False)
    firstName: Mapped[str] = mapped_column()
    lastName:Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate = func.now(),nullable=False)

    # #relationship
    # profiles: Mapped[List["Profile"]] = relationship(back_populates="users")

    def __repr__(self) -> str:
        return f"<User id={self.id}, email='{self.email}'>"
