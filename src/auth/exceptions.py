from fastapi import status
from src.exceptions import AppException


class InvalidCredentialsError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "AUTH_001"
    message = "Invalid email or password"

class TooManyVerificationAttemptsError(AppException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "AUTH_002"
    message = "Too many verification attempts. Please try again later."

class InvalidVerificationCodeError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "AUTH_003"
    message = "Invalid verification code"

class VerificationCodeExpiredError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "AUTH_004"
    message = "Verification code expired"

class VerificationCodeNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "AUTH_005"
    message = "Verification code not found"
