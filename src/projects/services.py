from datetime import date, datetime, time
from typing import List
from uuid import UUID

from fastapi import HTTPException, status

from src.registrations.services import PermissionDeniedError
from src.curators.models import Curator
from src.projects.interfaces import ProjectServicePort, ProjectRepositoryPort
from src.projects.models import Project, ProjectLink, ProjectMember, ProjectMemberNotAuth
from src.projects.exceptions import ProjectNotFoundError, ProjectLinkNotFoundError, ProjectMemberNotFoundError
from src.projects.schemas import (
    MyProjectResponse, ProjectFullSchemaResponse, ProjectCalendarItemResponse, ProjectLink as ProjectLinkSchema, ProjectMemberNotAuthCreateRequest, ProjectMemberNotAuthSchema, ProjectMemberNotAuthUpdateRequest, ProjectMemberResponse, 
    ProjectMemberSchema, CuratorSchema, ProjectCreateRequest, ProjectUpdateRequest,
    ProjectLinkCreateRequest, ProjectLinkUpdateRequest, ProjectMemberAddRequest, ProjectMemberUpdateRequest
)


class ProjectService(ProjectServicePort):
    def __init__(self, project_repo: ProjectRepositoryPort):
        self.project_repo = project_repo
    
    @staticmethod
    def _map_not_auth_member_to_schema(member: ProjectMemberNotAuth) -> ProjectMemberNotAuthSchema:
        """Маппит ORM ProjectMemberNotAuth в Pydantic ProjectMemberNotAuthSchema."""
        return ProjectMemberNotAuthSchema(
            id=member.id,
            first_name=member.first_name,
            last_name=member.last_name,
            middle_name=member.middle_name,
            role_in_team=member.role_in_team or "",
            academ_group=member.academ_group
        )
    
    @staticmethod
    def _map_member_to_schema(member: ProjectMember) -> ProjectMemberSchema:
        """Маппит ORM ProjectMember в Pydantic ProjectMemberSchema."""
        student_profile = member.student
        user = student_profile.user
        
        # Проверяем, как называется поле группы в вашей модели Student (academ_group или academGroup)
        academ_group = getattr(student_profile, "academ_group", None) or getattr(student_profile, "academGroup", "")
        
        return ProjectMemberSchema(
            id=user.id, # Или student_profile.id, если они различаются
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            academGroup=academ_group,
            roleInTeam=member.role_in_team or ""
        )
    
    @staticmethod
    def _map_link_to_schema(link: ProjectLink) -> ProjectLinkSchema:
        """Маппит ORM ProjectLink в Pydantic ProjectLinkSchema."""
        return ProjectLinkSchema(
            id=link.id,
            name=link.name,
            type=link.type,
            url=link.url,
            description=link.description
        )

    @staticmethod
    def _map_curator_to_schema(curator: Curator) -> CuratorSchema:
        """Маппит ORM Curator в Pydantic CuratorSchema."""
        user = curator.user
        return CuratorSchema(
            id=curator.id, # Или user.id
            firstName=user.first_name,
            lastName=user.last_name,
            middleName=user.middle_name
        )

    async def get_my_projects(self, user_id: UUID) -> List[MyProjectResponse]:
        """Получить проекты текущего пользователя (студента)."""
        projects = await self.project_repo.get_my_projects(user_id)
        return [self._map_to_my_project(p) for p in projects]


    def _map_to_my_project(self, project: Project) -> MyProjectResponse:
        """Маппинг Project в MyProjectResponse."""
        # Дата/время защиты и аудитория
        defense_datetime = None
        room_name = None
        
        if project.student_registrations:
            reg = project.student_registrations[0]
            if reg.slot:
                defense_datetime = datetime.combine(
                    reg.slot.date,
                    reg.slot.time_start
                )
            if reg.room:
                room_name = reg.room.name
        
        # Участники команды
        members = []
        for member in project.members:
            student_name = None
            if member.student:
                # Предполагаем, что у Student есть поле full_name или name
                student_name = (
                    getattr(member.student, 'full_name', None) or 
                    getattr(member.student, 'name', None)
                )
            members.append(ProjectMemberResponse(
                id=member.id,
                student_id=member.student_id,
                student_name=student_name,
                role_in_team=member.role_in_team
            ))
        
        # Куратор
        curator_name = None
        if project.curator:
            curator_name = (
                getattr(project.curator, 'full_name', None) or 
                getattr(project.curator, 'name', None) or
                getattr(project.curator, 'email', None)
            )
        
        return MyProjectResponse(
            id=project.id,
            projectName=project.name,
            curator_name=curator_name,
            members=members,
            defenseDateTime=defense_datetime,
            room_name=room_name
        )

    async def get_projects_calendar(self, user_id: UUID) -> List[ProjectCalendarItemResponse]:
        """Получить список всех проектов для календаря (только админ или эксперт)."""
        if not await self.project_repo.is_user_admin_or_expert(user_id):
            raise PermissionDeniedError(
                "Доступ запрещен. Требуются права администратора или эксперта."
            )
        
        projects = await self.project_repo.get_projects_calendar()
        return [self._map_to_calendar_item(p) for p in projects]


    def _map_to_calendar_item(self, project: Project) -> ProjectCalendarItemResponse:
        """Маппинг Project в ProjectCalendarItemResponse."""
        # Формируем defenseDateTime из даты и времени начала защиты
        defense_datetime = None
        
        if project.student_registrations:
            reg = project.student_registrations[0]
            if reg.slot:
                # Объединяем date и time_start в один datetime
                defense_datetime = datetime.combine(
                    reg.slot.date,
                    reg.slot.time_start
                )
        
        return ProjectCalendarItemResponse(
            id=project.id,
            projectName=project.name,
            defenseDateTime=defense_datetime or datetime.min
        )

    async def get_project_info(self, project_id: UUID) -> ProjectFullSchemaResponse:
        project = await self.project_repo.get_project_with_details(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
            
        return ProjectFullSchemaResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            curator=self._map_curator_to_schema(project.curator) if project.curator else None,
            team=[self._map_member_to_schema(m) for m in project.members],

            not_auth_members=[self._map_not_auth_member_to_schema(m) for m in project.members_not_auth],
            projectLinks=[self._map_link_to_schema(i) for i in project.links]
        )

    async def get_project_team(self, project_id: UUID) -> List[ProjectMemberSchema]:
        members = await self.project_repo.get_project_team(project_id)
        return [self._map_member_to_schema(i) for i in members]

    async def get_project_links(self, project_id: UUID) -> List[ProjectLinkSchema]:
        links = await self.project_repo.get_project_links(project_id)
        return [self._map_link_to_schema(i) for i in links]


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
            description=project_data.description
        )
        
        # 3. Сохраняем проект и добавляем создателя в одной транзакции
        created_project = await self.project_repo.create_project_with_creator(
            project=new_project,
            creator_student_id=student_id,
            creator_role="Team Lead"
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

    async def delete_project_link(self, project_id: UUID, link_id: UUID) -> None:
        await self.project_repo.delete_project_link(project_id, link_id)
    
    async def delete_all_project_links(self, project_id: UUID):
        await self.project_repo.delete_all_project_links(project_id)

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
    
    async def delete_project(self, project_id: UUID):
        await self.project_repo.delete_all_project_members(project_id)
        await self.project_repo.delete_project(project_id)



    # --- Not auth members ---
    async def add_project_not_auth_member(self, project_id: UUID, data: ProjectMemberNotAuthCreateRequest) -> ProjectMemberNotAuthSchema:
        if not await self.project_repo.get_project_with_details(project_id):
            raise ProjectNotFoundError(project_id)

        member = ProjectMemberNotAuth(
            project_id=project_id,
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            role_in_team=data.role_in_team,
            academ_group=data.academ_group
        )
        saved_member = await self.project_repo.add_project_not_auth_member(member)
        return self._map_not_auth_member_to_schema(saved_member)

    async def update_project_not_auth_member(self, project_id: UUID, member_id: UUID, data: ProjectMemberNotAuthUpdateRequest) -> ProjectMemberNotAuthSchema:
        member = await self.project_repo.get_not_auth_member_by_id(project_id, member_id)
        if not member:
            raise ProjectMemberNotFoundError(member_id)
            
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)
            
        await self.project_repo.update_project_not_auth_member(member)
        return self._map_not_auth_member_to_schema(member)

    async def delete_project_not_auth_member(self, project_id: UUID, member_id: UUID) -> None:
        await self.project_repo.delete_project_not_auth_member(project_id, member_id)

    async def delete_all_project_not_auth_members(self, project_id: UUID) -> None:
        await self.project_repo.delete_all_project_not_auth_members(project_id)