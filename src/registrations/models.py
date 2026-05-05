import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import (
    UUID, String, DateTime, func, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


from src.database import Base  # Ваш базовый класс

# Импорты для TYPE_CHECKING, чтобы избежать циклических импортов
if TYPE_CHECKING:
    from src.experts.models import Expert
    # from src.admins.models import 
    from src.projects.models import ProjectMember, Project
    from src.grading.models import Grade
    from src.defense.models import DefenseRoom, DefenseSlot
    from src.grading.models import FinalScore




class StudentRegistration(Base):
    """Регистрация команды/студента на защиту."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project_member.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    defense_slot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("defense_slot.id"), nullable=False)
    defense_room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("defense_room.id"), nullable=False)
    
    registered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Отношения
    member: Mapped["ProjectMember"] = relationship("ProjectMember", back_populates="registrations")
    project: Mapped["Project"] = relationship("Project", back_populates="student_registrations")
    slot: Mapped["DefenseSlot"] = relationship("DefenseSlot", back_populates="student_registrations")
    room: Mapped["DefenseRoom"] = relationship("DefenseRoom", back_populates="student_registrations")
    
    grades: Mapped[List["Grade"]] = relationship("Grade", back_populates="student_registration")
    final_score: Mapped[Optional["FinalScore"]] = relationship("FinalScore", back_populates="registration", uselist=False)


class ExpertRegistration(Base):
    """Регистрация эксперта на слот защиты."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expert_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expert.id"), nullable=False)
    defense_slot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("defense_slot.id"), nullable=False)
    defense_room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("defense_room.id"), nullable=False)
    role_at_registration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    registered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Отношения
    expert: Mapped["Expert"] = relationship("Expert", back_populates="registrations")
    slot: Mapped["DefenseSlot"] = relationship("DefenseSlot", back_populates="expert_registrations")
    room: Mapped["DefenseRoom"] = relationship("DefenseRoom", back_populates="expert_registrations")
