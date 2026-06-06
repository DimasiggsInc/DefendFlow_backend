from typing import TypeVar, Type, Callable, Awaitable, Any
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_session
from src.auth.dependencies import get_current_user

T = TypeVar("T")

# Тип для функции-политики: (юзер, сущность, сессия) -> bool
PolicyFunc = Callable[[dict, T, AsyncSession], Awaitable[bool]]

def require_access(
    model: Type[T],
    policy: PolicyFunc,
    load_options: list[Any] | None = None, # Поддержка selectinload/joinedload
    error_404: str = "Resource not found",
    error_403: str = "Access denied"
):
    """
    Универсальная фабрика зависимостей для проверки прав доступа.
    """
    async def dependency(
        resource_id: UUID, 
        session: AsyncSession = Depends(get_session),
        current_user: dict = Depends(get_current_user),
    ) -> T:
        # 1. Умная загрузка из БД
        if load_options:
            stmt = select(model).where(model.id == resource_id).options(*load_options)
            result = await session.execute(stmt)
            entity = result.scalar_one_or_none()
        else:
            # session.get оптимизирован и использует Identity Map
            entity = await session.get(model, resource_id)
            
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_404)
            
        # 2. Делегируем проверку бизнес-логики политике
        has_access = await policy(current_user, entity, session)
        
        if not has_access:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_403)
            
        return entity

    # Для красивого отображения в Swagger/OpenAPI
    dependency.__name__ = f"require_{model.__name__.lower()}_{policy.__name__}"
    return dependency
