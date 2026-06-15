# # from typing import Annotated
# # from uuid import UUID
# # import unicodedata
# # import regex

# # from pydantic import (
# #     BaseModel, EmailStr, ConfigDict,
# #     Field, AfterValidator, SecretStr,
# #     BeforeValidator,
# # )


# # USER_MAX_AGE = 130
# # USER_MIN_AGE = 13

# # PASSWORD_MIN_LENGTH = 8
# # PASSWORD_MAX_LENGTH = 50

# # UPPER_PATTERN = regex.compile(r"\p{Lu}")
# # LOWER_PATTERN = regex.compile(r"\p{Ll}")
# # DIGIT_PATTERN = regex.compile(r"\p{N}")

# # _ZERO_WIDTH_CHARS = '\u200B\u200C\u200D\uFEFF\u2060'
# # ZERO_WIDTH_TABLE = str.maketrans('', '', _ZERO_WIDTH_CHARS)

# # def remove_zero_width_chars(text: str) -> str:
# #     return text.translate(ZERO_WIDTH_TABLE)

# # def normalize_text(text: str) -> str:
# #     # Приводим к канонической форме NFC
# #     return unicodedata.normalize('NFC', text)

# # def validate_password_strength(password: str) -> str:
# #     if not isinstance(password, str):
# #         raise ValueError(f"Пароль должен быть строкой, получено: {type(password).__name__}")
    
# #     normalized_password = normalize_text(remove_zero_width_chars(password))

# #     if not normalized_password:
# #         raise ValueError("Пароль не может состоять только из невидимых символов")
# #     if len(normalized_password) < PASSWORD_MIN_LENGTH:
# #         raise ValueError(f"Пароль должен содержать минимум {PASSWORD_MIN_LENGTH} символов")
# #     if len(normalized_password) > PASSWORD_MAX_LENGTH:
# #         raise ValueError(f"Пароль не должен превышать {PASSWORD_MAX_LENGTH} символов")
# #     if not UPPER_PATTERN.search(normalized_password):
# #         raise ValueError("Должна быть хотя бы одна заглавная буква (любой алфавит)")
# #     if not LOWER_PATTERN.search(normalized_password):
# #         raise ValueError("Должна быть хотя бы одна строчная буква (любой алфавит)")
# #     if not DIGIT_PATTERN.search(normalized_password):
# #         raise ValueError("Должна быть хотя бы одна цифра")
# #     return normalized_password


# # UserEmail = Annotated[
# #     EmailStr,
# #     Field(
# #         description="Email пользователя",
# #         json_schema_extra={"examples": ["user@example.com"]},
# #         max_length=255
# #     )
# # ]

# # UserAge = Annotated[
# #     int,
# #     Field(
# #         ge=USER_MIN_AGE,
# #         le=USER_MAX_AGE,
# #         description=f"Возраст пользователя. От {USER_MIN_AGE} до {USER_MAX_AGE} лет"
# #     )
# # ]

# # UserId = Annotated[
# #     UUID,
# #     Field(
# #         description=f"UUID пользователя",
# #         json_schema_extra={"examples": ["0ed99044-63a9-4006-8cb6-f79e79c118f7"]}
# #     )
# # ]

# # UserPassword = Annotated[
# #     SecretStr,
# #     BeforeValidator(validate_password_strength),
# #     Field(
# #         description=f"Пароль пользователя. Длина: {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} символов. Должны быть минимум одна цифра, одна заглавная буква, одна строчная буква",
# #         json_schema_extra={"examples": ["1Stringst"]}
# #     )
# # ]


# # class UserRegistration(BaseModel):
# #     model_config = ConfigDict(
# #         title="Регистрация нового пользователя",
# #         extra="forbid",
# #         strict=True,
# #         frozen=True
# #     )

# #     email: UserEmail
# #     age: UserAge
# #     password: UserPassword


# # class UserRegistrationResponse(BaseModel):
# #     model_config = ConfigDict(
# #         title="Регистрация нового пользователя",
# #         extra="forbid",
# #         strict=True,
# #         frozen=True
# #     )
# #     user_id: UserId
# #     email: UserEmail
# #     age: UserAge

# #     is_premium: bool = Field(
# #         description="Есть ли премиум у человека"
# #     )



# # data = {"email": "test@example.com", "age": 25, "password": "1Strinsa\u200B\u200C\u200D"}
# # user = UserRegistration(**data)

# # print(data["password"] == str(user.password.get_secret_value()))
# # print(f"'{data["password"]}'")
# # print(f"'{user.password.get_secret_value()}'")

# from typing import Annotated
# from pydantic import BaseModel, BeforeValidator, Field, ConfigDict
# from uuid import UUID
# from decimal import Decimal, ROUND_HALF_UP


# def parse_decimal(value: str | int | float | Decimal) -> Decimal:
#     """Безопасно преобразует любое значение в Decimal."""
#     if isinstance(value, Decimal):
#         return value
    
#     if isinstance(value, float):
#         raise ValueError(
#             "Используйте строки для Decimal, а не float. "
#             f"Получено: {value}"
#         )
#     return Decimal(str(value))


# UserId = Annotated[
#     UUID,
#     Field(
#         description="UUID пользователя"
#     )
# ]

# ProductId = Annotated[
#     UUID,
#     Field(
#         description="UUID продукта"
#     )
# ]

# Amount = Annotated[
#     Decimal,
#     BeforeValidator(parse_decimal),
#     Field(
#         description="Количество чего-либо"
#     )
# ]


# class OrderCreate(BaseModel):
#     model_config = ConfigDict(
#         title="Создание нового заказа",
#         extra="forbid",
#         strict=True,
#         frozen=True
#     )

#     user_id: UserId
#     product_id: ProductId


# class PaymentRequest(BaseModel):
#     model_config = ConfigDict(
#         title="Получение оплаты",
#         extra="forbid",
#         strict=True,
#         frozen=True
#     )
    


# class RefundRequest(BaseModel):
#     model_config = ConfigDict(
#         title="Возврат денег за заказ",
#         extra="forbid",
#         strict=True,
#         frozen=True
#     )
    




# data = {}


# print()

