from typing import List, Optional, Protocol
from uuid import UUID
from src.protocols.schemas import FinalScoreSchema, GradeSchema, ProtocolSchema
from src.protocols.models import Protocol as Protocol_model
from src.grading.models import FinalScore, Grade


class DefenseProtocolRepositoryPort(Protocol):
    async def get_protocols_by_slot(self, slot_id: UUID) -> List[Protocol_model]:
        ...

    async def get_protocol_by_id(self, protocol_id: UUID) -> Optional[Protocol_model]:
        ...

    async def create_protocol(self, protocol: Protocol_model) -> Protocol_model:
        ...

    async def update_protocol_pdf(self, protocol_id: UUID, pdf_url: str) -> Protocol_model:
        ...

    # === Grades ===
    async def get_grades_by_registration(self, registration_id: UUID) -> List[Grade]:
        ...

    async def get_grades_by_expert(self, expert_id: UUID) -> List[Grade]:
        ...

    async def create_grade(self, grade: Grade) -> Grade:
        ...

    async def update_grade(self, grade: Grade) -> Grade:
        ...

    # === Final Score ===
    async def get_final_score_by_registration(self, registration_id: UUID) -> Optional[FinalScore]:
        ...

    async def create_or_update_final_score(self, registration_id: UUID, total_score: float) -> FinalScore:
        """Пересчитывает итоговый балл по среднему/взвешенному."""
        ...


class DefenseProtocolServicePort(Protocol):
    async def get_slot_protocols(self, slot_id: UUID) -> List[ProtocolSchema]:
        ...

    async def create_protocol(
        self, 
        admin_id: UUID, 
        slot_id: UUID, 
        room_id: UUID
    ) -> ProtocolSchema:
        ...

    async def upload_protocol_pdf(self, protocol_id: UUID, pdf_url: str) -> ProtocolSchema:
        ...

    async def submit_grade(
        self, 
        expert_id: UUID, 
        registration_id: UUID, 
        score: float, 
        text_questions: Optional[str] = None
    ) -> GradeSchema:
        """
        Поставить оценку.
        Бизнес-правила:
        - Эксперт должен быть записан на этот слот
        - Оценка в допустимом диапазоне (0-100)
        - Нельзя оценить дважды
        """
        ...

    async def get_registration_grades(self, registration_id: UUID) -> List[GradeSchema]:
        """Все оценки команды (для просмотра студентом/куратором)."""
        ...

    async def get_registration_final_score(self, registration_id: UUID) -> FinalScoreSchema:
        """Итоговый балл (пересчитывается автоматически после каждой оценки)."""
        ...

    async def recalculate_final_score(self, registration_id: UUID) -> FinalScoreSchema:
        """Явный пересчёт итога (например, после удаления оценки)."""
        ...