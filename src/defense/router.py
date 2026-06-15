import uuid
from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.admins.repositories import AdminRepository
from src.auth.dependencies import get_current_user
from src.users.schemas import CurrentUser
from src.database import get_session  # Ваша зависимость для получения AsyncSession

from src.defense.schemas import (
    DefenseRoomCreateRequest,
    DefenseRoomSchema, 
    DefenseRoomUpdateRequest,
    DefenseSlotCreateRequest,
    DefenseSlotSchema,
    DefenseSlotUpdateRequest,
    DefenseSlotWithRegistrationsSchema,
    SlotToRoomSchema
)

# Импортируйте ваши сервисы и исключения
from src.defense.services import AdminNotFoundError, DefenseSlotService, DefenseRoomService
from src.defense.services import SlotNotFoundError, RoomNotFoundError
from src.defense.repositories import DefenseSlotRepository, DefenseRoomRepository


# ==========================================
# DEPENDENCIES (Внедрение зависимостей)
# ==========================================

def get_slot_service(session: AsyncSession = Depends(get_session)) -> DefenseSlotService:
    """Фабрика для создания сервиса слотов."""
    repo = DefenseSlotRepository(session)
    return DefenseSlotService(repo)


def get_room_service(
    session: AsyncSession = Depends(get_session)
) -> DefenseRoomService:
    """Фабрика для создания сервиса аудиторий."""
    room_repo = DefenseRoomRepository(session)
    admin_repo = AdminRepository(session)  # Создаем репозиторий Admin
    return DefenseRoomService(room_repo, admin_repo)


# ==========================================
# DEFENSE SLOTS ROUTER
# ==========================================

slots_router = APIRouter(prefix="/defense/slots", tags=["Defense Slots"])


@slots_router.get("", response_model=List[DefenseSlotSchema])
async def get_available_slots(
    date_from: Optional[date] = Query(None, description="Start date filter"),
    date_to: Optional[date] = Query(None, description="End date filter"),
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseSlotService = Depends(get_slot_service),
):
    """Получить список доступных слотов для записи."""
    # Примечание: Если сервис строго требует non-optional date, 
    # здесь можно задать значения по умолчанию (например, date.today())
    return await service.get_available_slots(date_from, date_to)


@slots_router.get("/{slot_id}", response_model=DefenseSlotWithRegistrationsSchema)
async def get_slot_info(
    slot_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseSlotService = Depends(get_slot_service),
):
    """Получить детальную информацию о слоте."""
    try:
        return await service.get_slot_info(slot_id)
    except SlotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@slots_router.post("", response_model=DefenseSlotSchema, status_code=status.HTTP_201_CREATED)
async def create_slot(
    slot_data: DefenseSlotCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseSlotService = Depends(get_slot_service),
):
    """Создать новый слот защиты (Admin only)."""
    # Здесь можно добавить проверку: if not current_user.is_admin: raise HTTPException(403)
    return await service.create_slot(slot_data)


@slots_router.put("/{slot_id}", response_model=DefenseSlotSchema)
async def update_slot(
    slot_id: uuid.UUID,
    slot_data: DefenseSlotUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseSlotService = Depends(get_slot_service),
):
    """Обновить слот защиты (Admin only)."""
    try:
        return await service.update_slot(slot_id, slot_data)
    except SlotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@slots_router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slot(
    slot_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseSlotService = Depends(get_slot_service),
):
    """Удалить слот защиты (Admin only)."""
    try:
        await service.delete_slot(slot_id)
    except SlotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Slot to Room ---

@slots_router.get("/{slot_id}/rooms", response_model=List[DefenseRoomSchema])
async def get_slot_rooms(
    slot_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseSlotService = Depends(get_slot_service),
):
    """Получить аудитории, привязанные к слоту."""
    try:
        # Используем get_slot_info, так как он уже возвращает список комнат внутри схемы
        slot_details = await service.get_slot_info(slot_id)
        return slot_details.rooms
    except SlotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@slots_router.post("/{slot_id}/rooms", response_model=SlotToRoomSchema, status_code=status.HTTP_201_CREATED)
async def assign_room_to_slot(
    slot_id: uuid.UUID,
    room_id: uuid.UUID = Query(..., description="Room ID to assign"),
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseSlotService = Depends(get_slot_service),
):
    """Привязать аудиторию к слоту (Admin only)."""
    try:
        return await service.assign_room(slot_id, room_id)
    except SlotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e: # Ловим IntegrityError от БД, если room_id не существует
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный ID аудитории или она уже привяз")


@slots_router.delete("/{slot_id}/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_room_from_slot(
    slot_id: uuid.UUID,
    room_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseSlotService = Depends(get_slot_service),
):
    """Отвязать аудиторию от слота (Admin only)."""
    try:
        await service.remove_room(slot_id, room_id)
    except SlotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==========================================
# DEFENSE ROOMS ROUTER
# ==========================================

rooms_router = APIRouter(prefix="/defense/rooms", tags=["Defense Rooms"])


@rooms_router.get("", response_model=List[DefenseRoomSchema])
async def get_all_rooms(
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRoomService = Depends(get_room_service),
):
    """Получить список всех аудиторий."""
    return await service.get_all_rooms()


@rooms_router.get("/{room_id}", response_model=DefenseRoomSchema)
async def get_room_info(
    room_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRoomService = Depends(get_room_service),
):
    """Получить информацию об аудитории."""
    try:
        return await service.get_room_info(room_id)
    except RoomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@rooms_router.post("", response_model=DefenseRoomSchema, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: DefenseRoomCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRoomService = Depends(get_room_service),
):
    """Создать новую аудиторию (Admin only)."""
    try:
        # Передаем user_id (current_user.id), сервис сам найдет admin.id
        return await service.create_room(room_data, user_id=current_user.id)
    except AdminNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=str(e)
        )


@rooms_router.put("/{room_id}", response_model=DefenseRoomSchema)
async def update_room(
    room_id: uuid.UUID,
    room_data: DefenseRoomUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRoomService = Depends(get_room_service),
):
    """Обновить аудиторию (Admin only)."""
    try:
        return await service.update_room(room_id, room_data)
    except RoomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@rooms_router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DefenseRoomService = Depends(get_room_service),
):
    """Удалить аудиторию (Admin only)."""
    try:
        await service.delete_room(room_id)
    except RoomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
