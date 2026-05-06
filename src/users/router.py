"""Обработчик пользователей."""

from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_user

from src.users.interfaces import UserServicePort

from src.users.dependencies import get_user_service

from src.users.schemas import UserFullResponse, UserWithoutRoleResponse, UserFullRequest



router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.get("/profile", response_model=UserFullResponse | UserWithoutRoleResponse, status_code=status.HTTP_200_OK)
async def get_profile_info(
    current_user: dict = Depends(get_current_user),
    user_service: UserServicePort = Depends(get_user_service)
):
    """Получить профиль текущего пользователя."""
    data = await user_service.get_full_profile(current_user["id"])
    print(data)
    return data


@router.patch("/profile", response_model=UserFullResponse | UserWithoutRoleResponse, status_code=status.HTTP_200_OK)
async def update_profile_info(
    new_user_data: UserFullRequest,
    current_user: dict = Depends(get_current_user),
    user_service: UserServicePort = Depends(get_user_service)
):
    """Получить профиль текущего пользователя. (Заглушка)"""
    
    return await user_service.get_full_profile(current_user["id"])
