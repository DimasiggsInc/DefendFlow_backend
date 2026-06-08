from typing import List, Optional, Protocol
from uuid import UUID

from src.registrations.schemas import ExpertRegistrationSchema, StudentRegistrationSchema
from src.registrations.models import ExpertRegistration, StudentRegistration



class DefenseRegistrationRepositoryPort(Protocol):
    # === Student Registration ===
    async def get_student_registrations(
        self, 
        project_id: Optional[UUID] = None,
        defense_slot_id: Optional[UUID] = None
    ) -> List[StudentRegistration]:
        """Записи команд. Фильтры: по проекту или по слоту."""
        ...

    async def get_student_registration_by_id(self, reg_id: UUID) -> Optional[StudentRegistration]:
        ...

    async def get_student_registration_with_details(self, reg_id: UUID) -> Optional[StudentRegistration]:
        """Связанные project, defense_slot, defense_room, grades, final_score."""
        ...

    async def create_student_registration(self, reg: StudentRegistration) -> StudentRegistration:
        ...

    async def update_student_registration(self, reg: StudentRegistration) -> StudentRegistration:
        ...

    async def delete_student_registration(self, reg_id: UUID) -> None:
        ...

    async def get_registrations_count_by_slot(self, slot_id: UUID) -> int:
        """Сколько проектов уже записано на слот (для проверки max_customers)."""
        ...

    # === Expert Registration ===
    async def get_expert_registrations(
        self, 
        expert_id: Optional[UUID] = None,
        defense_slot_id: Optional[UUID] = None
    ) -> List[ExpertRegistration]:
        ...

    async def get_expert_registration_by_id(self, reg_id: UUID) -> Optional[ExpertRegistration]:
        ...

    async def get_expert_registration_with_details(self, reg_id: UUID) -> Optional[ExpertRegistration]:
        """Связанные expert, defense_slot, defense_room, grades."""
        ...

    async def create_expert_registration(self, reg: ExpertRegistration) -> ExpertRegistration:
        ...

    async def update_expert_registration(self, reg: ExpertRegistration) -> ExpertRegistration:
        ...

    async def delete_expert_registration(self, reg_id: UUID) -> None:
        ...

    async def get_experts_count_by_slot(self, slot_id: UUID) -> int:
        """Сколько экспертов уже записано на слот (для проверки max_expert)."""
        ...

    async def is_expert_already_registered(self, expert_id: UUID, slot_id: UUID, room_id: UUID) -> bool:
        """Проверка дубликата записи эксперта."""
        ...


class DefenseRegistrationServicePort(Protocol):
    # === Student (Team) ===
    async def register_project_for_defense(
        self, 
        project_id: UUID, 
        slot_id: UUID, 
        room_id: UUID,
        project_member_id: UUID  # кто регистрирует (team lead)
    ) -> StudentRegistrationSchema:
        """
        Записать проект на защиту.
        Бизнес-правила:
        - Проверить, что project_member принадлежит проекту
        - Проверить, что слот не переполнен (max_customers)
        - Проверить, что проект ещё не записан на этот слот
        - Проверить, что room привязан к slot
        """
        ...

    async def get_my_project_registrations(self, user_id: UUID) -> List[StudentRegistrationSchema]:
        """Все записи проектов текущего пользователя (через student → project_member)."""
        ...

    async def get_project_registrations(self, project_id: UUID) -> List[StudentRegistrationSchema]:
        """Все записи конкретного проекта (для куратора/админа)."""
        ...

    async def get_slot_registrations(self, slot_id: UUID) -> List[StudentRegistrationSchema]:
        """Какие проекты записаны на слот (для админа/эксперта)."""
        ...

    async def cancel_student_registration(self, reg_id: UUID, user_id: UUID) -> None:
        """Отменить запись (только владелец проекта или админ)."""
        ...

    # === Expert ===
    async def register_expert_for_defense(
        self, 
        expert_id: UUID, 
        slot_id: UUID, 
        room_id: UUID,
        role: str = "expert"
    ) -> ExpertRegistrationSchema:
        """
        Записать эксперта на защиту.
        Бизнес-правила:
        - Проверить max_expert в слоте
        - Проверить, что эксперт ещё не записан на этот слот+аудиторию
        """
        ...

    async def get_my_expert_registrations(self, user_id: UUID) -> List[ExpertRegistrationSchema]:
        """Записи текущего эксперта."""
        ...

    async def get_slot_experts(self, slot_id: UUID) -> List[ExpertRegistrationSchema]:
        """Список экспертов на слоте."""
        ...

    async def cancel_expert_registration(self, reg_id: UUID, user_id: UUID) -> None:
        ...