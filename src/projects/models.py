import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
from enum import Enum

from sqlalchemy import (
    UUID, String, DateTime, func, ForeignKey, Text, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.curators.models import Curator
    from src.students.models import Student
    from src.registrations.models import StudentRegistration



class ProjectLinkType(str, Enum):
    """Типы ссылок для проекта."""
    
    # Репозитории
    GITHUB = "GitHub"
    GITLAB = "GitLab"
    OTHER_REPO = "Other Repository"

    # Продукт
    WEB = "Web Application"
    MOBILE_APP = "Mobile Application"
    ADMIN_PANEL = "Admin Panel"

    # Документация и Дизайн
    API_DOCS = "API Documentation (Swagger/Postman)"
    DESIGN = "Design / Prototype (Figma)"
    DOCUMENTATION = "Technical Documentation"
    PRESENTATION = "Presentation (Online)"
    DATABASE_SCHEMA = "Database Schema"
    ANALYTICS = "Analytics / Metrics Dashboard"

    # Медиа
    VIDEO_DEMO = "Video Demo"

    # Остальное
    OTHER = "Other"


class Project(Base):
    """Проект студента."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    curator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curator.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


    curator: Mapped["Curator"] = relationship("Curator", back_populates="projects")
    members: Mapped[List["ProjectMember"]] = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    links: Mapped[List["ProjectLink"]] = relationship("ProjectLink", back_populates="project", cascade="all, delete-orphan")
    
    student_registrations: Mapped[List["StudentRegistration"]] = relationship("StudentRegistration", back_populates="project")


class ProjectLink(Base):
    """Ссылки проекта (git, design, etc)."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[ProjectLinkType] = mapped_column(SQLEnum(ProjectLinkType), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


    project: Mapped["Project"] = relationship("Project", back_populates="links")


class ProjectMember(Base):
    """Участник проекта (связывает студента и проект)."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("student.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    role_in_team: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


    student: Mapped["Student"] = relationship("Student", back_populates="project_members")
    project: Mapped["Project"] = relationship("Project", back_populates="members")
    registrations: Mapped[List["StudentRegistration"]] = relationship("StudentRegistration", back_populates="member")
