"""Модели пользователей для БД."""

from sqlalchemy import UUID, DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from typing import Optional
from datetime import datetime

from src.database import Base
from src.users.models import User


class Student(Base):
    """Модель студента."""
    __tablename__ = "student"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False)
    
    # Специфичные поля студента
    academ_group: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="student_profile")
