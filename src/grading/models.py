import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import (
    UUID, String, DateTime, func, ForeignKey, Text, Integer, Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base  # Ваш базовый класс

# Импорты для TYPE_CHECKING, чтобы избежать циклических импортов
if TYPE_CHECKING:
    from src.users.models import User
    from src.students.models import Student
    from src.experts.models import Expert
    # from src.admins.models import 
    from src.projects.models import ProjectMember, Project
    
    from src.defense.models import DefenseRoom, DefenseSlot
    from src.registrations.models import StudentRegistration


class Grade(Base):
    """Оценка от эксперта за регистрацию (студента)."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expert_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expert.id"), nullable=False)
    student_registration_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("student_registration.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    text_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


    expert: Mapped["Expert"] = relationship("Expert", back_populates="grades")
    student_registration: Mapped["StudentRegistration"] = relationship("StudentRegistration", back_populates="grades")


class FinalScore(Base):
    """Итоговая оценка."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_registration_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("student_registration.id"), nullable=False, unique=True)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    calculated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


    registration: Mapped["StudentRegistration"] = relationship("StudentRegistration", back_populates="final_score")
