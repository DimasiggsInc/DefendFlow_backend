from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.grading.models import Grade
from src.registrations.models import StudentRegistration, ExpertRegistration
from src.defense.models import SlotToRoom
from src.projects.models import Project, ProjectMember
from src.experts.models import Expert
from src.students.models import Student


class DefenseRegistrationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ============ STUDENT REGISTRATION ============

    async def get_student_registrations(
        self,
        project_id: Optional[UUID] = None,
        defense_slot_id: Optional[UUID] = None
    ) -> List[StudentRegistration]:
        query = (
            select(StudentRegistration)
            .options(
                # 🔥 Полная цепочка: project → members → student → user
                selectinload(StudentRegistration.project)
                    .selectinload(Project.members)
                    .selectinload(ProjectMember.student)
                    .selectinload(Student.user),
                selectinload(StudentRegistration.slot),
                selectinload(StudentRegistration.room),
                selectinload(StudentRegistration.member)
                    .selectinload(ProjectMember.student)
                    .selectinload(Student.user),
                # 🔥 Полная цепочка: grades → expert → user
                selectinload(StudentRegistration.grades)
                    .selectinload(Grade.expert)
                    .selectinload(Expert.user),
                selectinload(StudentRegistration.final_score)
            )
        )
        
        if project_id:
            query = query.where(StudentRegistration.project_id == project_id)
        if defense_slot_id:
            query = query.where(StudentRegistration.defense_slot_id == defense_slot_id)
            
        query = query.order_by(StudentRegistration.registered_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_student_registration_by_id(self, reg_id: UUID) -> Optional[StudentRegistration]:
        query = select(StudentRegistration).where(StudentRegistration.id == reg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_student_registration_with_details(self, reg_id: UUID) -> Optional[StudentRegistration]:
        """Связанные project, defense_slot, defense_room, grades, final_score."""
        query = (
            select(StudentRegistration)
            .options(
                selectinload(StudentRegistration.project),
                selectinload(StudentRegistration.slot),
                selectinload(StudentRegistration.room),
                # Используем joinedload для вложенной связи member -> student
                joinedload(StudentRegistration.member).joinedload(ProjectMember.student),
                selectinload(StudentRegistration.grades),
                selectinload(StudentRegistration.final_score)
            )
            .where(StudentRegistration.id == reg_id)
        )
        result = await self.session.execute(query)
        # unique() нужен при использовании joinedload с коллекциями
        return result.unique().scalar_one_or_none()

    async def get_student_registration_owner_user_id(self, reg_id: UUID) -> Optional[UUID]:
        """Получить user_id владельца регистрации студента для проверки прав."""
        query = (
            select(Student.user_id)
            .join(ProjectMember, Student.id == ProjectMember.student_id)
            .join(StudentRegistration, ProjectMember.id == StudentRegistration.project_member_id)
            .where(StudentRegistration.id == reg_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_student_registration(self, reg: StudentRegistration) -> StudentRegistration:
        self.session.add(reg)
        await self.session.flush()
        await self.session.refresh(reg)
        return reg

    async def update_student_registration(self, reg: StudentRegistration) -> StudentRegistration:
        self.session.add(reg)
        await self.session.flush()
        await self.session.refresh(reg)
        return reg

    async def delete_student_registration(self, reg_id: UUID) -> None:
        """Удалить запись. commit() делается на уровне сервиса/dependency."""
        query = delete(StudentRegistration).where(StudentRegistration.id == reg_id)
        await self.session.execute(query)

    async def get_registrations_count_by_slot(self, slot_id: UUID) -> int:
        """Сколько проектов уже записано на слот (для проверки max_customers)."""
        query = (
            select(func.count(StudentRegistration.id))
            .where(StudentRegistration.defense_slot_id == slot_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def is_project_already_registered_for_slot(
        self, 
        project_id: UUID, 
        slot_id: UUID
    ) -> bool:
        """Проверка дубликата записи проекта на слот."""
        query = select(StudentRegistration).where(
            StudentRegistration.project_id == project_id,
            StudentRegistration.defense_slot_id == slot_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def is_project_member_in_project(
        self, 
        project_member_id: UUID, 
        project_id: UUID
    ) -> bool:
        """Проверка, что participant принадлежит проекту."""
        query = select(ProjectMember).where(
            ProjectMember.id == project_member_id,
            ProjectMember.project_id == project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_student_registrations_by_user_id(self, user_id: UUID) -> List[StudentRegistration]:
        """Все регистрации проектов текущего пользователя (через student → project_member)."""
        query = (
            select(StudentRegistration)
            .join(ProjectMember, StudentRegistration.project_member_id == ProjectMember.id)
            .join(Student, ProjectMember.student_id == Student.id)
            .where(Student.user_id == user_id)
            .options(
                selectinload(StudentRegistration.project),
                selectinload(StudentRegistration.slot),
                selectinload(StudentRegistration.room),
                selectinload(StudentRegistration.member)
            )
            .order_by(StudentRegistration.registered_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ============ EXPERT REGISTRATION ============

    async def get_expert_registrations(
        self,
        expert_id: Optional[UUID] = None,
        defense_slot_id: Optional[UUID] = None
    ) -> List[ExpertRegistration]:
        query = (
            select(ExpertRegistration)
            .options(
                selectinload(ExpertRegistration.expert),
                selectinload(ExpertRegistration.slot),
                selectinload(ExpertRegistration.room)
            )
        )
        
        if expert_id:
            query = query.where(ExpertRegistration.expert_id == expert_id)
        if defense_slot_id:
            query = query.where(ExpertRegistration.defense_slot_id == defense_slot_id)
            
        query = query.order_by(ExpertRegistration.registered_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_expert_registration_by_id(self, reg_id: UUID) -> Optional[ExpertRegistration]:
        query = select(ExpertRegistration).where(ExpertRegistration.id == reg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_expert_registration_with_details(self, reg_id: UUID) -> Optional[ExpertRegistration]:
        """Связанные expert, defense_slot, defense_room."""
        query = (
            select(ExpertRegistration)
            .options(
                # Используем joinedload для вложенной связи expert -> user
                joinedload(ExpertRegistration.expert).joinedload(Expert.user),
                selectinload(ExpertRegistration.slot),
                selectinload(ExpertRegistration.room)
            )
            .where(ExpertRegistration.id == reg_id)
        )
        result = await self.session.execute(query)
        # unique() нужен при использовании joinedload
        return result.unique().scalar_one_or_none()

    async def get_expert_registration_owner_user_id(self, reg_id: UUID) -> Optional[UUID]:
        """Получить user_id владельца регистрации эксперта для проверки прав."""
        query = (
            select(Expert.user_id)
            .join(ExpertRegistration, Expert.id == ExpertRegistration.expert_id)
            .where(ExpertRegistration.id == reg_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_expert_registration(self, reg: ExpertRegistration) -> ExpertRegistration:
        self.session.add(reg)
        await self.session.flush()
        await self.session.refresh(reg)
        await self.session.commit()
        return reg

    async def update_expert_registration(self, reg: ExpertRegistration) -> ExpertRegistration:
        self.session.add(reg)
        await self.session.flush()
        await self.session.refresh(reg)
        await self.session.commit()
        return reg

    async def delete_expert_registration(self, reg_id: UUID) -> None:
        query = delete(ExpertRegistration).where(ExpertRegistration.id == reg_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_experts_count_by_slot(self, slot_id: UUID) -> int:
        """Сколько экспертов уже записано на слот (для проверки max_expert)."""
        query = (
            select(func.count(ExpertRegistration.id))
            .where(ExpertRegistration.defense_slot_id == slot_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def is_expert_already_registered(
        self, 
        expert_id: UUID, 
        slot_id: UUID, 
        room_id: UUID
    ) -> bool:
        """Проверка дубликата записи эксперта."""
        query = select(ExpertRegistration).where(
            ExpertRegistration.expert_id == expert_id,
            ExpertRegistration.defense_slot_id == slot_id,
            ExpertRegistration.defense_room_id == room_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def is_room_assigned_to_slot(self, slot_id: UUID, room_id: UUID) -> bool:
        """Проверка, что аудитория привязана к слоту."""
        query = select(SlotToRoom).where(
            SlotToRoom.defense_slot_id == slot_id,
            SlotToRoom.defense_room_id == room_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_expert_registrations_by_user_id(self, user_id: UUID) -> List[ExpertRegistration]:
        """Все регистрации текущего эксперта (чер Expert)."""
        query = (
            select(ExpertRegistration)
            .join(Expert, ExpertRegistration.expert_id == Expert.id)
            .where(Expert.user_id == user_id)
            .options(
                selectinload(ExpertRegistration.expert),
                selectinload(ExpertRegistration.slot),
                selectinload(ExpertRegistration.room)
            )
            .order_by(ExpertRegistration.registered_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_project_member(self, user_id: UUID, project_id: UUID) -> Optional[ProjectMember]:
        """
        Найти участника проекта по user_id и project_id.
        Использует JOIN через таблицу student.
        """
        query = (
            select(ProjectMember)
            .join(Student, ProjectMember.student_id == Student.id)
            .where(
                Student.user_id == user_id,
                ProjectMember.project_id == project_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_project_member_by_id(self, member_id: UUID) -> Optional[ProjectMember]:
        """Найти участника проекта по ID."""
        query = select(ProjectMember).where(ProjectMember.id == member_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_expert_by_user_id(self, user_id: UUID) -> Optional[Expert]:
        """
        Найти эксперта по user_id.
        У модели Expert поле user_id прямое (в отличие от Student, где нужен JOIN).
        """
        query = select(Expert).where(Expert.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()