from fastapi import status
from src.exceptions import AppException


class UserNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "USR_001"
    message = "User not found"

class UserAlreadyExistsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "USR_002"
    message = "Email already registered"

class IncorrectPasswordError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "USR_003"
    message = "Incorrect password"

class AccessDeniedError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "USR_004"
    message = "Insufficient permissions"
