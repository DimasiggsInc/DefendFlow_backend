from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from uuid import UUID

from src.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.auth.interfaces import AuthRepositoryPort
from src.models_hub import User



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

    async def get_user_hashed_password(self, user_id: UUID) -> str:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        res = await self.session.execute(query)
        
        user = res.scalars().one()

        return user.hashed_password

    async def get_user_salt(self, user_id: UUID) -> str:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        res = await self.session.execute(query)
        
        user = res.scalars().one()

        return user.salt
    
    async def get_email(self, user_id: UUID) -> str:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        res = await self.session.execute(query)
        
        user = res.scalars().one()

        return user.email
