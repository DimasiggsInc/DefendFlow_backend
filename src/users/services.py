from src.users.interfaces import UserServicePort, UserRepositoryPort
from uuid import UUID
from pydantic import BaseModel
from fastapi import HTTPException, status
from src.users.registry import RoleRegistry
from src.users.schemas import UserFullRequest



class UserService(UserServicePort):
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo

    # async def register(self, user: UserAuthenticationRequest) -> UserAuthenticationResponse: ...
    # async def login(self, user: UserAuthenticationRequest) -> UserAuthenticationResponse: ...
    # async def get_user_by_email(self, email: str) -> str | None: ...
    # async def send_email_code(self, email: str) -> None: ...
    # async def verify_email_code(self, email: str, code: str) -> None: ...

    async def get_full_profile(self, user_id: UUID) -> BaseModel:
        user = await self.user_repo.get_user_with_profiles(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return RoleRegistry.resolve(user)

    async def update_full_profile(self, user_id: UUID, user_data: UserFullRequest) -> BaseModel:
        """
        Обновляет профиль пользователя с учётом роли.
        Принимает Union-схему и делегирует обработку.
        """
        
        base_update = {
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "middle_name": user_data.middle_name,
        }
        
        # TODO: Сделать передачу SQLAlchemy модели в репо
        user = await self.user_repo.update_user(user_id, **{k: v for k, v in base_update.items() if v is not None})
        
        
        if user_data.profile is not None:
            profile_data = user_data.profile.model_dump(exclude_unset=True)
            if profile_data:
                await self.user_repo.update_profile(
                    user_id=user_id,
                    profile_type=user_data.role,
                    **profile_data
                )
        
        updated_user = await self.user_repo.get_user_with_profiles(user_id)
        return RoleRegistry.resolve(updated_user)
