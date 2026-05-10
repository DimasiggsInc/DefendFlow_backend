from cashews import cache
from typing import Final
from uuid import UUID

from src.config import settings

cache.setup(settings.REDIS_URL)

class CacheKeys:
    USER_BY_EMAIL: Final[str] = "user:{user_email}"
    USER_PROFILE: Final[str] = "user_profile:{user_id}"

    @staticmethod
    def user_by_email(email: str) -> str:
        return CacheKeys.USER_BY_EMAIL.format(user_email=email)

    @staticmethod
    def user_profile(user_id: UUID) -> str:
        return CacheKeys.USER_PROFILE.format(user_id=user_id)
