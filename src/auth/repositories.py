from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from uuid import UUID

from src.repositories import BaseRepository
from src.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.auth.interfaces import AuthRepositoryPort
from src.models_hub import User
from src.cache import cache



# TODO: Перенести в UserRepo
class AuthRepository(BaseRepository, AuthRepositoryPort):
    def __init__(self, model: type[User], session: AsyncSession):
        self.model = model
        self.session = session

    @cache(ttl="5m", key="user_id:{user_email}")
    async def get_by_email(self, user_email: str) -> User:
        res = await self.session.execute(select(self.model).where(self.model.email == user_email))
        return res.scalar_one_or_none()
