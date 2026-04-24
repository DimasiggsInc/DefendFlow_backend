"""Модели пользователей для БД."""

from sqlalchemy import UUID, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import datetime

from src.database import Base
from src.users.models import User


class Admin(Base):
    """Модель администратора."""
    __tablename__ = "admin"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Внешний ключ на User
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Связь обратно к User
    user: Mapped["User"] = relationship("User", back_populates="admin_profile")
