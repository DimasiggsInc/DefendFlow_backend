from typing import List
from uuid import UUID
from datetime import date

from src.admins.repositories import AdminRepository
from src.defense.interfaces import DefenseRoomRepositoryPort, DefenseSlotRepositoryPort
from src.defense.models import DefenseRoom, DefenseSlot
from src.defense.schemas import DefenseRoomCreateRequest, DefenseRoomSchema, DefenseRoomUpdateRequest, DefenseSlotCreateRequest, DefenseSlotFullSchema, DefenseSlotSchema, DefenseSlotUpdateRequest, SlotToRoomSchema


# ==================== EXCEPTIONS ====================
class DomainNotFoundError(Exception):
    """Базовое исключение для отсутствующих сущностей."""
    pass

class RoomNotFoundError(DomainNotFoundError): ...
class SlotNotFoundError(DomainNotFoundError): ...
class AdminNotFoundError(DomainNotFoundError): ...

# ==================== DEFENSE ROOM SERVICE ====================
class DefenseRoomService:
    def __init__(
        self, 
        room_repo: DefenseRoomRepositoryPort,
        admin_repo: AdminRepository
    ):
        self.room_repo = room_repo
        self.admin_repo = admin_repo

    async def get_all_rooms(self) -> List[DefenseRoomSchema]:
        rooms = await self.room_repo.get_all_rooms()
        return [DefenseRoomSchema.model_validate(room) for room in rooms]

    async def get_room_info(self, room_id: UUID) -> DefenseRoomSchema:
        room = await self.room_repo.get_room_by_id(room_id)
        if not room:
            raise RoomNotFoundError(f"Аудитория с ID {room_id} не найдена")
        return DefenseRoomSchema.model_validate(room)

    async def create_room(self, data: DefenseRoomCreateRequest, user_id: UUID) -> DefenseRoomSchema:
        """
        Создать комнату. 
        user_id - это ID из таблицы users (из токена current_user.id)
        """
        # Сначала находим админа по user_id
        admin = await self.admin_repo.get_admin_by_user_id(user_id)
        if not admin:
            raise AdminNotFoundError(f"Пользователь с ID {user_id} не является администратором")
        
        # Теперь используем admin.id (а не user_id)
        room_dict = data.model_dump()
        room_dict["admin_id"] = admin.id
        
        room = DefenseRoom(**room_dict)
        created_room = await self.room_repo.create_room(room)
        return DefenseRoomSchema.model_validate(created_room)

    async def update_room(self, room_id: UUID, data: DefenseRoomUpdateRequest) -> DefenseRoomSchema:
        room = await self.room_repo.get_room_by_id(room_id)
        if not room:
            raise RoomNotFoundError(f"Аудитория с ID {room_id} не найдена")

        # Обновляем только явно переданные поля
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(room, field, value)

        updated_room = await self.room_repo.update_room(room)
        return DefenseRoomSchema.model_validate(updated_room)

    async def delete_room(self, room_id: UUID) -> None:
        room = await self.room_repo.get_room_by_id(room_id)
        if not room:
            raise RoomNotFoundError(f"Аудитория с ID {room_id} не найдена")
        await self.room_repo.delete_room(room_id)


# ==================== DEFENSE SLOT SERVICE ====================
class DefenseSlotService:
    def __init__(self, slot_repo: DefenseSlotRepositoryPort):
        self.slot_repo = slot_repo

    async def get_available_slots(self, date_from: date, date_to: date) -> List[DefenseSlotSchema]:
        """
        Возвращает слоты, в которых остались свободные места для студентов.
        Примечание: Для production рекомендуется вынести подсчёт записей в отдельный 
        метод репозитория (SELECT COUNT) во избежание N+1 запросов.
        """
        slots = await self.slot_repo.get_all_slots(date_from, date_to)
        available_slots = []
        
        for slot in slots:
            # Проверка доступности (упрощённая)
            # В реальном проекте лучше использовать агрегирующий запрос в репозитории
            registered_count = len(getattr(slot, "student_registrations", []))
            if registered_count < slot.max_customers:
                available_slots.append(DefenseSlotSchema.model_validate(slot))
                
        return available_slots

    async def get_slot_info(self, slot_id: UUID) -> DefenseSlotFullSchema:
        slot = await self.slot_repo.get_slot_with_details(slot_id)
        if not slot:
            raise SlotNotFoundError(f"Слот с ID {slot_id} не найден")

        # Извлекаем связанные данные
        rooms = [link.room for link in slot.slot_to_rooms]
        projects_count = len(slot.student_registrations)
        experts_count = len(slot.expert_registrations)

        schema = DefenseSlotFullSchema.model_validate(slot)
        schema.rooms = [DefenseRoomSchema.model_validate(r) for r in rooms]
        schema.registered_projects_count = projects_count
        schema.registered_experts_count = experts_count
        return schema

    async def create_slot(self, data: DefenseSlotCreateRequest) -> DefenseSlotSchema:
        slot = DefenseSlot(**data.model_dump())
        created_slot = await self.slot_repo.create_slot(slot)
        return DefenseSlotSchema.model_validate(created_slot)

    async def update_slot(self, slot_id: UUID, data: DefenseSlotUpdateRequest) -> DefenseSlotSchema:
        slot = await self.slot_repo.get_slot_by_id(slot_id)
        if not slot:
            raise SlotNotFoundError(f"Слот с ID {slot_id} не найден")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(slot, field, value)

        updated_slot = await self.slot_repo.update_slot(slot)
        return DefenseSlotSchema.model_validate(updated_slot)

    async def delete_slot(self, slot_id: UUID) -> None:
        slot = await self.slot_repo.get_slot_by_id(slot_id)
        if not slot:
            raise SlotNotFoundError(f"Слот с ID {slot_id} не найден")
        await self.slot_repo.delete_slot(slot_id)

    async def assign_room(self, slot_id: UUID, room_id: UUID) -> SlotToRoomSchema:
        slot = await self.slot_repo.get_slot_by_id(slot_id)
        if not slot:
            raise SlotNotFoundError(f"Слот с ID {slot_id} не найден")
            
        # Создание связи (репозиторий сам проверит существование комнаты через FK)
        link = await self.slot_repo.assign_room_to_slot(slot_id, room_id)
        return SlotToRoomSchema.model_validate(link)

    async def remove_room(self, slot_id: UUID, room_id: UUID) -> None:
        slot = await self.slot_repo.get_slot_by_id(slot_id)
        if not slot:
            raise SlotNotFoundError(f"Слот с ID {slot_id} не найден")
            
        await self.slot_repo.remove_room_from_slot(slot_id, room_id)
