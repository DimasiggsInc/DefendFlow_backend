from typing import Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID

from src.models_hub import UserRole
from src.admins.models import Admin
from src.curators.models import Curator
from src.experts.models import Expert
from src.students.models import Student
from src.repositories import BaseRepository
from src.users.interfaces import UserRepositoryPort
from src.models_hub import User
from src.cache import cache, CacheKeys
from src.users.registry import RoleRegistry
from src.users.schemas import UserRolesEnum



class UserRepository(BaseRepository, UserRepositoryPort):
    def __init__(self, model: type[User], session: AsyncSession):
        self.model = model
        self.session = session

    @cache(ttl="5m", key=CacheKeys.USER_BY_EMAIL)  # "user_id:{user_email}"
    async def get_by_email(self, user_email: str) -> User:
        res = await self.session.execute(select(self.model).where(self.model.email == user_email))
        return res.scalar_one_or_none()

    async def email_exists(self, user_email: str) -> User:
        res = await self.session.execute(select(self.model).where(self.model.email == user_email))
        return res.scalar_one_or_none() is not None

    @cache(ttl="5m", key=CacheKeys.USER_PROFILE)  # "user_profile:{user_id}"
    async def get_user_with_profiles(self, user_id: UUID) -> User | None:
        load_opts = RoleRegistry.get_load_options()
        
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(*load_opts)
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    @cache(ttl="5m", key=CacheKeys.USER_ROLES)  # "user_roles:{user_id}"
    async def get_roles(self, user_id: UUID) -> List[UserRolesEnum]:
        stmt = select(UserRole.role_name).where(UserRole.user_id == user_id)
        result = await self.session.execute(stmt)
        
        return [UserRolesEnum(role_str) for role_str, in result.fetchall()]
    
    async def update_partial(self, user_id: UUID, update_data: dict[str, str]) -> "User | None":
        result = await self.session.execute(
            select(self.model).where(self.model.id == user_id).with_for_update()
        )
        user = result.scalar_one_or_none()
        if not user:
            return None

        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        await cache.delete(CacheKeys.user_by_email(user.email))
        await cache.delete(CacheKeys.user_profile(user_id))
        return user
