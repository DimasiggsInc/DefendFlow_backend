# src/registrations/services.py

from typing import List
from uuid import UUID

from src.registrations.schemas import (
    StudentRegistrationSchema,
    ExpertRegistrationSchema,
    StudentRegistrationCreateRequest,
    ExpertRegistrationCreateRequest
)
from src.registrations.models import StudentRegistration, ExpertRegistration
from src.registrations.repositories import DefenseRegistrationRepository
from src.defense.repositories import DefenseSlotRepository


# ============ EXCEPTIONS ============

class DomainError(Exception):
    """Базовое исключение для бизнес-ошибок."""
    pass

class RegistrationNotFoundError(DomainError): ...
class SlotNotFoundError(DomainError): ...
class SlotFullError(DomainError): ...
class ProjectAlreadyRegisteredError(DomainError): ...
class ExpertAlreadyRegisteredError(DomainError): ...
class RoomNotAssignedToSlotError(DomainError): ...
class PermissionDeniedError(DomainError): ...
class ProjectMemberNotInProjectError(DomainError): ...
class ExpertNotFoundError(DomainError): ...


# ============ SERVICE ============

class DefenseRegistrationService:
    def __init__(
        self,
        registration_repo: DefenseRegistrationRepository,
        slot_repo: DefenseSlotRepository
    ):
        self.registration_repo = registration_repo
        self.slot_repo = slot_repo

    # ============ STUDENT (TEAM) REGISTRATION ============

    async def register_project_for_defense(
        self,
        project_id: UUID,
        slot_id: UUID,
        room_id: UUID,
        user_id: UUID  # вместо project_member_id передаем user_id
    ) -> StudentRegistrationSchema:
        """
        Записать проект на защиту.
        Бизнес-правила:
        - Найти project_member по user_id и project_id
        - Проверить, что слот не переполнен (max_customers)
        - Проверить, что проект ещё не записан на этот слот
        - Проверить, что room привязан к slot
        """
        # 1. Найти project_member (участник должен быть в проекте)
        project_member = await self.registration_repo.get_project_member(user_id, project_id)
        if not project_member:
            raise ProjectMemberNotInProjectError(
                f"Пользователь {user_id} не является участником проекта {project_id}"
            )

        # 2. Проверить существование слота
        slot = await self.slot_repo.get_slot_by_id(slot_id)
        if not slot:
            raise SlotNotFoundError(f"Слот с ID {slot_id} не найден")

        # 3. Проверить, что room привязан к slot
        if not await self.registration_repo.is_room_assigned_to_slot(slot_id, room_id):
            raise RoomNotAssignedToSlotError(
                f"Аудитория {room_id} не привязана к слоту {slot_id}"
            )

        # 4. Проверить, что проект ещё не записан на этот слот
        if await self.registration_repo.is_project_already_registered_for_slot(
            project_id, slot_id
        ):
            raise ProjectAlreadyRegisteredError(
                f"Проект {project_id} уже записан на слот {slot_id}"
            )

        # 5. Проверить max_customers
        count = await self.registration_repo.get_registrations_count_by_slot(slot_id)
        if count >= slot.max_customers:
            raise SlotFullError(
                f"Слот {slot_id} переполнен (максимум {slot.max_customers} проектов)"
            )

        # 6. Создать запись
        reg = StudentRegistration(
            project_id=project_id,
            project_member_id=project_member.id,  # используем найденный member
            defense_slot_id=slot_id,
            defense_room_id=room_id
        )
        created_reg = await self.registration_repo.create_student_registration(reg)
        
        # Загрузить детали для схемы
        reg_with_details = await self.registration_repo.get_student_registration_with_details(
            created_reg.id
        )
        return self._to_student_schema(reg_with_details)

    async def get_my_project_registrations(self, user_id: UUID) -> List[StudentRegistrationSchema]:
        """Все записи проектов текущего пользователя (через student → project_member)."""
        regs = await self.registration_repo.get_student_registrations_by_user_id(user_id)
        return [self._to_student_schema(reg) for reg in regs]

    async def get_project_registrations(self, project_id: UUID) -> List[StudentRegistrationSchema]:
        """Все записи конкретного проекта (для куратора/админа)."""
        regs = await self.registration_repo.get_student_registrations(project_id=project_id)
        return [self._to_student_schema(reg) for reg in regs]

    async def get_slot_registrations(self, slot_id: UUID) -> List[StudentRegistrationSchema]:
        """Какие проекты записаны на слот (для админа/эксперта)."""
        regs = await self.registration_repo.get_student_registrations(defense_slot_id=slot_id)
        return [self._to_student_schema(reg) for reg in regs]

    async def cancel_student_registration(self, reg_id: UUID, user_id: UUID) -> None:
        """Отменить запись (только владелец проекта или админ)."""
        reg = await self.registration_repo.get_student_registration_with_details(reg_id)
        if not reg:
            raise RegistrationNotFoundError(f"Регистрация с ID {reg_id} не найдена")

        # Проверить, что пользователь - владелец (через project_member -> student -> user_id)
        # member.student загружается через selectinload в репозитории
        if reg.member.student.user_id != user_id:
            raise PermissionDeniedError(
                "Только владелец проекта может отменить регистрацию"
            )

        await self.registration_repo.delete_student_registration(reg_id)

    # ============ EXPERT REGISTRATION ============

    async def register_expert_for_defense(
        self,
        user_id: UUID,  # вместо expert_id передаем user_id
        slot_id: UUID,
        room_id: UUID,
        role: str = "expert"
    ) -> ExpertRegistrationSchema:
        """
        Записать эксперта на защиту.
        Бизнес-правила:
        - Найти expert по user_id
        - Проверить max_expert в слоте
        - Проверить, что эксперт ещё не записан на этот слот+аудиторию
        """
        # 1. Найти эксперта по user_id
        expert = await self.registration_repo.get_expert_by_user_id(user_id)
        if not expert:
            raise ExpertNotFoundError(
                f"Пользователь {user_id} не является экспертом"
            )

        # 2. Проверить существование слота
        slot = await self.slot_repo.get_slot_by_id(slot_id)
        if not slot:
            raise SlotNotFoundError(f"Слот с ID {slot_id} не найден")

        # 3. Проверить, что room привязан к slot
        if not await self.registration_repo.is_room_assigned_to_slot(slot_id, room_id):
            raise RoomNotAssignedToSlotError(
                f"Аудитория {room_id} не привязана к слоту {slot_id}"
            )

        # 4. Проверить дубликат
        if await self.registration_repo.is_expert_already_registered(
            expert.id, slot_id, room_id
        ):
            raise ExpertAlreadyRegisteredError(
                f"Эксперт уже записан на слот {slot_id} в аудиторию {room_id}"
            )

        # 5. Проверить max_expert
        count = await self.registration_repo.get_experts_count_by_slot(slot_id)
        if count >= slot.max_expert:
            raise SlotFullError(
                f"Слот {slot_id} переполнен (максимум {slot.max_expert} экспертов)"
            )

        # 6. Создать запись
        reg = ExpertRegistration(
            expert_id=expert.id,
            defense_slot_id=slot_id,
            defense_room_id=room_id,
            role_at_registration=role
        )
        created_reg = await self.registration_repo.create_expert_registration(reg)
        
        # Загрузить детали для схемы
        reg_with_details = await self.registration_repo.get_expert_registration_with_details(
            created_reg.id
        )
        return self._to_expert_schema(reg_with_details)

    async def get_my_expert_registrations(self, user_id: UUID) -> List[ExpertRegistrationSchema]:
        """Записи текущего эксперта."""
        regs = await self.registration_repo.get_expert_registrations_by_user_id(user_id)
        return [self._to_expert_schema(reg) for reg in regs]

    async def get_slot_experts(self, slot_id: UUID) -> List[ExpertRegistrationSchema]:
        """Список экспертов на слоте."""
        regs = await self.registration_repo.get_expert_registrations(defense_slot_id=slot_id)
        return [self._to_expert_schema(reg) for reg in regs]

    async def cancel_expert_registration(self, reg_id: UUID, user_id: UUID) -> None:
        """Отменить запись эксперта."""
        # Проверяем существование регистрации
        reg = await self.registration_repo.get_expert_registration_by_id(reg_id)
        if not reg:
            raise RegistrationNotFoundError(f"Регистрация с ID {reg_id} не найдена")

        # Получаем user_id владельца через отдельный запрос (эффективнее)
        owner_user_id = await self.registration_repo.get_expert_registration_owner_user_id(reg_id)
        if owner_user_id != user_id:
            raise PermissionDeniedError(
                "Только владелец эксперта может отменить регистрацию"
            )

        await self.registration_repo.delete_expert_registration(reg_id)

    # ============ HELPER METHODS ============

    def _to_student_schema(self, reg: StudentRegistration) -> StudentRegistrationSchema:
        """Конвертация модели в схему с заполнением project_name."""
        schema = StudentRegistrationSchema.model_validate(reg)
        schema.project_name = reg.project.name if reg.project else None
        return schema

    def _to_expert_schema(self, reg: ExpertRegistration) -> ExpertRegistrationSchema:
        """Конвертация модели в схему с заполнением expert_name."""
        schema = ExpertRegistrationSchema.model_validate(reg)
        # Предполагаем, что у Expert есть поле full_name или name
        if hasattr(reg.expert, 'full_name'):
            schema.expert_name = reg.expert.full_name
        elif hasattr(reg.expert, 'name'):
            schema.expert_name = reg.expert.name
        else:
            schema.expert_name = None
        return schema
