"""Модели админа для БД."""

from sqlalchemy import UUID, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import datetime
from typing import TYPE_CHECKING


from src.database import Base
if TYPE_CHECKING:
    from src.users.models import User
# from src.users.schemas import UserSchemaFull, StudentSchema


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
