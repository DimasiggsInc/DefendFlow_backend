from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import MailServiceMock
from src.auth.services import AuthService
from src.auth.utils import Hasher
from src.auth.utils import JWTService

from src.auth.interfaces import AuthServicePort, MailServicePort
from src.auth.interfaces import HasherPort
from src.auth.interfaces import AuthRepositoryPort
from src.auth.interfaces import JWTServicePort

from src.auth.repositories import AuthRepository

from src.database import get_session
from src.dependencies import get_redis

from src.config import settings


load_dotenv(override=True)

security = HTTPBearer()

async def get_mail_service() -> MailServicePort:
    return MailServiceMock(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)


async def get_hasher() -> HasherPort:
    pepper = settings.PEPPER
    return Hasher(pepper)


async def get_auth_repository(
    db: AsyncSession = Depends(get_session),
) -> AuthRepositoryPort:
    return AuthRepository(db)


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
    auth_repository: AuthRepositoryPort = Depends(get_auth_repository),
    jwt_util: JWTServicePort = Depends(get_jwt_service),
    redis=Depends(get_redis),
    mail_service: MailServicePort = Depends(get_mail_service)
) -> AuthServicePort:
    return AuthService(hasher, auth_repository, jwt_util, redis, mail_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_util: JWTServicePort = Depends(get_jwt_service),
    auth_repo: AuthRepositoryPort = Depends(get_auth_repository)
) -> dict:
    """Получение id текущего пользователя"""
    try:
        a = jwt_util.decode(credentials.credentials)
        email = await auth_repo.get_email(a["id"])

        return {"id": a["id"], "email": email}  #  TODO: Возвращать схемой пользователя, а не просто словарём
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")  # TODO: Исправить на более конкретные ошибки
