"""Схемы для пользователя."""

import re
from typing import Annotated, Any, Literal, Optional, Union
from uuid import UUID
from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, EmailStr
from pydantic.config import ConfigDict
from enum import StrEnum

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


class UserRolesEnum(StrEnum):
    CURATOR = "curator"
    ADMIN = "admin"
    STUDENT = "student"
    EXPERT = "expert"
    NONE = "none"


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





class CuratorProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID

class AdminProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    admin_signature_image_url: Optional[str] = None

class ExpertProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    position: Optional[str] = None
    company: Optional[str] = None

class StudentProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    academ_group: Optional[str] = None



class UserBaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None


class UserWithCurator(UserBaseRead):
    role: Literal[UserRolesEnum.CURATOR]
    profile: CuratorProfileRead

class UserWithAdmin(UserBaseRead): 
    role: Literal[UserRolesEnum.ADMIN]
    profile: AdminProfileRead

class UserWithStudent(UserBaseRead): 
    role: Literal[UserRolesEnum.STUDENT]
    profile: StudentProfileRead

class UserWithExpert(UserBaseRead): 
    role: Literal[UserRolesEnum.EXPERT]
    profile: ExpertProfileRead


# Объединённая модель для FastAPI response_model
UserFullResponse = Union[
    UserWithCurator,
    UserWithAdmin,
    UserWithStudent,
    UserWithExpert
]

class UserWithoutRoleResponse(BaseModel):
    """Базовый ответ, когда у пользователя нет назначенной роли."""
    id: UUID
    email: str
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str]
    role: None = None
    profile: None = None
