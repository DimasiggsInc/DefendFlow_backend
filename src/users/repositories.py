
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.repositories import BaseRepository
from src.users.interfaces import UserRepositoryPort
from src.models_hub import User
from src.cache import cache
from src.users.registry import RoleRegistry



# TODO: Перенести в UserRepo
class UserRepository(BaseRepository, UserRepositoryPort):
    def __init__(self, model: type[User], session: AsyncSession):
        self.model = model
        self.session = session

    @cache(ttl="5m", key="user_id:{user_email}")
    async def get_by_email(self, user_email: str) -> User:
        res = await self.session.execute(select(self.model).where(self.model.email == user_email))
        return res.scalar_one_or_none()

    async def email_exists(self, user_email: str) -> User:
        res = await self.session.execute(select(self.model).where(self.model.email == user_email))
        return not res.scalar_one_or_none() is None


    async def get_user_with_profiles(self, user_id: UUID) -> User | None:
        # ✅ Репозиторий динамически формирует JOIN-ы через реестр
        load_opts = RoleRegistry.get_load_options()
        
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(*load_opts)
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
