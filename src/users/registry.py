from typing import Type, Callable, Any
from sqlalchemy.orm import joinedload
from pydantic import BaseModel

from src.users.interfaces import RoleSerializerPort
from src.users.models import User
from src.users.schemas import UserWithoutRoleResponse

class RoleRegistry:
    _registry: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(
        cls,
        rel_name: str,
        serializer_cls: Type[RoleSerializerPort],
        loader_factory: Callable[[], Any] | None = None
    ) -> None:
        """
        Регистрирует роль.
        
        :param rel_name: имя атрибута связи в модели User (например, "student_profile")
        :param serializer_cls: класс сериализатора для этой роли
        :param loader_factory: опциональная фабрика для SQLAlchemy loader option
        """
        
        if loader_factory is None:
            loader_factory = lambda: joinedload(getattr(User, rel_name))  # noqa
        
        cls._registry[rel_name] = {
            "serializer": serializer_cls,
            "loader": loader_factory
        }

    @classmethod
    def get_load_options(cls) -> list[Any]:
        """Возвращает список опций загрузки для SQLAlchemy."""
        return [item["loader"]() for item in cls._registry.values()]

    @classmethod
    def resolve(cls, user: "User") -> BaseModel:
        """
        Находит активную роль и возвращает типизированный ответ.
        Если роль не найдена — возвращает базовый ответ с null-значениями.
        """
        for rel_name, config in cls._registry.items():
            profile = getattr(user, rel_name, None)
            if profile is not None:
                return config["serializer"]().serialize(user)
        
        return UserWithoutRoleResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role=None,
            profile=None
        )

from src.users.serializers import CuratorSerializer, AdminSerializer, ExpertSerializer, StudentSerializer  # noqa
