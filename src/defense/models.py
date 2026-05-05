from asyncio import Protocol
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    UUID, String, DateTime, func, ForeignKey, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base  # Ваш базовый класс

# Импорты для TYPE_CHECKING, чтобы избежать циклических импортов
if TYPE_CHECKING:
    from src.admins.models import Admin
    from src.registrations.models import ExpertRegistration, StudentRegistration


class DefenseSlot(Base):
    """Временной слот для защиты."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    time_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    time_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    max_expert: Mapped[int] = mapped_column(Integer, nullable=False)
    max_customers: Mapped[int] = mapped_column(Integer, nullable=False)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


    slot_to_rooms: Mapped[List["SlotToRoom"]] = relationship("SlotToRoom", back_populates="slot")
    protocols: Mapped[List["Protocol"]] = relationship("Protocol", back_populates="slot")
    student_registrations: Mapped[List["StudentRegistration"]] = relationship("StudentRegistration", back_populates="slot")
    expert_registrations: Mapped[List["ExpertRegistration"]] = relationship("ExpertRegistration", back_populates="slot")


class DefenseRoom(Base):
    """Аудитория для защиты."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    admin_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admin.id"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


    admin: Mapped["Admin"] = relationship("Admin", back_populates="rooms")
    slot_to_rooms: Mapped[List["SlotToRoom"]] = relationship("SlotToRoom", back_populates="room")
    protocols: Mapped[List["Protocol"]] = relationship("Protocol", back_populates="room")
    student_registrations: Mapped[List["StudentRegistration"]] = relationship("StudentRegistration", back_populates="room")
    expert_registrations: Mapped[List["ExpertRegistration"]] = relationship("ExpertRegistration", back_populates="room")


class SlotToRoom(Base):
    """Связь слота и комнаты."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    defense_slot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("defense_slot.id"), nullable=False)
    defense_room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("defense_room.id"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Отношения
    slot: Mapped["DefenseSlot"] = relationship("DefenseSlot", back_populates="slot_to_rooms")
    room: Mapped["DefenseRoom"] = relationship("DefenseRoom", back_populates="slot_to_rooms")
