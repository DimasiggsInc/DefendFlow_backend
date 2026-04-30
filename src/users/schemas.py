"""Схемы для пользователя."""

import re
from typing import Annotated, Any, Optional
from uuid import UUID
from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, field_validator, EmailStr
from pydantic.config import ConfigDict


# ─── Функции-валидаторы (чистые, без привязки к классам) ─────────────────────
def normalize_email(value: Any) -> str:
    """Нормализация email: strip + lower. Безопасно для не-str значений."""
    if not isinstance(value, str):
        return value  # Pydantic сам выбросит ошибку типа позже
    return value.strip().lower()

def validate_password_strength(value: str) -> str:
    """Проверка сложности пароля."""
    if len(value) < 8:
        raise ValueError("Пароль должен содержать минимум 8 символов")
    if not re.search(r"[A-ZА-ЯЁ]", value):
        raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
    if not re.search(r"[a-zа-яё]", value):
        raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
    if not re.search(r"\d", value):
        raise ValueError("Пароль должен содержать хотя бы одну цифру")
    return value


NormalizedEmail = Annotated[
    EmailStr,
    BeforeValidator(normalize_email),
    Field(max_length=255, description="Email пользователя")
]

StrongPassword = Annotated[
    str,
    AfterValidator(validate_password_strength),
    Field(min_length=8, max_length=128, description="Пароль")
]



class AddUser(BaseModel):
    email: NormalizedEmail
    password: StrongPassword
    firstName: Optional[str] = Field(None, min_length=1, max_length=20)
    lastName: Optional[str] = Field(None, min_length=1, max_length=20)
    middleName: Optional[str] = Field(None, min_length=1, max_length=20)


class UpdateUser(BaseModel):
    id: UUID
    email: Optional[NormalizedEmail]
    firstName: Optional[str] = Field(None, min_length=1, max_length=20)
    lastName: Optional[str] = Field(None, min_length=1, max_length=20)
    middleName: Optional[str] = Field(None, min_length=1, max_length=20)


class UserAuthenticationRequest(BaseModel):
    """Схема для запроса на добавление пользователей."""

    email: NormalizedEmail
    password: StrongPassword


class VerifyEmailCodeRequest(UserAuthenticationRequest):
    """Схема для запроса на верификацию email."""
    verification_code: str = Field(..., min_length=6, max_length=6, description="6-значный код верификации")


class UserSchemaBase(BaseModel):
    """Базовая схема для пользователей, от которой наследуется большинство схем."""

    id: UUID
    model_config = ConfigDict(from_attributes=True)


class UserSchemaFull(UserSchemaBase):
    """Полная схема пользователя"""
    email: NormalizedEmail
    firstName: str
    lastName: str
    middleName: str




class SendEmailCodeRequest(BaseModel):
    """Схема для запроса на отправку кода на почту."""
    email: NormalizedEmail


class UserAuthenticationResponse(BaseModel):
    """Схема для ответа на запрос на добавление пользователей."""

    token: str
    refresh_token: str


class UserMeResponse(BaseModel):
    id: UUID
    email: NormalizedEmail


class StudentSchemaFull(UserSchemaBase):
    """Полная схема для студента."""
    email: NormalizedEmail
    firstName: str
    lastName: str
    middleName: str
    academGroup: str
