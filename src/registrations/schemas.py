from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from src.protocols.schemas import FinalScoreSchema, GradeSchema


class StudentRegistrationSchema(BaseModel):
    id: UUID
    project_member_id: UUID
    project_id: UUID
    project_name: Optional[str] = None
    defense_slot_id: UUID
    defense_room_id: UUID
    registered_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentRegistrationCreateRequest(BaseModel):
    project_id: UUID
    defense_slot_id: UUID
    defense_room_id: UUID
    # project_member_id: UUID


# ============ EXPERT REGISTRATION ============

class ExpertRegistrationSchema(BaseModel):
    id: UUID
    expert_id: UUID
    expert_name: Optional[str] = None
    defense_slot_id: UUID
    defense_room_id: UUID
    role_at_registration: str = "expert"
    registered_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpertRegistrationCreateRequest(BaseModel):
    # expert_id: UUID
    defense_slot_id: UUID
    defense_room_id: UUID
    role_at_registration: str = Field(default="expert", pattern="^(expert|consultant|reviewer)$")

class RegistrationWithGradesSchema(StudentRegistrationSchema):
    """
    Расширенная схема записи студента с оценками и итоговым баллом.
    Используется в эндпоинте GET /defense/registrations/student/{reg_id}.
    """
    grades: List[GradeSchema] = []
    final_score: Optional[FinalScoreSchema] = None
