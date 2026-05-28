"""Обработчик пользователей."""

from fastapi import APIRouter, Depends, status
from uuid import uuid4

from src.auth.dependencies import get_current_user
from src.users.interfaces import UserServicePort
from src.users.dependencies import get_user_service
from src.users.schemas import CuratorProfileUpdate, CurrentUser, ExpertProfileUpdate, StudentProfileUpdate, UserFullResponse, UserPatchSchema, UserRolesEnum, UserSchemaFull, UserWithCuratorRequest, UserWithExpertRequest, UserWithStudentRequest, UserWithoutRoleResponse
from src.users.exceptions import UserNotFoundError


router = APIRouter(
    prefix="/user",
    tags=["User"],
)

# @router.post("/role", response_model=UserFullResponse | UserWithoutRoleResponse, status_code=status.HTTP_200_OK)
# async def get_profile_info(
#     current_user: CurrentUser = Depends(get_current_user),
#     user_service: UserServicePort = Depends(get_user_service)
# ):
#     """Получить профиль текущего пользователя."""
#     data = await user_service.get_full_profile(current_user.id)
#     return data


@router.get("/profile", response_model=UserFullResponse | UserWithoutRoleResponse, status_code=status.HTTP_200_OK)
async def get_profile_info(
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserServicePort = Depends(get_user_service)
):
    """Получить профиль текущего пользователя."""
    data = await user_service.get_full_profile(current_user.id)
    return data

@router.patch("/profile", response_model=UserSchemaFull, status_code=status.HTTP_200_OK)
async def update_user(
    patch_data: UserPatchSchema,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserServicePort = Depends(get_user_service)
):
    from src.users.models import User
    updated_user: User = await service.patch_user(current_user.id, patch_data)
    if not updated_user:
        raise UserNotFoundError()
    
    # Преобразуем ORM-модель в Pydantic для ответа
    print(updated_user.to_read_model())
    return UserSchemaFull.model_validate(updated_user)


# --- STUDENT ---
@router.patch("/student", response_model=UserWithStudentRequest)
async def update_student_profile(
    profile_data: StudentProfileUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserServicePort = Depends(get_user_service)
):
    """Обновить профиль Студента (Заглушка)"""

    
    # Создаем экземпляр модели профиля студента
    student_profile = StudentProfileUpdate(
        academ_group="CS-101",
    )

    # Создаем экземпляр полного ответа пользователя
    return UserWithStudentRequest(
        email="student@example.com",
        first_name="Иван",
        middle_name="Иванович",
        last_name="Студентов",
        role=UserRolesEnum.STUDENT, # Используем Enum, если он определен так
        profile=student_profile
    )


# --- CURATOR ---
@router.patch("/curator", response_model=UserWithCuratorRequest)
async def update_curator_profile(
    profile_data: CuratorProfileUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserServicePort = Depends(get_user_service)
):
    """Обновить профиль Куратора (Заглушка)"""

    curator_profile = CuratorProfileUpdate()

    return UserWithCuratorRequest(
        id=uuid4(),
        email="curator@example.com",
        first_name="Мария",
        middle_name="Петровна",
        last_name="Кураторова",
        role=UserRolesEnum.CURATOR,
        profile=curator_profile
    )


# --- EXPERT ---
@router.patch("/expert", response_model=UserWithExpertRequest)
async def update_expert_profile(
    profile_data: ExpertProfileUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserServicePort = Depends(get_user_service)
):
    """Обновить профиль Эксперта (Заглушка)"""

    expert_profile = ExpertProfileUpdate(
        position="Позер",
        company="Говнокомпания"
        # добавьте остальные обязательные поля из ExpertProfileRead
    )

    return UserWithExpertRequest(
        id=uuid4(),
        email="expert@example.com",
        first_name="Алексей",
        middle_name="Сергеевич",
        last_name="Экспертов",
        role=UserRolesEnum.EXPERT,
        profile=expert_profile
    )
