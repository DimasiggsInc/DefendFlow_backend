from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import MailService
from src.auth.services import AuthService
from src.auth.utils import Hasher
from src.auth.utils import JWTService

from src.auth.interfaces import AuthServicePort, MailServicePort
from src.auth.interfaces import HasherPort
from src.users.interfaces import UserRepositoryPort, UserServicePort
from src.auth.interfaces import JWTServicePort

from src.users.repositories import UserRepository

from src.database import get_session
from src.dependencies import get_redis

from src.config import settings
from src.users.models import User
from src.users.dependencies import get_user_service
from src.users.schemas import UserRolesEnum


load_dotenv(override=True)

security = HTTPBearer()

async def get_mail_service() -> MailServicePort:
    return MailService(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)


async def get_hasher() -> HasherPort:
    pepper = settings.PEPPER
    return Hasher(pepper)


async def get_auth_repository(
    db: AsyncSession = Depends(get_session),
) -> UserRepositoryPort:
    return UserRepository(User, db)


def get_jwt_service() -> JWTServicePort:
    secret_key = settings.SECRET_KEY
    alg = settings.JWT_ALGORITHM
    exp_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    return JWTService(
        alg,
        secret_key,
        exp_minutes
    )


async def get_auth_service(
    hasher: HasherPort = Depends(get_hasher),
    auth_repository: UserRepositoryPort = Depends(get_auth_repository),
    jwt_util: JWTServicePort = Depends(get_jwt_service),
    redis=Depends(get_redis),
    mail_service: MailServicePort = Depends(get_mail_service)
) -> AuthServicePort:
    return AuthService(hasher, auth_repository, jwt_util, redis, mail_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_util: JWTServicePort = Depends(get_jwt_service),
    auth_repo: UserRepositoryPort = Depends(get_auth_repository)
) -> dict:
    """Получение id текущего пользователя"""
    try:
        a = jwt_util.decode(credentials.credentials)

        user = await auth_repo.get_by_id(a["id"])
        print(user.email)
        return {"id": user.id, "email": user.email}  #  TODO: Возвращать схемой пользователя, а не просто словарём
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")  # TODO: Исправить на более конкретные ошибки


def require_role(required_role: UserRolesEnum):
    """
    Фабрика зависимостей для проверки роли.
    Возвращает функцию-зависимость, которая проверяет наличие required_role у пользователя.
    """
    async def role_checker(
        user: UUID = Depends(get_current_user),
        user_service: UserServicePort = Depends(get_user_service)
    ) -> UUID:
        user_id = user["id"]
        # 1. Получаем список ролей пользователя (из БД или кэша)
        # Ожидается, что сервис вернет список Enum-ов или строк
        user_roles = await user_service.get_roles(user_id)
        
        # 2. Проверка
        # Если user_roles это список строк, то: required_role.value not in user_roles
        # Если список Enum-ов, то: required_role not in user_roles
        if required_role not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        
        # 3. Возвращаем user_id, чтобы использовать его в эндпоинте
        return user_id
        
    return role_checker