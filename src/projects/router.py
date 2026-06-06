import uuid
from typing import List

from fastapi import APIRouter, status, Depends

from src.projects.interfaces import ProjectServicePort
from src.projects.schemas import (
    CuratorSchema, ProjectCalendarItemResponse, ProjectFullSchemaResponse, 
    ProjectMemberSchema, ProjectLink, ProjectCreateRequest, ProjectUpdateRequest,
    ProjectLinkCreateRequest, ProjectLinkUpdateRequest, ProjectMemberAddRequest,
    ProjectMemberUpdateRequest, CuratorAssignRequest
)
from src.projects.services import ProjectService
from src.projects.dependencies import get_project_service
from src.auth.dependencies import get_current_user
from src.users.schemas import CurrentUser # Ваша зависимость для JWT/Авторизации


router = APIRouter(
    prefix="/project",
    tags=["Project"],
)

#========GET========#

@router.get("/calendar", response_model=List[ProjectCalendarItemResponse], status_code=status.HTTP_200_OK)
async def get_projects_calendar(
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Получить список проектов для календаря защит(Заглушка)."""
    return await service.get_projects_calendar(current_user.id)

@router.get("/{project_id}", response_model=ProjectFullSchemaResponse, status_code=status.HTTP_200_OK)
async def get_project_info(
    project_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Получить информацию о проекте(Заглушка)."""
    # TODO: service.check_access(project_id, current_user)
    return await service.get_project_info(project_id)

@router.get("/{project_id}/links", response_model=List[ProjectLink], status_code=status.HTTP_200_OK)
async def get_project_links(
    project_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Получить ссылки на ресурсы проекта(Заглушка)."""
    return await service.get_project_links(project_id)

@router.get("/{project_id}/team", response_model=List[ProjectMemberSchema], status_code=status.HTTP_200_OK)
async def get_project_team(
    project_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Получить информацию о команде проекта(Заглушка)."""
    return await service.get_project_team(project_id)

#=======POST========#

@router.post("/", response_model=ProjectFullSchemaResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreateRequest,
    service: ProjectServicePort = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Создать новый проект."""
    return await service.create_project(project_data, creator_id=current_user.id)

@router.post("/{project_id}/links", response_model=ProjectLink, status_code=status.HTTP_201_CREATED)
async def add_project_link(
    project_id: uuid.UUID,
    link_data: ProjectLinkCreateRequest,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Добавить ссылку на ресурс проекта(Заглушка)."""
    return await service.add_project_link(project_id, link_data)

@router.post("/{project_id}/team", response_model=ProjectMemberSchema, status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: uuid.UUID,
    member_data: ProjectMemberAddRequest,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Добавить участника в команду проекта(Заглушка)."""
    return await service.add_project_member(project_id, member_data)

@router.post("/{project_id}/curator", response_model=CuratorSchema, status_code=status.HTTP_201_CREATED)
async def assign_project_curator(
    project_id: uuid.UUID,
    curator_data: CuratorAssignRequest,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Назначить куратора проекта(Заглушка)."""
    return await service.assign_curator(project_id, curator_data.curator_id)

#======DELETE=======#

@router.delete("/{project_id}/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_link(
    project_id: uuid.UUID, link_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Удалить ссылку на ресурс проекта(Заглушка)."""
    await service.delete_project_link(project_id, link_id)

@router.delete("/{project_id}/team/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_member(
    project_id: uuid.UUID, member_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Удалить участника из команды проекта(Заглушка)."""
    await service.delete_project_member(project_id, member_id)

@router.delete("/{project_id}/curator", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_curator(
    project_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Удалить куратора проекта(Заглушка)."""
    await service.remove_curator(project_id)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Удалить проект(Заглушка)."""
    await service.delete_project(project_id)

@router.delete("/{project_id}/links", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_project_links(
    project_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Удалить все ссылки на ресурсы проекта(Заглушка)."""
    await service.delete_all_project_links(project_id)

#========PUT========#

@router.put("/{project_id}", response_model=ProjectFullSchemaResponse, status_code=status.HTTP_200_OK)
async def update_project(
    project_id: uuid.UUID, 
    project_data: ProjectUpdateRequest,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Обновить информацию о проекте(Заглушка)."""
    return await service.update_project(project_id, project_data)

@router.put("/{project_id}/links/{link_id}", response_model=ProjectLink, status_code=status.HTTP_200_OK)
async def update_project_link(
    project_id: uuid.UUID, link_id: uuid.UUID, 
    link_data: ProjectLinkUpdateRequest,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Обновить информацию о ссылке на ресурс проекта(Заглушка)."""
    return await service.update_project_link(project_id, link_id, link_data)

@router.put("/{project_id}/team/{member_id}", response_model=ProjectMemberSchema, status_code=status.HTTP_200_OK)
async def update_project_member(
    project_id: uuid.UUID, member_id: uuid.UUID, 
    member_data: ProjectMemberUpdateRequest,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Обновить информацию об участнике команды проекта(Заглушка)."""
    return await service.update_project_member(project_id, member_id, member_data)

@router.put("/{project_id}/curator", response_model=CuratorSchema, status_code=status.HTTP_200_OK)
async def update_project_curator(
    project_id: uuid.UUID, 
    curator_data: CuratorAssignRequest,
    service: ProjectService = Depends(get_project_service),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Обновить (сменить) куратора проекта(Заглушка)."""
    return await service.assign_curator(project_id, curator_data.curator_id)
