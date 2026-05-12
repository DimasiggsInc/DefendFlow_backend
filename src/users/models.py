"""Модели пользователей для БД."""

from sqlalchemy import UUID, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING


from src.database import Base
if TYPE_CHECKING:
    from src.admins.models import Admin
    from src.students.models import Student
    from src.experts.models import Expert
    from src.curators.models import Curator

class User(Base):
    """
    Базовая модель пользователя.
    Содержит данные для авторизации и общие профилированные данные.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    # Поля из схемы БД
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)

    # Поля для аутентификации (из вашего кода)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Отношения (Relationships) - "Один ко многим" или "Один к одному"
    # back_populates позволяет обращаться из дочерней модели к родительской
    admin_profile: Mapped[Optional["Admin"]] = relationship("Admin", back_populates="user", uselist=False, cascade="all, delete-orphan")
    curator_profile: Mapped[Optional["Curator"]] = relationship("Curator", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student_profile: Mapped[Optional["Student"]] = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    expert_profile: Mapped[Optional["Expert"]] = relationship("Expert", back_populates="user", uselist=False, cascade="all, delete-orphan")
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    def get_full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(filter(None, parts))

    def to_read_model(self):
        # Здесь логика преобразования в Pydantic схему
        pass
