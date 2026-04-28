"""Схемы для проектов."""

from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from src.users.schemas import StudentSchemaFull



# TODO: Перенести в отдельные файлы
class ProjectMemberSchema(StudentSchemaFull):
    """Схема для участника проекта."""
    roleInTeam: str

class CuratorSchema(BaseModel):
    """Схема для куратора проекта."""
    id: UUID
    firstName: str
    lastName: str
    middleName: str

class ProjectLinkType(str, Enum):
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

class ProjectLink(BaseModel):
    """Схема для ссылки на проект."""
    id: UUID
    name: str
    type: ProjectLinkType
    url: str
    description: Optional[str] = None





class ProjectSchemaAdd(BaseModel):
    """Схема для добавления проектов."""

    name: str
    description: Optional[str] = None


class ProjectSchema(BaseModel):
    """Схема для проекта."""
    id: UUID
    name: str
    description: Optional[str] = None
    curator: Optional[CuratorSchema] = None


class ProjectFullSchemaResponse(ProjectSchema):
    """Схема для ответа информации о проекте."""
    team: List[ProjectMemberSchema]
    projectLinks: List[ProjectLink]
