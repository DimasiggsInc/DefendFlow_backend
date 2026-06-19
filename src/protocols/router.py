# src/grading/router.py

import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from src.registrations.repositories import DefenseRegistrationRepository
from src.protocols.schemas import (
    AvailableProjectForGradingResponse,
    FinalScoreSchema,
    GradeCreateRequest,
    GradeSchema,
    GradeUpdateRequest,
    ProtocolCreateRequest,
    ProtocolPdfUpdateRequest,
    ProtocolSchema
)
from src.auth.dependencies import get_current_user
from src.users.schemas import CurrentUser
from src.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.protocols.repositories import (
    GradeRepository,
    FinalScoreRepository,
    ProtocolRepository
)
from src.protocols.services import (
    DomainError,
    ExpertNotFoundError,
    ExpertNotRegisteredForSlotError,
    ExpertRegistrationNotFoundError,
    GradeService,
    FinalScoreService,
    ProtocolService,
    GradeNotFoundError,
    FinalScoreNotFoundError,
    ProtocolNotFoundError,
    AlreadyGradedError,
    PermissionDeniedError,
    AdminNotFoundError,
    RoomNotAssignedToSlotError,
    StudentRegistrationNotFoundError
)


# ==========================================
# DEPENDENCIES
# ==========================================

def get_grade_service(
    session: AsyncSession = Depends(get_session)
) -> GradeService:
    grade_repo = GradeRepository(session)
    return GradeService(grade_repo)


def get_final_score_service(
    session: AsyncSession = Depends(get_session)
) -> FinalScoreService:
    final_score_repo = FinalScoreRepository(session)
    grade_repo = GradeRepository(session)
    return FinalScoreService(final_score_repo, grade_repo)


def get_protocol_service(
    session: AsyncSession = Depends(get_session)
) -> ProtocolService:
    protocol_repo = ProtocolRepository(session)
    grade_repo = GradeRepository(session)
    registration_repo = DefenseRegistrationRepository(session)
    return ProtocolService(protocol_repo, grade_repo, registration_repo)


# ==========================================
# GRADES ROUTER
# ==========================================

grades_router = APIRouter(prefix="/defense/grades", tags=["Grades"])


@grades_router.get("/available-projects", response_model=List[AvailableProjectForGradingResponse])
async def get_available_projects_for_grading(
    current_user: CurrentUser = Depends(get_current_user),
    service: GradeService = Depends(get_grade_service),
):
    """
    Получить список проектов, которым текущий эксперт может поставить оценку.
    Исключает проекты, которые эксперт уже оценил.
    """
    return await service.get_available_projects_for_grading(current_user.id)


@grades_router.post("", response_model=GradeSchema, status_code=status.HTTP_201_CREATED)
async def submit_grade(
    grade_data: GradeCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: GradeService = Depends(get_grade_service),
):
    """
    Поставить оценку проекту.
    
    Передаётся только student_registration_id — ID записи проекта на защиту.
    expert_id определяется из токена.
    Проверяется, что эксперт зарегистрирован на этот же слот/аудиторию.
    """
    try:
        return await service.submit_grade(
            user_id=current_user.id,
            student_registration_id=grade_data.student_registration_id,
            score=grade_data.score,
            text_questions=grade_data.text_questions
        )
    except ExpertNotFoundError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except StudentRegistrationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ExpertNotRegisteredForSlotError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except AlreadyGradedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@grades_router.put("/{grade_id}", response_model=GradeSchema)
async def update_grade(
    grade_id: uuid.UUID,
    grade_data: GradeUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: GradeService = Depends(get_grade_service),
):
    """Изменить оценку (только свою или Admin)."""
    try:
        return await service.update_grade(
            grade_id=grade_id,
            user_id=current_user.id,
            score=grade_data.score,
            text_questions=grade_data.text_questions
        )
    except GradeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@grades_router.get("/registration/{registration_id}", response_model=List[GradeSchema])
async def get_registration_grades(
    registration_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: GradeService = Depends(get_grade_service),
):
    """Получить все оценки команды."""
    return await service.get_registration_grades(registration_id)


