"""Схемы для пользователя."""

import re
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, EmailStr
from pydantic.config import ConfigDict


UserEmail = Annotated[EmailStr, Field(max_length=255, description="Email пользователя")]

# Пароль: мин. 8 символов, обязательные буквы и цифры
UserPassword = Annotated[
    str,
    Field(
        min_length=8,
        max_length=128,
        description="Пароль (мин. 8 символов, буквы и цифры)"
    )
]


class UserSchemaBase(BaseModel):
    """Базовая схема для пользователей, от которой наследуется большинство схем."""

    id: UUID
    model_config = ConfigDict(from_attributes=True)


class UserSchemaFull(UserSchemaBase):
    """Полная схема пользователя"""
    email: UserEmail
    hashed_password: str
    salt: str


class UserAuthenticationRequest(BaseModel):
    """Схема для запроса на добавление пользователей."""

    email: UserEmail
    password: UserPassword

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Проверка сложности пароля."""
        if not re.search(r"[A-ZА-ЯЁ]", value):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-zа-яё]", value):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"\d", value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return value

    # Нормализация email (нижний регистр)
    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class VerifyEmailCodeRequest(UserAuthenticationRequest):
    """Схема для запроса на верификацию email."""
    verification_code: str = Field(..., min_length=6, max_length=6, description="6-значный код верификации")


class SendEmailCodeRequest(BaseModel):
    """Схема для запроса на отправку кода на почту."""
    email: UserEmail

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserAuthenticationResponse(BaseModel):
    """Схема для ответа на запрос на добавление пользователей."""

    token: str
    refresh_token: str


class UserMeResponse(BaseModel):
    id: UUID
    email: UserEmail


class StudentSchemaFull(UserSchemaBase):
    """Полная схема для студента."""
    email: UserEmail
    firstName: str
    lastName: str
    middleName: str
    academGroup: str
