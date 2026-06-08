from datetime import time, datetime
from datetime import date as date_
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from src.registrations.schemas import ExpertRegistrationSchema, StudentRegistrationSchema



# ============ DEFENSE SLOT ============

class DefenseSlotSchema(BaseModel):
    id: UUID
    date: date_
    time_start: time
    time_end: time
    max_expert: int
    max_customers: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DefenseSlotFullSchema(DefenseSlotSchema):
    rooms: List["DefenseRoomSchema"] = []
    registered_projects_count: int = 0
    registered_experts_count: int = 0


class DefenseSlotCreateRequest(BaseModel):
    date: date_
    time_start: time
    time_end: time
    max_expert: int = Field(ge=1, default=5)
    max_customers: int = Field(ge=1, default=10)


class DefenseSlotUpdateRequest(BaseModel):
    date: Optional[date_] = None
    time_start: Optional[time] = None
    time_end: Optional[time] = None
    max_expert: Optional[int] = Field(None, ge=1)
    max_customers: Optional[int] = Field(None, ge=1)


# ============ DEFENSE ROOM ============

class DefenseRoomSchema(BaseModel):
    id: UUID
    name: str
    admin_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DefenseRoomCreateRequest(BaseModel):
    name: str
    admin_id: Optional[UUID] = None


class DefenseRoomUpdateRequest(BaseModel):
    name: Optional[str] = None
    admin_id: Optional[UUID] = None


# ============ SLOT TO ROOM ============

class SlotToRoomSchema(BaseModel):
    id: UUID
    defense_slot_id: UUID
    defense_room_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DefenseSlotWithRegistrationsSchema(DefenseSlotFullSchema):
    """
    Расширенная схема слота с информацией о записанных проектах и экспертах.
    Используется в эндпоинте GET /defense/slots/{slot_id}.
    """
    student_registrations: List[StudentRegistrationSchema] = []
    expert_registrations: List[ExpertRegistrationSchema] = []