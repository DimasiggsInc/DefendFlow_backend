from uuid import UUID
from pydantic import BaseModel
from fastapi import HTTPException, status

from src.users.interfaces import UserServicePort, UserRepositoryPort
from src.users.registry import RoleRegistry
from src.users.schemas import UserFullRequest, UserPatchSchema
from src.users.models import User
from src.users.exceptions import UserNotFoundError



class UserService(UserServicePort):
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo
    
    async def get_user_by_id(self, id: UUID) -> User | None:
        try:
            user_data = await self.user_repo.get_by_id(id)
            return user_data
        except UserNotFoundError:
            return None
    
    async def patch_user(self, user_id: UUID, patch_data: UserPatchSchema) -> "User | None":
        data_to_update = patch_data.get_changed_fields()
        if not data_to_update:
            return await self.user_repo.get_user_with_profiles(user_id)

        updated_user = await self.user_repo.update_partial(user_id, data_to_update)
        if not updated_user:
            return None

        return updated_user

    async def get_full_profile(self, user_id: UUID) -> BaseModel:
        user = await self.user_repo.get_user_with_profiles(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return RoleRegistry.resolve(user)


    async def get_roles(self, user_id: UUID):
        return await self.user_repo.get_roles(user_id)
