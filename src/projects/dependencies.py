from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.projects.repositories import ProjectRepository
from src.projects.services import ProjectService
from src.projects.models import Project

async def get_project_repo(session: AsyncSession = Depends(get_session)) -> ProjectRepository:
    return ProjectRepository(model=Project, session=session)

async def get_project_service(repo: ProjectRepository = Depends(get_project_repo)) -> ProjectService:
    return ProjectService(project_repo=repo)
