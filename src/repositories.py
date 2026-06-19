from typing import Generic, TypeVar, List, Optional, Protocol
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.cache import cache


ModelType = TypeVar("ModelType")



class BaseRepositoryPort(Protocol):
    def __init__(self, model: type[ModelType], session: AsyncSession) -> None: ...
    async def get_by_id(self, id: UUID) -> Optional[ModelType]: ...
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]: ...
    async def create(self, obj: ModelType) -> ModelType: ...
    async def update(self, obj: ModelType) -> ModelType: ...
    async def delete(self, obj: ModelType) -> None: ...


class BaseRepository(BaseRepositoryPort, Generic[ModelType]):
    """Базовый репозиторий, работающий только с ORM-моделями."""
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
        self._prefix = getattr(model, "__tablename__", model.__name__)

    def _key(self, *parts: str) -> str:
        return f"{self._prefix}:{':'.join(str(p) for p in parts)}"

    def _invalidate_single(self, obj_id: UUID):
        cache.delete(self._key("id", obj_id))

    # @cache(ttl="5m", key="{self._key('id', id)}")
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        res = await self.session.execute(select(self.model).where(self.model.id == id))
        return res.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        res = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return list(res.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        print(f"Создание объекта c данными: {obj.__dict__}")
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def update(self, obj: ModelType) -> ModelType:
        await self.session.commit()
        await self.session.refresh(obj)

        cache_key = self._key("id", obj.id)
        cache.delete(cache_key)

        return obj

    async def delete(self, obj: ModelType) -> None:
        await self.session.delete(obj)
        await self.session.commit()
        cache_key = self._key("id", obj.id)
        cache.delete(cache_key)
