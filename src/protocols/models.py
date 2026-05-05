import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    UUID, String, DateTime, func, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.admins.models import Admin
    from src.defense.models import DefenseRoom, DefenseSlot



class Protocol(Base):
    """Протокол защиты."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admin.id"), nullable=False)
    defense_slot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("defense_slot.id"), nullable=False)
    defense_room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("defense_room.id"), nullable=False)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


    admin: Mapped["Admin"] = relationship("Admin", back_populates="protocols")
    slot: Mapped["DefenseSlot"] = relationship("DefenseSlot", back_populates="protocols")
    room: Mapped["DefenseRoom"] = relationship("DefenseRoom", back_populates="protocols")
