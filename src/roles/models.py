# src/roles/models.py (или добавьте в src/models_hub.py)
from sqlalchemy import Column, Enum, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models_hub import Base
from src.users.schemas import UserRolesEnum  # Замените на ваш реальный импорт DeclarativeBase


class UserRole(Base):
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    
    role_name = Column(
        Enum(UserRolesEnum, name="user_role_enum"),
        primary_key=True,
        nullable=False
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship("User", back_populates="roles")

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role={self.role_name})>"
