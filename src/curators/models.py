import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import (
    UUID, String, DateTime, func, ForeignKey, Text, Integer, Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
if TYPE_CHECKING:
    from src.users.models import User
    from src.projects.models import Project


class Curator(Base):
    """Профиль куратора."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, unique=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="curator_profile")
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="curator")
