"""Модели пользователей для БД."""

from sqlalchemy import UUID, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import datetime
from typing import Optional

from src.database import Base
from src.users.models import User

class Expert(Base):
    """Модель эксперта."""
    __tablename__ = "expert"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False)
    
    # Специфичные поля эксперта
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="expert_profile")
