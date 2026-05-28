from typing import List, Any
from uuid import UUID

from fastapi import HTTPException, status

from src.projects.interfaces import ProjectServicePort, ProjectRepositoryPort
from src.projects.models import Project, ProjectLink, ProjectMember
from src.projects.exceptions import ProjectNotFoundError, ProjectLinkNotFoundError, ProjectMemberNotFoundError
from src.projects.schemas import (
    ProjectFullSchemaResponse, ProjectCalendarItemResponse, ProjectLink as ProjectLinkSchema, 
    ProjectMemberSchema, CuratorSchema, ProjectCreateRequest, ProjectUpdateRequest,
    ProjectLinkCreateRequest, ProjectLinkUpdateRequest, ProjectMemberAddRequest, ProjectMemberUpdateRequest
)


class ProjectService(ProjectServicePort):
    def __init__(self, project_repo: ProjectRepositoryPort):
        self.project_repo = project_repo

    async def get_projects_calendar(self) -> List[ProjectCalendarItemResponse]:
        projects = await self.project_repo.get_projects_calendar()
        # TODO: Реализовать маппинг ORM объектов Project в ProjectCalendarItemResponse
        # return [map_to_calendar(p) for p in projects]
        return [] 

    async def get_project_info(self, project_id: UUID) -> Any:
        project = await self.project_repo.get_project_with_details(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
        return project # FastAPI сам сконвертирует ORM модель в Pydantic схему через response_model

    async def get_project_links(self, project_id: UUID) -> List[ProjectLinkSchema]:
        return await self.project_repo.get_project_links(project_id)

    async def get_project_team(self, project_id: UUID) -> List[ProjectMemberSchema]:
        return await self.project_repo.get_project_team(project_id)
    
    async def get_projects_calendar(self, current_user_id: UUID) -> List[ProjectCalendarItemResponse]:
        projects = await self.project_repo.get_projects_calendar()
        # Здесь должна быть логика маппинга ORM -> ProjectCalendarItemResponse
        # и проверка, зарегистрирован ли current_user_id на защиту
        return [] 

    async def get_project_info(self, project_id: UUID) -> ProjectFullSchemaResponse:
        project = await self.project_repo.get_project_with_details(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
        return project # FastAPI сам преобразует ORM в Pydantic благодаря response_model


    # ======= Методы создания и обновления =======

    async def create_project(
        self, 
        project_data: ProjectCreateRequest, 
        creator_id: UUID
    ) -> ProjectFullSchemaResponse:
        
        # 1. Находим профиль студента для создателя
        student_id = await self.project_repo.get_student_id_by_user_id(creator_id)
        if not student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не найден в таблице студентов или не имеет прав на создание проекта."
            )

        # 2. Создаем ORM объект проекта
        new_project = Project(
            name=project_data.name,
            description=project_data.description,
            curator_id=project_data.curator_id
        )
        
        # 3. Сохраняем проект и добавляем создателя в одной транзакции
        created_project = await self.project_repo.create_project_with_creator(
            project=new_project,
            creator_student_id=student_id,
            creator_role="Team Lead" # Роль создателя по умолчанию
        )
        
        # 4. Возвращаем полный профиль (подтянет пустые links и уже созданного team member)
        return await self.get_project_info(created_project.id)

    async def update_project(self, project_id: UUID, project_data: ProjectUpdateRequest) -> ProjectFullSchemaResponse:
        project = await self.project_repo.get_project_with_details(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
            
        # Обновляем только те поля, которые пришли (Partial Update логика)
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
            
        await self.project_repo.update_project(project)
        return await self.get_project_info(project_id)

    # --- Links ---
    async def add_project_link(self, project_id: UUID, link_data: ProjectLinkCreateRequest) -> ProjectLinkSchema:
        # Проверяем существование проекта
        if not await self.project_repo.get_project_with_details(project_id):
            raise ProjectNotFoundError(project_id)

        link = ProjectLink(
            project_id=project_id,
            name=link_data.name,
            type=link_data.type,
            url=link_data.url,
            description=link_data.description
        )
        saved_link = await self.project_repo.add_project_link(link)
        return saved_link

    async def update_project_link(self, project_id: UUID, link_id: UUID, link_data: ProjectLinkUpdateRequest) -> ProjectLinkSchema:
        link = await self.project_repo.get_link_by_id(project_id, link_id)
        if not link:
            raise ProjectLinkNotFoundError(link_id)
            
        update_data = link_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(link, field, value)
            
        return await self.project_repo.update_project_link(link)

    # --- Team ---
    async def add_project_member(self, project_id: UUID, member_data: ProjectMemberAddRequest) -> ProjectMemberSchema:
        if not await self.project_repo.get_project_with_details(project_id):
            raise ProjectNotFoundError(project_id)

        member = ProjectMember(
            project_id=project_id,
            student_id=member_data.student_id,
            role_in_team=member_data.role_in_team
        )
        saved_member = await self.project_repo.add_project_member(member)
        # Для возврата ProjectMemberSchema нужно подтянуть данные студента из БД
        return await self.project_repo.get_member_by_id(project_id, saved_member.id)

    async def update_project_member(self, project_id: UUID, member_id: UUID, member_data: ProjectMemberUpdateRequest) -> ProjectMemberSchema:
        member = await self.project_repo.get_member_by_id(project_id, member_id)
        if not member:
            raise ProjectMemberNotFoundError(member_id)
            
        if member_data.role_in_team is not None:
            member.role_in_team = member_data.role_in_team
            
        await self.project_repo.update_project_member(member)
        return await self.project_repo.get_member_by_id(project_id, member_id)

    # --- Curator ---
    async def assign_curator(self, project_id: UUID, curator_id: UUID) -> CuratorSchema:
        # 1. Обновляем связь в БД
        updated_project = await self.project_repo.update_project_curator(project_id, curator_id)
        if not updated_project:
            raise ProjectNotFoundError(project_id)
            
        # 2. Заново получаем полный профиль проекта со всеми связями (включая User)
        # Это безопасный паттерн для Async SQLAlchemy после commit()
        full_project = await self.project_repo.get_project_with_details(project_id)
        
        # 3. Извлекаем данные из связанной таблицы User
        curator_profile = full_project.curator
        user_data = curator_profile.user # Переходим к таблице User
        
        return CuratorSchema(
            id=curator_profile.id, # Или user_data.id, если в схеме ожидается ID юзера
            firstName=user_data.first_name,
            lastName=user_data.last_name,
            middleName=user_data.middle_name
        )

    async def remove_curator(self, project_id: UUID) -> None:
        # Если в БД curator_id nullable=False, здесь нужно назначать "системного" куратора
        # либо менять схему БД.
        project = await self.project_repo.remove_project_curator(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
