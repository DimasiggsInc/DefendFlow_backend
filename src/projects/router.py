"""Обработчик проектов."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_user

from src.projects.schemas import CuratorSchema, ProjectFullSchemaResponse, ProjectMemberSchema, ProjectLink, ProjectLinkType


router = APIRouter(
    prefix="/project",
    tags=["Project"],
)


@router.get("/{project_id}", response_model=ProjectFullSchemaResponse, status_code=status.HTTP_200_OK)
async def get_project_info(project_id: uuid.UUID,): # current_user: dict = Depends(get_current_user)
    """Получить информацию о проекте. (Пока что возвращает заглушку)"""
    curator = CuratorSchema(
        id="123e4567-e89b-12d3-a456-426614174001",
        firstName="Иван",
        lastName="Иванов",
        middleName="Иванович"
    )
    
    member = ProjectMemberSchema(
        id="123e4567-e89b-12d3-a456-426614174002",
        email="mail@example.com",
        firstName="Петр",
        lastName="Петров",
        middleName="Петрович",
        academGroup="РИ-1488_67_42_52",
        roleInTeam="Разработчик"
    )

    link1 = ProjectLink(
        id="123e4567-e89b-12d3-a456-426614174003",
        name="GitHub Repository",
        type=ProjectLinkType.GITHUB,
        url="github.com/example/project",
        description="Репозиторий проекта на GitHub"
    )
    link2 = ProjectLink(
        id="123e4567-e89b-12d3-a456-426614174004",
        name="Figma Design",
        type=ProjectLinkType.DESIGN,
        url="figma.com/example/project-design",
        description="Дизайн проекта в Figma"
    )

    project = ProjectFullSchemaResponse(
        id=project_id,
        name="Пример проекта",
        description="Это пример описания проекта.",
        curator=curator,
        team=[member, member],
        projectLinks=[link1, link2],
    )
    return project
