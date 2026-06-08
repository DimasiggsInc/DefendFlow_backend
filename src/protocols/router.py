import uuid
from typing import List

from fastapi import APIRouter, Depends, status


from src.protocols.schemas import FinalScoreSchema, GradeCreateRequest, GradeSchema, GradeUpdateRequest, ProtocolCreateRequest, ProtocolPdfUpdateRequest, ProtocolSchema
from src.auth.dependencies import get_current_user
from src.users.schemas import CurrentUser


grades_router = APIRouter(prefix="/defense/grades", tags=["Grades"])


@grades_router.post("", response_model=GradeSchema, status_code=status.HTTP_201_CREATED)
async def submit_grade(
    grade_data: GradeCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Поставить оценку проекту."""
    pass


@grades_router.put("/{grade_id}", response_model=GradeSchema)
async def update_grade(
    grade_id: uuid.UUID,
    grade_data: GradeUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Изменить оценку (только свою или Admin)."""
    pass


@grades_router.get("/registration/{registration_id}", response_model=List[GradeSchema])
async def get_registration_grades(
    registration_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить все оценки команды."""
    pass


@grades_router.get("/expert/{expert_id}", response_model=List[GradeSchema])
async def get_expert_grades(
    expert_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить все оценки эксперта (Admin или свой expert_id)."""
    pass


final_score_router = APIRouter(prefix="/defense/final-scores", tags=["Final Scores"])


@final_score_router.get("/registration/{registration_id}", response_model=FinalScoreSchema)
async def get_registration_final_score(
    registration_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить итоговый балл команды."""
    pass


@final_score_router.post("/registration/{registration_id}/recalculate", response_model=FinalScoreSchema)
async def recalculate_final_score(
    registration_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Пересчитать итоговый балл (Admin only)."""
    pass


protocols_router = APIRouter(prefix="/defense/protocols", tags=["Protocols"])


@protocols_router.get("/slot/{slot_id}", response_model=List[ProtocolSchema])
async def get_slot_protocols(
    slot_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить все протоколы слота."""
    pass


@protocols_router.get("/{protocol_id}", response_model=ProtocolSchema)
async def get_protocol_info(
    protocol_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить информацию о протоколе."""
    pass


@protocols_router.post("", response_model=ProtocolSchema, status_code=status.HTTP_201_CREATED)
async def create_protocol(
    protocol_data: ProtocolCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Создать протокол защиты (Admin only)."""
    pass


@protocols_router.put("/{protocol_id}/pdf", response_model=ProtocolSchema)
async def upload_protocol_pdf(
    protocol_id: uuid.UUID,
    pdf_data: ProtocolPdfUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Загрузить PDF протокола (Admin only)."""
    pass
