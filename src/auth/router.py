"""Обработчик аутентификации пользователей."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_user

from src.auth.interfaces import AuthServicePort

from src.auth.dependencies import get_auth_service
from src.users.schemas import UserAuthenticationRequest, UserAuthenticationResponse, UserMeResponse, VerifyEmailCodeRequest, SendEmailCodeRequest

from src.auth.exceptions import InvalidVerificationCodeError, TooManyVerificationAttemptsError, UserAlreadyExistsError, VerificationCodeNotFoundError


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
    try:
        print(f"Проверяем код {user.verification_code} для email {user.email}")
        await auth_service.verify_email_code(user.email, user.verification_code)

        reg_request = UserAuthenticationRequest(
            email=user.email,
            password=user.password,
        )
        result = await auth_service.register(reg_request)

        return UserAuthenticationResponse(token=result.token, refresh_token=result.refresh_token)
    # TODO: при большом количестве запросов на верификацию одного email, можно временно блокировать возможность отправки кодов на этот email, чтобы предотвратить спам и атаки перебором кодов
    except TooManyVerificationAttemptsError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification attempts. Please try again later.",
        )
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    except InvalidVerificationCodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code",
        )
    except VerificationCodeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification code not found",
        )



@router.post(
        "/register/send-email-code",
        status_code=status.HTTP_202_ACCEPTED,
)
async def send_email_code(
    user: SendEmailCodeRequest,
    auth_service: AuthServicePort = Depends(get_auth_service)
):
    if await auth_service.get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

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
