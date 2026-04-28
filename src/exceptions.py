from fastapi import HTTPException, status
from typing import Any, Optional


class AppException(Exception):
    """Базовое доменное исключение. Не наследуется от HTTPException."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    message: str = "Internal server error"
    details: Optional[Any] = None

    def __init__(self, message: Optional[str] = None, details: Optional[Any] = None):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)

class HTTPAppException(AppException, HTTPException):
    """Мост для быстрых проверок в зависимостях. Лучше использовать чистые AppException."""
    def __init__(self, message: Optional[str] = None, details: Optional[Any] = None):
        AppException.__init__(self, message, details)
        HTTPException.__init__(self, status_code=self.status_code, detail=self.message)
