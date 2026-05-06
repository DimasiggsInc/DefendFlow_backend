from src.users.interfaces import UserServicePort, UserRepositoryPort
from uuid import UUID
from pydantic import BaseModel
from fastapi import HTTPException, status
from src.users.registry import RoleRegistry



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
