from uuid import UUID
from typing import Protocol

from typing import Optional, List

from src.repositories import BaseRepositoryPort
from src.users.schemas import (
    UserAuthenticationResponse,
    UserAuthenticationRequest,
)
from src.users.models import User
from sqlalchemy.ext.asyncio import AsyncSession


class AuthRepositoryPort(BaseRepositoryPort):
    def __init__(self, model: type[User], session: AsyncSession) -> None: ...
    async def get_by_id(self, id: UUID) -> Optional[User]: ...
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]: ...
    async def create(self, obj: User) -> User: ...
    async def update(self, obj: User) -> User: ...
    async def delete(self, obj: User) -> None: ...
    
    async def get_by_email(self, user_email: str) -> Optional[User]: ...


class AuthServicePort(Protocol):
    async def register(self, user: UserAuthenticationRequest) -> UserAuthenticationResponse: ...
    async def login(self, user: UserAuthenticationRequest) -> UserAuthenticationResponse: ...
    async def get_user_by_email(self, email: str) -> str | None: ...
    async def send_email_code(self, email: str) -> None: ...
    async def verify_email_code(self, email: str, code: str) -> None: ...


class HasherPort(Protocol):
    pepper: str
    salt_len: int

    def encode(self, text: str, salt: str) -> str: ...
    def verify(self, text: str, salt: str, hashed_text: str) -> bool: ...
    @property
    def salt(self) -> str: ...


class JWTServicePort(Protocol):
    alg: str
    secret_key: str
    exp_minutes: str

    def encode(self, user_id: UUID) -> str:
        """
        Docstring for encode
        
        :return: 
        :rtype: str
        """
        ...

    def decode(self, access_token: str) -> dict:
        """
        Docstring for decode
        
        :return: {"id": str, "exp": int}
        :rtype: dict
        """
        ...



class MailServicePort(Protocol):
    sender_email: str
    sender_password: str

    async def send_email(self, email: str, code: str) -> None:
        """
        Docstring for send_email
        
        :return: None
        :rtype: None
        """
        ...
