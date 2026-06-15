from typing import List, Optional
from uuid import UUID
from datetime import date

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.defense.models import DefenseRoom, DefenseSlot, SlotToRoom


class DefenseSlotRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_slots(
        self, 
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None
    ) -> List[DefenseSlot]:
        query = (
            select(DefenseSlot)
            .options(
                selectinload(DefenseSlot.student_registrations),
                selectinload(DefenseSlot.expert_registrations)
            )
        )
        
        if date_from:
            query = query.where(DefenseSlot.date >= date_from)
        if date_to:
            query = query.where(DefenseSlot.date <= date_to)
            
        query = query.order_by(DefenseSlot.date, DefenseSlot.time_start)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_slot_by_id(self, slot_id: UUID) -> Optional[DefenseSlot]:
        query = select(DefenseSlot).where(DefenseSlot.id == slot_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_slot_with_details(self, slot_id: UUID) -> Optional[DefenseSlot]:
        """Слот со связанными аудиториями, записями студентов и экспертов."""
        query = (
            select(DefenseSlot)
            .options(
                # Загружаем связь слот-комната и саму комнату
                selectinload(DefenseSlot.slot_to_rooms).selectinload(SlotToRoom.room),
                # Загружаем регистрации
                selectinload(DefenseSlot.student_registrations),
                selectinload(DefenseSlot.expert_registrations)
            )
            .where(DefenseSlot.id == slot_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_slot(self, slot: DefenseSlot) -> DefenseSlot:
        self.session.add(slot)
        await self.session.flush()
        await self.session.refresh(slot)
        await self.session.commit()
        return slot

    async def update_slot(self, slot: DefenseSlot) -> DefenseSlot:
        # Предполагается, что объект slot уже изменен в сервисном слое.
        # Добавляем его в сессию (если он detached) и обновляем состояние.
        self.session.add(slot)
        await self.session.flush()
        await self.session.refresh(slot)
        await self.session.commit()
        return slot

    async def delete_slot(self, slot_id: UUID) -> None:
        # Примечание: Убедитесь, что в моделях настроен cascade="all, delete-orphan" 
        # для связанных записей, либо в БД настроен ON DELETE CASCADE, 
        # иначе возникнет ошибка нарушения целостности (ForeignKeyViolation).
        query = delete(DefenseSlot).where(DefenseSlot.id == slot_id)
        await self.session.execute(query)
        await self.session.commit()

    # === Связь Slot ↔ Room ===

    async def get_slot_rooms(self, slot_id: UUID) -> List[DefenseRoom]:
        query = (
            select(DefenseRoom)
            .join(SlotToRoom, DefenseRoom.id == SlotToRoom.defense_room_id)
            .where(SlotToRoom.defense_slot_id == slot_id)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def assign_room_to_slot(self, slot_id: UUID, room_id: UUID) -> SlotToRoom:
        # Проверяем, не назначена ли комната уже, чтобы избежать IntegrityError
        check_query = select(SlotToRoom).where(
            SlotToRoom.defense_slot_id == slot_id,
            SlotToRoom.defense_room_id == room_id
        )
        result = await self.session.execute(check_query)
        existing_link = result.scalar_one_or_none()
        
        if existing_link:
            return existing_link

        new_link = SlotToRoom(
            defense_slot_id=slot_id,
            defense_room_id=room_id
        )
        self.session.add(new_link)
        await self.session.flush()
        await self.session.refresh(new_link)
        await self.session.commit()
        return new_link

    async def remove_room_from_slot(self, slot_id: UUID, room_id: UUID) -> None:
        query = delete(SlotToRoom).where(
            SlotToRoom.defense_slot_id == slot_id,
            SlotToRoom.defense_room_id == room_id
        )
        await self.session.execute(query)
        await self.session.commit()


class DefenseRoomRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_rooms(self) -> List[DefenseRoom]:
        query = select(DefenseRoom).order_by(DefenseRoom.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_room_by_id(self, room_id: UUID) -> Optional[DefenseRoom]:
        query = select(DefenseRoom).where(DefenseRoom.id == room_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_room(self, room: DefenseRoom) -> DefenseRoom:
        self.session.add(room)
        await self.session.flush()
        await self.session.refresh(room)
        await self.session.commit()
        return room

    async def update_room(self, room: DefenseRoom) -> DefenseRoom:
        self.session.add(room)
        await self.session.flush()
        await self.session.refresh(room)
        await self.session.commit()
        return room

    async def delete_room(self, room_id: UUID) -> None:
        # Примечание: Аналогично слотам, убедитесь в наличии каскадного удаления 
        # для записей в SlotToRoom, Protocol, StudentRegistration, ExpertRegistration,
        # ссылающихся на эту комнату.
        query = delete(DefenseRoom).where(DefenseRoom.id == room_id)
        await self.session.execute(query)
        await self.session.commit()
