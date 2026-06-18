from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.admins.models import Admin
from src.experts.models import Expert
from src.registrations.models import StudentRegistration
from src.curators.models import Curator
from src.repositories import BaseRepository
from src.projects.interfaces import ProjectRepositoryPort
from src.projects.models import Project, ProjectLink, ProjectMember, ProjectMemberNotAuth
from src.students.models import Student



class ProjectRepository(BaseRepository, ProjectRepositoryPort):
    def __init__(self, model: type[Project], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def is_user_admin_or_expert(self, user_id: UUID) -> bool:
        """Проверка, является ли пользователь админом или экспертом (один запрос)."""
        # Проверяем в таблице admin
        admin_query = select(Admin.id).where(Admin.user_id == user_id)
        admin_result = await self.session.execute(admin_query)
        if admin_result.scalar_one_or_none() is not None:
            return True

        # Проверяем в таблице expert
        expert_query = select(Expert.id).where(Expert.user_id == user_id)
        expert_result = await self.session.execute(expert_query)
        return expert_result.scalar_one_or_none() is not None

    async def get_my_projects(self, user_id: UUID) -> List[Project]:
        """
        Получить все проекты, в которых пользователь является участником.
        Цепочка: users.id -> student.user_id -> project_member.student_id -> project
        """
        stmt = (
            select(self.model)
            .join(ProjectMember, ProjectMember.project_id == self.model.id)
            .join(Student, Student.id == ProjectMember.student_id)
            .where(Student.user_id == user_id)
            .options(
                selectinload(self.model.members).selectinload(ProjectMember.student),
                selectinload(self.model.curator),
                selectinload(self.model.student_registrations)
                    .selectinload(StudentRegistration.slot),
                selectinload(self.model.student_registrations)
                    .selectinload(StudentRegistration.room)
            )
            .distinct()  # Чтобы избежать дубликатов, если у студента несколько ролей
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_projects_calendar(self) -> List[Project]:
        """
        Загружаем проекты с данными о защите для календаря.
        Включаем: members, curator, student_registrations (со слотом и комнатой).
        """
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.members).selectinload(ProjectMember.student),
                selectinload(self.model.curator),
                selectinload(self.model.student_registrations)
                    .selectinload(StudentRegistration.slot),
                selectinload(self.model.student_registrations)
                    .selectinload(StudentRegistration.room)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_project_with_details(self, project_id: UUID) -> Optional[Project]:
        """
        Загружает проект со всеми вложенными данными, включая неавторизованных участников.
        """
        stmt = (
            select(self.model)
            .where(self.model.id == project_id)
            .options(
                # 1. Загружаем Куратора и его User
                selectinload(Project.curator).selectinload(Curator.user), 
                
                # 2. Загружаем Авторизованных Участников и их Student -> User
                selectinload(Project.members)
                    .selectinload(ProjectMember.student)
                    .selectinload(Student.user),
                
                # 3. 👇 ОБЯЗАТЕЛЬНО: Загружаем Неавторизованных Участников
                selectinload(Project.members_not_auth),
                
                # 4. Загружаем Ссылки
                selectinload(Project.links)
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_project_links(self, project_id: UUID) -> List[ProjectLink]:
        stmt = select(ProjectLink).where(ProjectLink.project_id == project_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_project_team(self, project_id: UUID) -> List[ProjectMember]:
        """
        Отдельный метод для команды, если он используется независимо.
        """
        stmt = (
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .options(
                selectinload(ProjectMember.student)
                    .selectinload(Student.user)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_student_id_by_user_id(self, user_id: UUID) -> Optional[UUID]:
        """
        Ищет таблицу Student по полю user_id.
        (Предполагается, что в модели Student есть поле user_id = ForeignKey("user.id"))
        """
        stmt = select(Student.id).where(Student.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_project_with_creator(
        self, 
        project: Project, 
        creator_student_id: UUID, 
        creator_role: str = "Team Lead"
    ) -> Project:
        # 1. Добавляем проект в сессию
        self.session.add(project)
        
        # 2. Flush генерирует project.id (дефолтный uuid.uuid4 или от БД), 
        # но НЕ делает commit. Транзакция остается открытой.
        await self.session.flush() 
        
        # 3. Создаем запись участника, используя сгенерированный project.id
        creator_member = ProjectMember(
            project_id=project.id,
            student_id=creator_student_id,
            role_in_team=creator_role
        )
        self.session.add(creator_member)
        
        # 4. Финальный коммит обеих записей одновременно
        await self.session.commit()
        await self.session.refresh(project)
        
        return project

    async def update_project(self, project: Project) -> Project:
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete_project(self, project_id: UUID) -> None:
        stmt = delete(self.model).where(self.model.id == project_id)
        await self.session.execute(stmt)
        await self.session.commit()

    # === Links ===
    async def get_link_by_id(self, project_id: UUID, link_id: UUID) -> Optional[ProjectLink]:
        stmt = select(ProjectLink).where(
            ProjectLink.id == link_id, 
            ProjectLink.project_id == project_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_project_link(self, link: ProjectLink) -> ProjectLink:
        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(link)
        return link

    async def update_project_link(self, link: ProjectLink) -> ProjectLink:
        await self.session.commit()
        await self.session.refresh(link)
        return link

    async def delete_project_link(self, project_id: UUID, link_id: UUID) -> None:
        stmt = delete(ProjectLink).where(
            ProjectLink.id == link_id,
            ProjectLink.project_id == project_id
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_all_project_links(self, project_id: UUID) -> None:
        stmt = delete(ProjectLink).where(ProjectLink.project_id == project_id)
        await self.session.execute(stmt)
        await self.session.commit()

    # === Team ===
    async def get_member_by_id(self, project_id: UUID, member_id: UUID) -> Optional[ProjectMember]:
        stmt = select(ProjectMember).where(
            ProjectMember.id == member_id, 
            ProjectMember.project_id == project_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_project_member(self, member: ProjectMember) -> ProjectMember:
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def update_project_member(self, member: ProjectMember) -> ProjectMember:
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def delete_project_member(self, project_id: UUID, member_id: UUID) -> None:
        stmt = delete(ProjectMember).where(
            ProjectMember.id == member_id, 
            ProjectMember.project_id == project_id
        )
        await self.session.execute(stmt)
        await self.session.commit()
        
    async def delete_all_project_members(self, project_id: UUID) -> None:
        """
        Удаляет всех участников (members) из проекта одним запросом.
        """
        stmt = delete(ProjectMember).where(ProjectMember.project_id == project_id)
        await self.session.execute(stmt)
        await self.session.commit()

    # === Curator ===
    async def update_project_curator(self, project_id: UUID, curator_id: UUID) -> Optional[Project]:
        project = await self.get_project_with_details(project_id)
        if project:
            project.curator_id = curator_id
            await self.session.commit()
            await self.session.refresh(project)
        return project

    async def remove_project_curator(self, project_id: UUID) -> Optional[Project]:
        project = await self.get_project_with_details(project_id)
        if project:
            # Внимание: В вашей модели curator_id имеет nullable=False. 
            # Присвоение None вызовет IntegrityError на уровне БД, 
            # если не изменить схему БД или не назначить "дефолтного" куратора.
            project.curator_id = None 
            await self.session.commit()
            await self.session.refresh(project)
        return project
    

    async def get_project_not_auth_team(self, project_id: UUID) -> List[ProjectMemberNotAuth]:
        """
        Получает список всех неавторизованных участников проекта.
        """
        stmt = select(ProjectMemberNotAuth).where(
            ProjectMemberNotAuth.project_id == project_id
        ).order_by(ProjectMemberNotAuth.created_at)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_not_auth_member_by_id(self, project_id: UUID, member_id: UUID) -> Optional[ProjectMemberNotAuth]:
        """
        Получает конкретного неавторизованного участника по ID, проверяя принадлежность к проекту.
        """
        stmt = select(ProjectMemberNotAuth).where(
            ProjectMemberNotAuth.id == member_id, 
            ProjectMemberNotAuth.project_id == project_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_project_not_auth_member(self, member: ProjectMemberNotAuth) -> ProjectMemberNotAuth:
        """
        Добавляет нового неавторизованного участника в проект.
        """
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def update_project_not_auth_member(self, member: ProjectMemberNotAuth) -> ProjectMemberNotAuth:
        """
        Обновляет данные неавторизованного участника.
        """
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def delete_project_not_auth_member(self, project_id: UUID, member_id: UUID) -> None:
        """
        Удаляет конкретного неавторизованного участника из проекта.
        Проверка project_id предотвращает случайное удаление записей из других проектов.
        """
        stmt = delete(ProjectMemberNotAuth).where(
            ProjectMemberNotAuth.id == member_id, 
            ProjectMemberNotAuth.project_id == project_id
        )
        await self.session.execute(stmt)
        await self.session.commit()
        
    async def delete_all_project_not_auth_members(self, project_id: UUID) -> None:
        """
        Удаляет всех неавторизованных участников из проекта одним запросом.
        Полезно при полном удалении проекта или очистке команды.
        """
        stmt = delete(ProjectMemberNotAuth).where(
            ProjectMemberNotAuth.project_id == project_id
        )
        await self.session.execute(stmt)
        await self.session.commit()

