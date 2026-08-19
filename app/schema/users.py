from sqlalchemy.orm import Mapped, mapped_column
from core.db import Base
from sqlalchemy import String
from datetime import datetime, timezone

class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_date: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_date: Mapped[datetime] = mapped_column(default=datetime.now(), onupdate=datetime.now())