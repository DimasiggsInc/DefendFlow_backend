"""Схемы для проектов."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from pydantic import Field



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
    expert_id: UUID
    student_registration_id: UUID
    score: float = Field(ge=0, le=100)
    text_questions: Optional[str] = None


class GradeUpdateRequest(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    text_questions: Optional[str] = None


# ============ FINAL SCORE ============

class FinalScoreSchema(BaseModel):
    id: UUID
    student_registration_id: UUID
    total_score: float
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ PROTOCOL ============

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
    admin_id: UUID
    defense_slot_id: UUID
    defense_room_id: UUID


class ProtocolPdfUpdateRequest(BaseModel):
    pdf_url: str