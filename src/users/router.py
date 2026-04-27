"""Обработчик аутентификации пользователей."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_user

from src.auth.interfaces import AuthServicePort

from src.auth.dependencies import get_auth_service
from src.users.schemas import UserAuthenticationRequest, UserAuthenticationResponse, UserMeResponse

from src.auth.exceptions import UserAlreadyExistsError


router = APIRouter(
    prefix="/user",
    tags=["User"],
)
