# src/registrations/router.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.registrations.schemas import (
    ExpertRegistrationCreateRequest,
    ExpertRegistrationSchema,
    RegistrationWithGradesSchema,
    StudentRegistrationCreateRequest,
    StudentRegistrationSchema
)
from src.auth.dependencies import get_current_user
from src.users.schemas import CurrentUser
from src.database import get_session

from src.registrations.services import (
    DefenseRegistrationService,
    ExpertNotFoundError,
    RegistrationNotFoundError,
    SlotNotFoundError,
    SlotFullError,
    ProjectAlreadyRegisteredError,
    ExpertAlreadyRegisteredError,
    RoomNotAssignedToSlotError,
    PermissionDeniedError,
    ProjectMemberNotInProjectError
)
from src.registrations.repositories import DefenseRegistrationRepository
from src.defense.repositories import DefenseSlotRepository


# ==========================================
# DEPENDENCIES
# ==========================================

def get_registration_service(
    session: AsyncSession = Depends(get_session)
) -> DefenseRegistrationService:
    """Фабрика для создания сервиса регистраций."""
    registration_repo = DefenseRegistrationRepository(session)
    slot_repo = DefenseSlotRepository(session)
    return DefenseRegistrationService(registration_repo, slot_repo)


# ==========================================
# STUDENT REGISTRATIONS ROUTER
# ==========================================

registrations_student_router = APIRouter(
    prefix="/defense/registrations/student",
    tags=["Student Registrations"]
)


@registrations_student_router.get("", response_model=List[StudentRegistrationSchema])
async def get_my_project_registrations(
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Получить все записи проектов текущего пользователя."""
    return await service.get_my_project_registrations(current_user.id)


@registrations_student_router.get("/project/{project_id}", response_model=List[StudentRegistrationSchema])
async def get_project_registrations(
    project_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Получить все записи конкретного проекта (Curator/Admin)."""
    # Опционально: проверка прав доступа
    # if not current_user.is_admin and not current_user.is_curator:
    #     raise HTTPException(status_code=403, detail="Недостаточно прав")
    return await service.get_project_registrations(project_id)


@registrations_student_router.get("/slot/{slot_id}", response_model=List[StudentRegistrationSchema])
async def get_slot_student_registrations(
    slot_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Получить все проекты, записанные на слот (Admin/Expert)."""
    # Опционально: проверка прав доступа
    # if not current_user.is_admin and not current_user.is_expert:
    #     raise HTTPException(status_code=403, detail="Недостаточно прав")
    return await service.get_slot_registrations(slot_id)


@registrations_student_router.get("/{reg_id}", response_model=RegistrationWithGradesSchema)
async def get_student_registration_details(
    reg_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Получить детальную информацию о записи (с оценками)."""
    reg = await service.registration_repo.get_student_registration_with_details(reg_id)
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Регистрация с ID {reg_id} не найдена"
        )
    
    # Опционально: проверка прав доступа (только владелец или админ)
    # if reg.member.user_id != current_user.id and not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return RegistrationWithGradesSchema.model_validate(reg)


@registrations_student_router.post("", response_model=StudentRegistrationSchema, status_code=status.HTTP_201_CREATED)
async def register_project_for_defense(
    reg_data: StudentRegistrationCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Записать проект на защиту (автоматически определяется участник проекта)."""
    try:
        return await service.register_project_for_defense(
            project_id=reg_data.project_id,
            slot_id=reg_data.defense_slot_id,
            room_id=reg_data.defense_room_id,
            user_id=current_user.id  # передаем user_id вместо project_member_id
        )
    except SlotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RoomNotAssignedToSlotError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ProjectMemberNotInProjectError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))  # 403 вместо 400
    except ProjectAlreadyRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except SlotFullError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    

@registrations_student_router.delete("/{reg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_student_registration(
    reg_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Отменить запись проекта на защиту."""
    try:
        await service.cancel_student_registration(reg_id, current_user.id)
    except RegistrationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ==========================================
# EXPERT REGISTRATIONS ROUTER
# ==========================================

registrations_expert_router = APIRouter(
    prefix="/defense/registrations/expert",
    tags=["Expert Registrations"]
)


@registrations_expert_router.get("", response_model=List[ExpertRegistrationSchema])
async def get_my_expert_registrations(
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Получить все записи текущего эксперта."""
    return await service.get_my_expert_registrations(current_user.id)


@registrations_expert_router.get("/slot/{slot_id}", response_model=List[ExpertRegistrationSchema])
async def get_slot_experts(
    slot_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Получить список экспертов, записанных на слот (Admin)."""
    # Опционально: проверка прав доступа
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Недостаточно прав")
    return await service.get_slot_experts(slot_id)


@registrations_expert_router.get("/{reg_id}", response_model=ExpertRegistrationSchema)
async def get_expert_registration_details(
    reg_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Получить информацию о записи эксперта."""
    reg = await service.registration_repo.get_expert_registration_with_details(reg_id)
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Регистрация с ID {reg_id} не найдена"
        )
    
    # Опционально: проверка прав доступа
    # if reg.expert.user_id != current_user.id and not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return service._to_expert_schema(reg)

@registrations_expert_router.post("", response_model=ExpertRegistrationSchema, status_code=status.HTTP_201_CREATED)
async def register_expert_for_defense(
    reg_data: ExpertRegistrationCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Записаться экспертом на защиту (expert_id определяется автоматически из токена)."""
    try:
        return await service.register_expert_for_defense(
            user_id=current_user.id,  # передаем user_id вместо expert_id
            slot_id=reg_data.defense_slot_id,
            room_id=reg_data.defense_room_id,
            role=reg_data.role_at_registration
        )
    except ExpertNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except SlotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RoomNotAssignedToSlotError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExpertAlreadyRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except SlotFullError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@registrations_expert_router.delete("/{reg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_expert_registration(
    reg_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRegistrationService = Depends(get_registration_service),
):
    """Отменить запись эксперта на защиту."""
    try:
        await service.cancel_expert_registration(reg_id, current_user.id)
    except RegistrationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
