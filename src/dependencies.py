from fastapi import HTTPException, Request

from typing import Type, TypeVar, Callable
from sqlalchemy.orm import Session


async def get_redis(request: Request):
    yield request.app.state.redis


T = TypeVar("T")

def make_owner_dependency(
    model: Type[T],
    owner_field: str = "user_id",
    allow_admin: bool = True,
):
    """Фабрика: создаёт зависимость для проверки владения конкретной моделью."""
    
    async def dependency(
        resource_id: int,  # имя параметра зависит от path-параметра в роуте
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> T:
        resource = db.query(model).filter(model.id == resource_id).first()
        
        if not resource:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        
        # Проверка прав
        is_owner = getattr(resource, owner_field) == current_user.id
        is_admin = allow_admin and current_user.role == UserRole.ADMIN
        
        if not (is_owner or is_admin):
            from src.users.exceptions import AccessDeniedError
            raise AccessDeniedError()
        
        return resource
    
    # Даём фабрике имя — это важно для OpenAPI документации
    dependency.__name__ = f"get_current_user_{model.__name__.lower()}"
    return dependency