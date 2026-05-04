from collections.abc import AsyncIterator
import re
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

from contextlib import asynccontextmanager

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей БД."""

    @declared_attr
    def __tablename__(cls) -> str:
        """Генерирует __tablename__ автоматически из имени класса в snake_case."""
        # Преобразуем CamelCase в snake_case
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower()


@asynccontextmanager
async def get_async_connection() -> AsyncIterator[AsyncSession]:
    """Возвращает async context manager для сессии."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Для FastAPI Depends (без context manager):
async def get_session() -> AsyncIterator[AsyncSession]:
    """Возвращает асинхронную сессиию."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def get_session_sync():
    return async_session_maker()
