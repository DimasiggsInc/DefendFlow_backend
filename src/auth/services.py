import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import secrets

from src.auth.interfaces import HasherPort, AuthRepositoryPort, AuthServicePort, JWTServicePort, MailServicePort
from src.users.schemas import UserAuthenticationRequest, UserAuthenticationResponse
from src.auth.exceptions import InvalidVerificationCodeError, TooManyVerificationAttemptsError, VerificationCodeNotFoundError 
from src.users.exceptions import UserNotFoundError, IncorrectPasswordError

from redis.asyncio import Redis

from src.config import settings



class AuthService(AuthServicePort):
    def __init__(self, hasher: HasherPort, auth_repository: AuthRepositoryPort, jwt_util: JWTServicePort, redis: Redis, mail_service: MailServicePort):
        self.hasher = hasher
        self.auth_repository = auth_repository
        self.jwt_util = jwt_util
        self.redis = redis
        self.mail_service = mail_service
        self.MAX_VERIFICATION_ATTEMPTS = settings.MAX_VERIFICATION_ATTEMPTS

    async def register(self, user: UserAuthenticationRequest) -> UserAuthenticationResponse:
        salt = self.hasher.salt
        hashed_password = self.hasher.encode(user.password, salt)

        user_id = await self.auth_repository.add_user(user.email, hashed_password, salt)

        jwt_token = self.jwt_util.encode(user_id)

        return UserAuthenticationResponse(token=jwt_token, refresh_token="lol")

    async def login(self, user: UserAuthenticationRequest) -> UserAuthenticationResponse:
        try:
            user_id = await self.auth_repository.get_id_by_email(user.email)
        except ValueError:
            raise UserNotFoundError()

        salt = await self.auth_repository.get_user_salt(user_id)
        hashed_password = await self.auth_repository.get_user_hashed_password(user_id)
        
        if not self.hasher.verify(user.password, salt, hashed_password):
            raise IncorrectPasswordError()
        
        
        jwt_token = self.jwt_util.encode(user_id)

        return UserAuthenticationResponse(token=jwt_token, refresh_token="lol")
    
    async def get_user_by_email(self, email: str) -> str | None:
        try:
            user_id = await self.auth_repository.get_id_by_email(email)
            return user_id
        except ValueError:
            return None

    async def send_email_code(self, email: str) -> None:
        code = str(secrets.randbelow(900000) + 100000)
        await self.mail_service.send_email(email, code)

        key = f"email_code:{email}"
        async with self.redis.pipeline() as pipe:
            await pipe.hset(key, mapping={"code": code, "attempts": 0})
            await pipe.expire(key, settings.EMAIL_CODE_CACHE_TTL)
            await pipe.execute()

    async def verify_email_code(self, email: str, code: str) -> None:
        key = f"email_code:{email}"
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
        await self.redis.delete(f"email_code:{email}")



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
