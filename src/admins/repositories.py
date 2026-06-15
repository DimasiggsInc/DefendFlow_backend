from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.admins.models import Admin


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_admin_by_user_id(self, user_id: UUID) -> Optional[Admin]:
        """Найти админа по user_id."""
        query = select(Admin).where(Admin.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
