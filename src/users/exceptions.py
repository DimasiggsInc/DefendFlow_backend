from src.exceptions import AppException
from fastapi import status


class UserNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "USR_001"
    message = "User not found"


class EmailAlreadyExistsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "USR_002"
    message = "Email already registered"
