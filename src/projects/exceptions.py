from fastapi import status
from src.exceptions import AppException


class ProjectNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "PRJ_001"
    message = "Project not found"

class ProjectLinkNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "PRJ_002"
    message = "Project link not found"

class ProjectMemberNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "PRJ_003"
    message = "Project member not found"
