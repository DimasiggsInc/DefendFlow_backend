"""Схемы для проектов."""

from datetime import datetime, time, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from pydantic import Field



class AvailableProjectForGradingResponse(BaseModel):
    """Проект, которому эксперт ещё не поставил оценку."""
    student_registration_id: UUID
    project_id: UUID
    project_name: str
    defense_date: date
    defense_time_start: time
    room_name: str

    class Config:
        from_attributes = True


class GradeSchema(BaseModel):
    id: UUID
    expert_id: UUID
    expert_name: Optional[str] = None
    student_registration_id: UUID
    score: float = Field(ge=0, le=100)
    text_questions: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GradeCreateRequest(BaseModel):
    student_registration_id: UUID  # Запись эксперта на защиту
    score: float = Field(ge=0, le=100)
    text_questions: Optional[str] = None
    # student_registration_id и expert_id убраны - определяются автоматически


class GradeUpdateRequest(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    text_questions: Optional[str] = None


class FinalScoreSchema(BaseModel):
    id: UUID
    student_registration_id: UUID
    total_score: float
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProtocolSchema(BaseModel):
    id: UUID
    admin_id: UUID
    defense_slot_id: UUID
    defense_room_id: UUID
    pdf_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProtocolCreateRequest(BaseModel):
    defense_slot_id: UUID
    defense_room_id: UUID
    # admin_id убран - берется из токена


class ProtocolPdfUpdateRequest(BaseModel):
    pdf_url: str