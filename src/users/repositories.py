from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID

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
    
    # TODO: Сделать передачу SQLAlchemy модели в репо
    async def update_user(self, user_id: UUID, **kwargs) -> User:
        allowed_fields = {"first_name", "last_name", "middle_name", "email"}
        clean_data = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if clean_data:
            old_email = None
            if "email" in clean_data:
                res = await self.session.execute(select(User.email).where(User.id == user_id))
                old_email = res.scalar_one_or_none()

            await self.session.execute(
                update(User).where(User.id == user_id).values(**clean_data)
            )
            await self.session.commit()

            await cache.delete(CacheKeys.user_profile(user_id))
            if old_email:
                await cache.delete(CacheKeys.user_by_email(old_email))
                await cache.delete(CacheKeys.user_by_email(clean_data["email"]))

        load_opts = RoleRegistry.get_load_options()
        stmt = select(User).where(User.id == user_id).options(*load_opts)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError(f"User with id {user_id} not found after update")

        return user

    # TODO: Сделать передачу SQLAlchemy модели в репо
    async def update_profile(self, user_id: UUID, profile_type: str, **kwargs) -> Any:
        profile_models = {
            UserRolesEnum.CURATOR: Curator,
            UserRolesEnum.ADMIN: Admin,
            UserRolesEnum.EXPERT: Expert,
            UserRolesEnum.STUDENT: Student,
        }
        ProfileModel = profile_models.get(profile_type)
        if not ProfileModel:
            raise ValueError(f"Unknown profile type: {profile_type}")

        result = await self.session.execute(select(ProfileModel).where(ProfileModel.user_id == user_id))
        profile = result.scalar_one_or_none()

        if profile:
            allowed = {c.key for c in ProfileModel.__table__.columns} - {"id", "user_id", "created_at", "updated_at"}
            clean_data = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
            if clean_data:
                await self.session.execute(
                    update(ProfileModel).where(ProfileModel.id == profile.id).values(**clean_data)
                )
        else:
            profile = ProfileModel(user_id=user_id, **{k: v for k, v in kwargs.items() if k in ProfileModel.__table__.columns})
            self.session.add(profile)

        await self.session.commit()
        await self.session.refresh(profile)

        await cache.delete(CacheKeys.user_profile(user_id))

        return profile
