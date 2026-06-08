from datetime import date
from typing import List, Optional, Protocol
from uuid import UUID

from src.defense.schemas import DefenseRoomCreateRequest, DefenseRoomSchema, DefenseRoomUpdateRequest, DefenseSlotCreateRequest, DefenseSlotFullSchema, DefenseSlotSchema, DefenseSlotUpdateRequest, SlotToRoomSchema
from src.defense.models import DefenseRoom, DefenseSlot, SlotToRoom


class DefenseSlotRepositoryPort(Protocol):
    async def get_all_slots(
        self, 
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None
    ) -> List[DefenseSlot]:
        """Получить список слотов с фильтрацией по датам."""
        ...

    async def get_slot_by_id(self, slot_id: UUID) -> Optional[DefenseSlot]:
        ...

    async def get_slot_with_details(self, slot_id: UUID) -> Optional[DefenseSlot]:
        """Слот со связанными аудиториями, записями студентов и экспертов."""
        ...

    async def create_slot(self, slot: DefenseSlot) -> DefenseSlot:
        ...

    async def update_slot(self, slot: DefenseSlot) -> DefenseSlot:
        ...

    async def delete_slot(self, slot_id: UUID) -> None:
        ...

    # === Связь Slot ↔ Room ===
    async def get_slot_rooms(self, slot_id: UUID) -> List[DefenseRoom]:
        ...

    async def assign_room_to_slot(self, slot_id: UUID, room_id: UUID) -> SlotToRoom:
        ...

    async def remove_room_from_slot(self, slot_id: UUID, room_id: UUID) -> None:
        ...
    


class DefenseSlotServicePort(Protocol):
    async def get_available_slots(self, date_from: date, date_to: date) -> List[DefenseSlotSchema]:
        """Публичный список слотов для записи (с учётом свободных мест)."""
        ...

    async def get_slot_info(self, slot_id: UUID) -> DefenseSlotFullSchema:
        """Детальная информация о слоте: аудитории, записанные проекты, эксперты."""
        ...

    async def create_slot(self, data: DefenseSlotCreateRequest) -> DefenseSlotSchema:
        ...

    async def update_slot(self, slot_id: UUID, data: DefenseSlotUpdateRequest) -> DefenseSlotSchema:
        ...

    async def delete_slot(self, slot_id: UUID) -> None:
        ...

    async def assign_room(self, slot_id: UUID, room_id: UUID) -> SlotToRoomSchema:
        ...

    async def remove_room(self, slot_id: UUID, room_id: UUID) -> None:
        ...


class DefenseRoomRepositoryPort(Protocol):
    async def get_all_rooms(self) -> List[DefenseRoom]:
        ...

    async def get_room_by_id(self, room_id: UUID) -> Optional[DefenseRoom]:
        ...

    async def create_room(self, room: DefenseRoom) -> DefenseRoom:
        ...

    async def update_room(self, room: DefenseRoom) -> DefenseRoom:
        ...

    async def delete_room(self, room_id: UUID) -> None:
        ...



class DefenseRoomServicePort(Protocol):
    async def get_all_rooms(self) -> List[DefenseRoomSchema]:
        ...

    async def get_room_info(self, room_id: UUID) -> DefenseRoomSchema:
        ...

    async def create_room(self, data: DefenseRoomCreateRequest) -> DefenseRoomSchema:
        ...

    async def update_room(self, room_id: UUID, data: DefenseRoomUpdateRequest) -> DefenseRoomSchema:
        ...

    async def delete_room(self, room_id: UUID) -> None:
        ...
