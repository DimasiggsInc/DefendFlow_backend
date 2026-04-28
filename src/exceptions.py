from fastapi import status
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
