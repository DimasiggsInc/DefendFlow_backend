from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from uuid import UUID

from src.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.auth.interfaces import AuthRepositoryPort
from src.models_hub import User
from src.cache import cache

from src.users.schemas import UserSchemaFull



# TODO: Перенести в UserRepo
class AuthRepository(AuthRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, email: str, hashed_password: str, salt: str) -> UUID:
        db_user = User(email=email, hashed_password=hashed_password, salt=salt)
        self.session.add(db_user)

        try:
            await self.session.commit()
            await self.session.refresh(db_user)

            return db_user.id
        except IntegrityError:
            await self.session.rollback()
            raise UserAlreadyExistsError()

    @cache(ttl="5m", key="user_id:{user_email}")
    async def get_id_by_email(self, user_email: str) -> UUID:
        query = (
            select(User)
            .where(User.email == user_email)
        )
        res = await self.session.execute(query)
        
        try:
            user = res.scalars().one()
        except Exception:
            raise UserNotFoundError()

        return user.id

    @cache(ttl="5m", key="user_hashed_password:{user_id}")
    async def get_user_hashed_password(self, user_id: UUID) -> str:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        res = await self.session.execute(query)
        
        user = res.scalars().one()

        return user.hashed_password
    
    @cache(ttl="5m", key="user_salt:{user_id}")
    async def get_user_salt(self, user_id: UUID) -> str:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        res = await self.session.execute(query)
        
        user = res.scalars().one()

        return user.salt
    
    @cache(ttl="5m", key="user_email:{user_id}")
    async def get_email(self, user_id: UUID) -> str:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        res = await self.session.execute(query)
        
        user = res.scalars().one()

        return user.email

    async def set_user_info(self, user_id: UUID, first_name: str | None, last_name: str | None, middle_name: str | None) -> UserSchemaFull:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        res = await self.session.execute(query)
        
        user = res.scalars().one()

        user.first_name = first_name
        user.last_name = last_name
        user.middle_name = middle_name

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        # TODO: Изменять значение в кеше при обновлении данных пользователя
        cache_key = f"user_info:{user_id}"
        await cache.delete(cache_key)
        
        return UserSchemaFull(
            id=user.id,
            email=user.email,
            firstName=user.first_name,
            lastName=user.last_name,
            middleName=user.middle_name
        )

    @cache(ttl="5m", key="user_info:{user_id}")
    async def get_user_info(self, user_id: UUID) -> UserSchemaFull:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        res = await self.session.execute(query)
        
        user = res.scalars().one()
        # last_name: 
        # first_name:
        # middle_name
        # email: Mapp
        return UserSchemaFull(
            id=user.id,
            email=user.email,
            firstName=user.first_name,
            lastName=user.last_name,
            middleName=user.middle_name
        )
