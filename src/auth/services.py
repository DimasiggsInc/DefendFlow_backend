import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import secrets
from uuid import UUID

from redis.asyncio import Redis

from src.auth.interfaces import HasherPort, AuthServicePort, JWTServicePort, MailServicePort
from src.auth.exceptions import InvalidVerificationCodeError, TooManyVerificationAttemptsError, VerificationCodeNotFoundError 

from src.users.interfaces import UserRepositoryPort
from src.users.schemas import UserAuthenticationRequest, UserAuthenticationResponse
from src.users.exceptions import UserAlreadyExistsError, UserNotFoundError, IncorrectPasswordError

from src.config import settings
from src.users.models import User



class AuthService(AuthServicePort):
    def __init__(self, hasher: HasherPort, auth_repository: UserRepositoryPort, jwt_util: JWTServicePort, redis: Redis, mail_service: MailServicePort):
        self.hasher = hasher
        self.auth_repository = auth_repository
        self.jwt_util = jwt_util
        self.redis = redis
        self.mail_service = mail_service
        self.MAX_VERIFICATION_ATTEMPTS = settings.MAX_VERIFICATION_ATTEMPTS
    
    def _email_code_cache_key(self, email: str) -> str:
        return f"email_code:{email}"

    async def register(self, user: UserAuthenticationRequest) -> UserAuthenticationResponse:
        salt = self.hasher.salt
        hashed_password = self.hasher.encode(user.password, salt)

        create_data = User()
        create_data.email = user.email
        create_data.hashed_password = hashed_password
        create_data.salt = salt

        print(f"Регистрация пользователя с данными: email={user.email}, hashed_password={hashed_password}, salt={salt}")
        print(create_data.__dict__)
        
        user_data = await self.auth_repository.create(create_data)

        jwt_token = self.jwt_util.encode(user_data.id)

        return UserAuthenticationResponse(token=jwt_token, refresh_token="lol")

    async def login(self, user: UserAuthenticationRequest) -> UserAuthenticationResponse:
        try:
            user_data = await self.auth_repository.get_by_email(user.email)
        except ValueError:
            raise UserNotFoundError()
        
        if not self.hasher.verify(user.password, user_data.salt, user_data.hashed_password):
            raise IncorrectPasswordError()
        
        jwt_token = self.jwt_util.encode(user_data.id)

        return UserAuthenticationResponse(token=jwt_token, refresh_token="lol")

    async def get_user_by_email(self, email: str) -> str | None:
        try:
            user_data = await self.auth_repository.get_by_email(email)
            return user_data.id
        except Exception:
            return None
    
    async def get_user_by_id(self, id: UUID) -> str | None:
        try:
            user_data = await self.auth_repository.get_by_id(id)
            return user_data.id
        except UserNotFoundError:
            return None
    
    async def email_exists(self, email: str) -> bool:
        return self.auth_repository.email_exists(email)

    # TODO: Перенести в MailService
    async def send_email_code(self, email: str) -> None:
        if await self.email_exists(email) is True:
            raise UserAlreadyExistsError()
        code = str(secrets.randbelow(900000) + 100000)
        await self.mail_service.send_email(email, code)

        key = self._email_code_cache_key(email)
        async with self.redis.pipeline() as pipe:
            await pipe.hset(key, mapping={"code": code, "attempts": 0})
            await pipe.expire(key, settings.EMAIL_CODE_CACHE_TTL)
            await pipe.execute()

    async def verify_email_code(self, email: str, code: str) -> None:
        key = self._email_code_cache_key(email)
        
        if not await self.redis.exists(key):
            print(f"Код для email {email} не найден или истек")
            raise VerificationCodeNotFoundError()

        attempts = await self.redis.hincrby(key, "attempts", 1)

        if attempts > self.MAX_VERIFICATION_ATTEMPTS:
            await self.redis.delete(key)
            raise TooManyVerificationAttemptsError()
        
        cached_code = await self.redis.hget(key, "code")
        print(f"Проверяем код {code} для email {email}, попытка {attempts}/{self.MAX_VERIFICATION_ATTEMPTS}")
        print(f"Код из кеша: {cached_code}")
        
        if cached_code is None or cached_code != code:
            raise InvalidVerificationCodeError()
        print(f"Код {code} действителен для email {email}")
        await self.redis.delete(self._email_code_cache_key(email))


class MailService(MailServicePort):
    def __init__(self, sender_email: str, sender_password: str):
        self.sender_email = sender_email
        self.sender_password = sender_password

    async def send_email(self, email: str, code: str) -> None:
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = email
        message["Subject"] = "Подтверждение регистрации на DefendFlow"
        body = f"Код подтверждения: {code}"
        message.attach(MIMEText(body, "plain"))

        # Отправка
        try:
            print(f"Отправляем код {code} на email {email}")
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(message)
            server.quit()
            print("Письмо успешно отправлено!")
        except Exception as e:
            print(f"Ошибка: {e}")



class MailServiceMock(MailServicePort):
    def __init__(self, sender_email: str, sender_password: str):
        self.sender_email = sender_email
        self.sender_password = sender_password

    async def send_email(self, email: str, code: str) -> None:
        print(f"Mock send email to {email} with code {code}")