@grades_router.get("/expert/{expert_id}", response_model=List[GradeSchema])
async def get_expert_grades(
    expert_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: GradeService = Depends(get_grade_service),
):
    """Получить все оценки эксперта (Admin или свой expert_id)."""
    try:
        return await service.get_expert_grades(expert_id, current_user.id)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ExpertNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==========================================
# FINAL SCORES ROUTER
# ==========================================

final_score_router = APIRouter(prefix="/defense/final-scores", tags=["Final Scores"])


@final_score_router.get("/registration/{registration_id}", response_model=FinalScoreSchema)
async def get_registration_final_score(
    registration_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: FinalScoreService = Depends(get_final_score_service),
):
    """Получить итоговый балл команды."""
    try:
        return await service.get_registration_final_score(registration_id)
    except FinalScoreNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@final_score_router.post(
    "/registration/{registration_id}/recalculate",
    response_model=FinalScoreSchema
)
async def recalculate_final_score(
    registration_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: FinalScoreService = Depends(get_final_score_service),
):
    """Пересчитать итоговый балл (Admin only)."""
    try:
        return await service.recalculate_final_score(
            registration_id, current_user.id
        )
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# PROTOCOLS ROUTER
# ==========================================

protocols_router = APIRouter(prefix="/defense/protocols", tags=["Protocols"])


@protocols_router.get("/slot/{slot_id}", response_model=List[ProtocolSchema])
async def get_slot_protocols(
    slot_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProtocolService = Depends(get_protocol_service),
):
    """Получить все протоколы слота."""
    try:
        return await service.get_slot_protocols(slot_id, current_user.id)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@protocols_router.get("/{protocol_id}", response_model=ProtocolSchema)
async def get_protocol_info(
    protocol_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProtocolService = Depends(get_protocol_service),
):
    """Получить информацию о протоколе."""
    try:
        return await service.get_protocol_info(protocol_id, current_user.id)
    except ProtocolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@protocols_router.post("", response_model=ProtocolSchema, status_code=status.HTTP_201_CREATED)
async def create_protocol(
    protocol_data: ProtocolCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProtocolService = Depends(get_protocol_service),
):
    """Создать протокол защиты (Admin only). admin_id берется из токена."""
    try:
        return await service.create_protocol(
            user_id=current_user.id,
            defense_slot_id=protocol_data.defense_slot_id,
            defense_room_id=protocol_data.defense_room_id
        )
    except AdminNotFoundError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except RoomNotAssignedToSlotError as e:
        raise HTTPException(status_code=400, detail=str(e))


@protocols_router.put("/{protocol_id}/pdf", response_model=ProtocolSchema)
async def upload_protocol_pdf(
    protocol_id: uuid.UUID,
    pdf_data: ProtocolPdfUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProtocolService = Depends(get_protocol_service),
):
    """Загрузить PDF протокола (Admin only)."""
    try:
        return await service.upload_protocol_pdf(
            protocol_id=protocol_id,
            user_id=current_user.id,
            pdf_url=pdf_data.pdf_url
        )
    except ProtocolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))

@protocols_router.post("/{protocol_id}/generate", response_model=ProtocolSchema)
async def generate_protocol(
    protocol_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProtocolService = Depends(get_protocol_service),
):
    """
    Сгенерировать протокол защиты из шаблона DOCX.
    Создает файл и сохраняет путь в pdf_url.
    """
    try:
        await service.generate_protocol_document(
            protocol_id=protocol_id,
            user_id=current_user.id,
            template_path="./static/template.docx",
            output_dir="./static/protocols/"
        )
        # Возвращаем обновленный протокол
        return await service.get_protocol_info(protocol_id, current_user.id)
    except ProtocolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@protocols_router.get("/{protocol_id}/download")
async def download_protocol(
    protocol_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProtocolService = Depends(get_protocol_service),
):
    """Скачать сгенерированный протокол."""
    protocol = await service.protocol_repo.get_protocol_by_id(protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Протокол не найден")

    if not protocol.pdf_url:
        raise HTTPException(
            status_code=404,
            detail="Протокол еще не сгенерирован. Используйте POST /generate"
        )

    # Проверка прав
    is_admin = await service._is_user_admin(current_user.id)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Путь к файлу
    file_path = f".{protocol.pdf_url}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден на сервере")

    return FileResponse(
        path=file_path,
        filename=f"protocol_{protocol_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )