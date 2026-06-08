import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from src.registrations.schemas import ExpertRegistrationCreateRequest, ExpertRegistrationSchema, RegistrationWithGradesSchema, StudentRegistrationCreateRequest, StudentRegistrationSchema
from src.auth.dependencies import get_current_user
from src.users.schemas import CurrentUser



registrations_student_router = APIRouter(prefix="/defense/registrations/student", tags=["Student Registrations"])


@registrations_student_router.get("", response_model=List[StudentRegistrationSchema])
async def get_my_project_registrations(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить все записи проектов текущего пользователя."""
    pass


@registrations_student_router.get("/{reg_id}", response_model=RegistrationWithGradesSchema)
async def get_student_registration_details(
    reg_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить детальную информацию о записи (с оценками)."""
    pass


@registrations_student_router.post("", response_model=StudentRegistrationSchema, status_code=status.HTTP_201_CREATED)
async def register_project_for_defense(
    reg_data: StudentRegistrationCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Записать проект на защиту."""
    pass


@registrations_student_router.delete("/{reg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_student_registration(
    reg_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Отменить запись проекта на защиту."""
    pass


@registrations_student_router.get("/project/{project_id}", response_model=List[StudentRegistrationSchema])
async def get_project_registrations(
    project_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить все записи конкретного проекта (Curator/Admin)."""
    pass


@registrations_student_router.get("/slot/{slot_id}", response_model=List[StudentRegistrationSchema])
async def get_slot_student_registrations(
    slot_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить все проекты, записанные на слот (Admin/Expert)."""
    pass


registrations_expert_router = APIRouter(prefix="/defense/registrations/expert", tags=["Expert Registrations"])


@registrations_expert_router.get("", response_model=List[ExpertRegistrationSchema])
async def get_my_expert_registrations(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить все записи текущего эксперта."""
    pass


@registrations_expert_router.get("/{reg_id}", response_model=ExpertRegistrationSchema)
async def get_expert_registration_details(
    reg_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить информацию о записи эксперта."""
    pass


@registrations_expert_router.post("", response_model=ExpertRegistrationSchema, status_code=status.HTTP_201_CREATED)
async def register_expert_for_defense(
    reg_data: ExpertRegistrationCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Записаться экспертом на защиту."""
    pass


@registrations_expert_router.delete("/{reg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_expert_registration(
    reg_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Отменить запись эксперта на защиту."""
    pass


@registrations_expert_router.get("/slot/{slot_id}", response_model=List[ExpertRegistrationSchema])
async def get_slot_experts(
    slot_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить список экспертов, записанных на слот (Admin)."""
    pass