"""Схемы для проектов."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from src.users.schemas import StudentSchemaFull, UserRolesEnum



# TODO: Перенести в отдельные файлы
class ProjectMemberSchema(StudentSchemaFull):
    """Схема для участника проекта."""
    roleInTeam: Optional[str] = None

class CuratorSchema(BaseModel):
    """Схема для куратора проекта."""
    model_config = ConfigDict(from_attributes=True) 
    id: UUID
    firstName: Optional[str] = Field(None, validation_alias="user.first_name") 
    lastName: Optional[str] = Field(None, validation_alias="user.last_name")
    middleName: Optional[str] = Field(None, validation_alias="user.middle_name")

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
    team: Optional[List[ProjectMemberSchema]] = None
    projectLinks: Optional[List[ProjectLink]] = None





class DefenseParticipantResponse(BaseModel):
    """Участник защиты: студент или член команды."""
    id: UUID
    fullName: str = None


class DefenseObserverResponse(BaseModel):
    """Наблюдатель на защите: преподаватель, эксперт, куратор."""
    id: UUID
    fullName: str
    role: UserRolesEnum


class ProjectCalendarItemResponse(BaseModel):
    """Краткая информация о проекте для календаря защит."""
    id: UUID
    projectName: str
    defenseDateTime: datetime
    
    isCurrentUserRegistered: bool = False
    
    participants: list[DefenseParticipantResponse] = Field(default_factory=list)
    observers: list[DefenseObserverResponse] = Field(default_factory=list)


class ProjectCreateRequest(BaseModel):
    """Схема для создания проекта."""
    name: str
    description: Optional[str] = None
    # curator_id: UUID # Куратор обычно назначается сразу

class ProjectUpdateRequest(BaseModel):
    """Схема для обновления базовой информации проекта."""
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectLinkCreateRequest(BaseModel):
    """Схема для добавления ссылки."""
    name: str
    type: ProjectLinkType
    url: str
    description: Optional[str] = None

class ProjectLinkUpdateRequest(BaseModel):
    """Схема для обновления ссылки."""
    name: Optional[str] = None
    type: Optional[ProjectLinkType] = None
    url: Optional[str] = None
    description: Optional[str] = None

class ProjectMemberAddRequest(BaseModel):
    """Схема для добавления участника (студента) в проект."""
    student_id: UUID
    role_in_team: Optional[str] = None

class ProjectMemberUpdateRequest(BaseModel):
    """Схема для обновления роли участника."""
    role_in_team: Optional[str] = None

class CuratorAssignRequest(BaseModel):
    """Схема для назначения или смены куратора."""
    curator_id: UUID
