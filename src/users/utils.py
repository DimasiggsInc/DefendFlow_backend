from src.users.registry import RoleRegistry
from typing import Type


def register_role(rel_name: str):
    """Декоратор: регистрирует стратегию и её relationship в реестре."""
    def decorator(cls: Type) -> Type:
        RoleRegistry.register(
            rel_name=rel_name,
            serializer_cls=cls
        )
        return cls
    return decorator
