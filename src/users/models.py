"""Модели пользователей для БД."""
from __future__ import annotations

from sqlalchemy import UUID, ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import datetime
from typing import Optional

from src.database import Base
# from src.users.schemas import UserSchemaFull, StudentSchema


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
    admin_profile: Mapped[Optional[Admin]] = relationship("Admin", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student_profile: Mapped[Optional[Student]] = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    expert_profile: Mapped[Optional[Expert]] = relationship("Expert", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def get_full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(filter(None, parts))

    def to_read_model(self):
        # Здесь логика преобразования в Pydantic схему
        pass



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
