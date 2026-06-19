# src/grading/repositories.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.grading.models import Grade, FinalScore
from src.protocols.models import Protocol
from src.registrations.models import ExpertRegistration, StudentRegistration
from src.experts.models import Expert
from src.admins.models import Admin
from src.defense.models import DefenseSlot, DefenseRoom, SlotToRoom


# [
#   {
#     "id": "355c6147-06bf-4eca-b691-19427d130e29",
#     "expert_id": "c12dd185-7b14-4b39-ac3d-0c76409c7b81",
#     "expert_name": null,
#     "defense_slot_id": "4eed4cb7-476c-41e2-8478-741f359f5ff6",
#     "defense_room_id": "7cf1293f-2189-4f94-94b1-4885be616036",
#     "role_at_registration": "expert",
#     "registered_at": "2026-06-19T10:00:02.699819",
#     "created_at": "2026-06-19T10:00:02.699819",
#     "updated_at": "2026-06-19T10:00:02.699819"
#   }
# ]






class GradeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_available_student_registrations_for_expert(
        self, expert_id: UUID
    ) -> List[StudentRegistration]:
        """
        Получить проекты на защитах, где зарегистрирован эксперт,
        исключая те, которым эксперт уже поставил оценку.
        """
        # Подзапрос: слоты и комнаты, где зарегистрирован эксперт
        expert_slots_subq = (
            select(
                ExpertRegistration.defense_slot_id, 
                ExpertRegistration.defense_room_id
            )
            .where(ExpertRegistration.expert_id == expert_id)
            .subquery()
        )

        # Основной запрос: StudentRegistration + Left Join Grade
        stmt = (
            select(StudentRegistration)
            .join(
                expert_slots_subq,
                (StudentRegistration.defense_slot_id == expert_slots_subq.c.defense_slot_id) &
                (StudentRegistration.defense_room_id == expert_slots_subq.c.defense_room_id)
            )
            .outerjoin(
                Grade,
                (Grade.student_registration_id == StudentRegistration.id) &
                (Grade.expert_id == expert_id)
            )
            .where(Grade.id.is_(None))  # Оставляем только те, где оценки НЕТ
            .options(
                selectinload(StudentRegistration.project),
                selectinload(StudentRegistration.slot),
                selectinload(StudentRegistration.room)
            )
            .distinct() # На случай, если эксперт зарегистрирован в одной комнате несколько раз (защита от дублей)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_student_registration_by_id(
        self, reg_id: UUID
    ) -> Optional[StudentRegistration]:
        """Получить запись проекта на защиту со связями."""
        query = (
            select(StudentRegistration)
            .options(
                selectinload(StudentRegistration.project),
                selectinload(StudentRegistration.slot),
                selectinload(StudentRegistration.room)
            )
            .where(StudentRegistration.id == reg_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_expert_registration_by_expert_and_slot_room(
        self, expert_id: UUID, slot_id: UUID, room_id: UUID
    ) -> Optional[ExpertRegistration]:
        """
        Проверить, что эксперт зарегистрирован на этот же слот+комнату.
        Возвращает запись эксперта, если она существует.
        """
        query = select(ExpertRegistration).where(
            ExpertRegistration.expert_id == expert_id,
            ExpertRegistration.defense_slot_id == slot_id,
            ExpertRegistration.defense_room_id == room_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def is_expert_already_graded(
        self, expert_id: UUID, student_registration_id: UUID
    ) -> bool:
        """Проверка, что эксперт уже поставил оценку этой регистрации."""
        query = select(Grade).where(
            Grade.expert_id == expert_id,
            Grade.student_registration_id == student_registration_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def create_grade(self, grade: Grade) -> Grade:
        self.session.add(grade)
        await self.session.flush()
        await self.session.refresh(grade)
        await self.session.commit()
        return grade

    async def get_grade_by_id(self, grade_id: UUID) -> Optional[Grade]:
        query = (
            select(Grade)
            .options(selectinload(Grade.expert).selectinload(Expert.user))
            .where(Grade.id == grade_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_grade(self, grade: Grade) -> Grade:
        self.session.add(grade)
        await self.session.flush()
        await self.session.refresh(grade)
        await self.session.commit()
        return grade

    async def get_grades_by_registration(
        self, registration_id: UUID
    ) -> List[Grade]:
        query = (
            select(Grade)
            .options(selectinload(Grade.expert).selectinload(Expert.user))
            .where(Grade.student_registration_id == registration_id)
            .order_by(Grade.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_grades_by_expert(self, expert_id: UUID) -> List[Grade]:
        """Получить все оценки эксперта."""
        query = (
            select(Grade)
            .options(
                selectinload(Grade.student_registration),
                selectinload(Grade.expert).selectinload(Expert.user)
            )
            .where(Grade.expert_id == expert_id)
            .order_by(Grade.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class FinalScoreRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_final_score_by_registration(
        self, registration_id: UUID
    ) -> Optional[FinalScore]:
        query = select(FinalScore).where(
            FinalScore.student_registration_id == registration_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_final_score(self, score: FinalScore) -> FinalScore:
        self.session.add(score)
        await self.session.flush()
        await self.session.refresh(score)
        await self.session.commit()
        return score

    async def update_final_score(self, score: FinalScore) -> FinalScore:
        self.session.add(score)
        await self.session.flush()
        await self.session.refresh(score)
        await self.session.commit()
        return score

    async def delete_final_score(self, registration_id: UUID) -> None:
        query = delete(FinalScore).where(
            FinalScore.student_registration_id == registration_id
        )
        await self.session.execute(query)
        await self.session.commit()


class ProtocolRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_protocol_by_id(self, protocol_id: UUID) -> Optional[Protocol]:
        query = (
            select(Protocol)
            .options(
                selectinload(Protocol.slot),
                selectinload(Protocol.room)
            )
            .where(Protocol.id == protocol_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_protocols_by_slot(self, slot_id: UUID) -> List[Protocol]:
        """Получить все протоколы слота."""
        query = (
            select(Protocol)
            .options(
                selectinload(Protocol.slot),
                selectinload(Protocol.room)
            )
            .where(Protocol.defense_slot_id == slot_id)
            .order_by(Protocol.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_protocol(self, protocol: Protocol) -> Protocol:
        self.session.add(protocol)
        await self.session.flush()
        await self.session.refresh(protocol)
        await self.session.commit()
        return protocol

    async def update_protocol(self, protocol: Protocol) -> Protocol:
        self.session.add(protocol)
        await self.session.flush()
        await self.session.refresh(protocol)
        await self.session.commit()
        return protocol

    async def delete_protocol(self, protocol_id: UUID) -> None:
        query = delete(Protocol).where(Protocol.id == protocol_id)
        await self.session.execute(query)
        await self.session.commit()

    async def is_room_assigned_to_slot(
        self, slot_id: UUID, room_id: UUID
    ) -> bool:
        """Проверка, что аудитория привязана к слоту."""
        query = select(SlotToRoom).where(
            SlotToRoom.defense_slot_id == slot_id,
            SlotToRoom.defense_room_id == room_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_admin_by_user_id(self, user_id: UUID) -> Optional[Admin]:
        """Найти админа по user_id."""
        query = select(Admin).where(Admin.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_admin_by_id(self, admin_id: UUID) -> Optional[Admin]:
        """Найти админа по ID с загруженным user."""
        query = (
            select(Admin)
            .options(
                selectinload(Admin.user)  # 🔥 Загружаем user
            )
            .where(Admin.id == admin_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()