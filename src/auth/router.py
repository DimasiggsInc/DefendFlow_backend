"""Обработчик аутентификации пользователей."""

from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_user

from src.auth.interfaces import AuthServicePort

from src.auth.dependencies import get_auth_service
from src.users.schemas import UserAuthenticationRequest, UserAuthenticationResponse, UserMeResponse, VerifyEmailCodeRequest, SendEmailCodeRequest



router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
        "/login",
        response_model=UserAuthenticationResponse,
        status_code=status.HTTP_200_OK,
)
async def login(
    user: UserAuthenticationRequest, auth_service: AuthServicePort = Depends(get_auth_service)
) -> UserAuthenticationResponse:
    user_response = await auth_service.login(user)

    return user_response


@router.post(
        "/register/verify-email-code",
        response_model=UserAuthenticationResponse,
        status_code=status.HTTP_201_CREATED,
)
async def verify_email_code(
    user: VerifyEmailCodeRequest,
    auth_service: AuthServicePort = Depends(get_auth_service)
):
    print(f"Проверяем код {user.verification_code} для email {user.email}")
    await auth_service.verify_email_code(user.email, user.verification_code)

    reg_request = UserAuthenticationRequest(
        email=user.email,
        password=user.password,
    )
    result = await auth_service.register(reg_request)

    return UserAuthenticationResponse(token=result.token, refresh_token=result.refresh_token)



@router.post(
        "/register/send-email-code",
        status_code=status.HTTP_202_ACCEPTED,
)
async def send_email_code(
    user: SendEmailCodeRequest,
    auth_service: AuthServicePort = Depends(get_auth_service)
):
    await auth_service.get_user_by_email(user.email)  # Проверяем, что пользователь с таким email уже существует.

    await auth_service.send_email_code(user.email)

    return {"message": "Verification code sent to email"}



@router.get("/me", response_model=UserMeResponse, status_code=status.HTTP_200_OK)
async def me(current_user: dict = Depends(get_current_user)):
    """Получить профиль текущего пользователя."""
    print(current_user)

    return UserMeResponse(
        id=current_user["id"],
        email=current_user["email"],
    )

# TODO: POST /api/auth/refresh
