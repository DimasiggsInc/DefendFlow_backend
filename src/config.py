"""Настройки для всего проекта."""

import os
from dotenv import load_dotenv
from typing import List


if os.getenv("DOCKER_ENV") != "true":
    from dotenv import load_dotenv
    load_dotenv(override=True)


class Settings:
    APP_VERSION: str = "0.0.1"
    PORT: int = int(os.getenv("PORT", 8000))
    
    RATE_LIMIT_COUNT: int = int(os.getenv("RATE_LIMIT_COUNT", 100))

    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "postgres")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_NAME: str = os.getenv("POSTGRES_NAME", "defendflow_db")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/defendflow_db",
    )

    # CORS настройки
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    ALLOW_CREDENTIALS: bool = os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true"

    PEPPER: str = os.getenv("PEPPER", "pepper")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "lol")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", 10))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 6000)) # Время жизни кэша в секундах (по умолчанию 6000 секунд, или 100 минут)
    EMAIL_CODE_CACHE_TTL: int = int(os.getenv("EMAIL_CODE_CACHE_TTL", 600))

    # Email settings
    EMAIL_SENDER: str = os.getenv("EMAIL_SENDER", "noreply@defendflow.com")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "password")
    MAX_VERIFICATION_ATTEMPTS: int = int(os.getenv("MAX_VERIFICATION_ATTEMPTS", 3))

settings = Settings()
