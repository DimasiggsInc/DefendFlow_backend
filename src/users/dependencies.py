from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session
from src.users.repositories import UserRepository
from src.users.services import UserService
from src.users.interfaces import UserServicePort, UserRepositoryPort
from src.users.models import User

def get_user_repo(db: AsyncSession = Depends(get_session)) -> UserRepositoryPort:
    return UserRepository(User, db)


def get_user_service(repo: UserRepositoryPort = Depends(get_user_repo)) -> UserServicePort:
    return UserService(repo)
