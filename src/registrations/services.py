import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import (
    UUID, String, DateTime, func, ForeignKey, Text, Integer, Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base  # Ваш базовый класс

# Импорты для TYPE_CHECKING, чтобы избежать циклических импортов
if TYPE_CHECKING:
    from src.users.models import User
    from src.students.models import Student
    from src.experts.models import Expert
    from src.admins.models import Admin
    from src.projects.models import ProjectMember  # Предположительно

class Curator(Base):
    """Профиль куратора."""
    __tablename__ = "curator"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, unique=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="curator_profile") # Убедитесь, что в User добавлено это поле
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="curator")


class Project(Base):
    """Проект студента."""
    __tablename__ = "project"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    curator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curator.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Отношения
    curator: Mapped["Curator"] = relationship("Curator", back_populates="projects")
    members: Mapped[List["ProjectMember"]] = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    links: Mapped[List["ProjectLink"]] = relationship("ProjectLink", back_populates="project", cascade="all, delete-orphan")
    # Обратные связи для регистраций, если нужны
    student_registrations: Mapped[List["StudentRegistration"]] = relationship("StudentRegistration", back_populates="project")


class ProjectLink(Base):
    """Ссылки проекта (git, design, etc)."""
    __tablename__ = "project_link"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # git/design/etc
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Отношения
    project: Mapped["Project"] = relationship("Project", back_populates="links")


class ProjectMember(Base):
    """Участник проекта (связывает студента и проект)."""
    __tablename__ = "project_member"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("student.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    role_in_team: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Отношения
    student: Mapped["Student"] = relationship("Student", back_populates="project_members")
    project: Mapped["Project"] = relationship("Project", back_populates="members")
    registrations: Mapped[List["StudentRegistration"]] = relationship("StudentRegistration", back_populates="member")
