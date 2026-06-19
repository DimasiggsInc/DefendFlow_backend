# src/grading/services.py

import os
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pathlib import Path

from docxtpl import DocxTemplate

from sqlalchemy import select


from src.admins.models import Admin
from src.registrations.models import StudentRegistration
from src.defense.models import DefenseRoom, DefenseSlot
from src.registrations.repositories import DefenseRegistrationRepository
from src.protocols.schemas import (
    AvailableProjectForGradingResponse,
    GradeSchema,
    GradeCreateRequest,
    GradeUpdateRequest,
    FinalScoreSchema,
    ProtocolSchema,
    ProtocolCreateRequest,
    ProtocolPdfUpdateRequest
)
from src.grading.models import Grade, FinalScore
from src.protocols.models import Protocol
from src.protocols.repositories import (
    GradeRepository,
    FinalScoreRepository,
    ProtocolRepository
)
from src.experts.models import Expert
from src.utils import get_user_full_name


# ============ EXCEPTIONS ============

class DomainError(Exception):
    pass

class GradeNotFoundError(DomainError): ...
class FinalScoreNotFoundError(DomainError): ...
class ProtocolNotFoundError(DomainError): ...
class ExpertNotFoundError(DomainError): ...
class AdminNotFoundError(DomainError): ...
class AlreadyGradedError(DomainError): ...
class PermissionDeniedError(DomainError): ...
class RoomNotAssignedToSlotError(DomainError): ...
class ExpertRegistrationNotFoundError(DomainError): ...
class StudentRegistrationNotFoundError(DomainError): ...
class ExpertNotRegisteredForSlotError(DomainError): ...



# ============ GRADE SERVICE ============
class GradeService:
    def __init__(self, grade_repo: GradeRepository):
        self.grade_repo = grade_repo

    async def submit_grade(
        self,
        user_id: UUID,
        student_registration_id: UUID,
        score: float,
        text_questions: Optional[str] = None
    ) -> GradeSchema:
        # 1. Найти эксперта по user_id
        expert = await self._get_expert_by_user_id(user_id)

        # 2. Найти запись проекта на защиту
        student_reg = await self.grade_repo.get_student_registration_by_id(
            student_registration_id
        )
        if not student_reg:
            raise StudentRegistrationNotFoundError(
                f"Запись проекта с ID {student_registration_id} не найдена"
            )

        # 3. Проверить, что эксперт зарегистрирован на этот же слот+комнату
        expert_reg = await self.grade_repo.get_expert_registration_by_expert_and_slot_room(
            expert_id=expert.id,
            slot_id=student_reg.defense_slot_id,
            room_id=student_reg.defense_room_id
        )
        if not expert_reg:
            raise ExpertNotRegisteredForSlotError(
                "Эксперт не зарегистрирован на эту защиту (слот/аудитория)"
            )

        # 4. Проверить дубликат
        if await self.grade_repo.is_expert_already_graded(
            expert.id, student_registration_id
        ):
            raise AlreadyGradedError(
                "Эксперт уже поставил оценку этому проекту"
            )

        # 5. Создать оценку
        grade = Grade(
            expert_id=expert.id,
            student_registration_id=student_registration_id,
            score=int(score),
            text_questions=text_questions
        )
        created_grade = await self.grade_repo.create_grade(grade)
        
        grade_with_relations = await self.grade_repo.get_grade_by_id(created_grade.id)
        return self._to_grade_schema(grade_with_relations)

    async def update_grade(
        self,
        grade_id: UUID,
        user_id: UUID,
        score: Optional[float] = None,
        text_questions: Optional[str] = None
    ) -> GradeSchema:
        grade = await self.grade_repo.get_grade_by_id(grade_id)
        if not grade:
            raise GradeNotFoundError(f"Оценка с ID {grade_id} не найдена")

        # Проверка прав
        is_owner = grade.expert.user_id == user_id
        is_admin = await self._is_user_admin(user_id)

        if not (is_owner or is_admin):
            raise PermissionDeniedError(
                "Только автор оценки или администратор может её изменить"
            )

        if score is not None:
            grade.score = int(score)
        if text_questions is not None:
            grade.text_questions = text_questions

        await self.grade_repo.update_grade(grade)
        
        #  ПЕРЕЗАГРУЗИТЬ с eager-loaded связями
        updated_grade = await self.grade_repo.get_grade_by_id(grade.id)
        return self._to_grade_schema(updated_grade)

    async def get_registration_grades(
        self, registration_id: UUID
    ) -> List[GradeSchema]:
        """Получить все оценки команды."""
        grades = await self.grade_repo.get_grades_by_registration(registration_id)
        return [self._to_grade_schema(g) for g in grades]

    async def get_expert_grades(
        self, expert_id: UUID, user_id: UUID
    ) -> List[GradeSchema]:
        """Получить все оценки эксперта."""
        expert = await self._get_expert_by_id(expert_id)
        is_owner = expert.user_id == user_id
        is_admin = await self._is_user_admin(user_id)

        if not (is_owner or is_admin):
            raise PermissionDeniedError(
                "Доступ запрещен. Только админ или владелец эксперта."
            )

        grades = await self.grade_repo.get_grades_by_expert(expert_id)
        return [self._to_grade_schema(g) for g in grades]

    async def get_available_projects_for_grading(
        self, user_id: UUID
    ) -> List[AvailableProjectForGradingResponse]:
        """
        Получить список проектов для выставления оценок.
        Возвращает только те проекты, которые:
        1. Защищаются в то же время и в той же аудитории, где зарегистрирован эксперт.
        2. Ещё не были оценены этим экспертом.
        """
        # 1. Находим эксперта по user_id
        from sqlalchemy import select
        query = select(Expert).where(Expert.user_id == user_id)
        result = await self.grade_repo.session.execute(query)
        expert = result.scalar_one_or_none()

        if not expert:
            return []  # Если пользователь не эксперт, возвращаем пустой список

        # 2. Получаем доступные регистрации
        regs = await self.grade_repo.get_available_student_registrations_for_expert(expert.id)

        # 3. Маппинг в схему
        return [self._map_to_available_project(r) for r in regs]

    # ============ HELPERS ============
    
    def _map_to_available_project(self, reg: StudentRegistration) -> AvailableProjectForGradingResponse:
        return AvailableProjectForGradingResponse(
            student_registration_id=reg.id,
            project_id=reg.project_id,
            project_name=reg.project.name if reg.project else "Без названия",
            defense_date=reg.slot.date if reg.slot else None,
            defense_time_start=reg.slot.time_start if reg.slot else None,
            room_name=reg.room.name if reg.room else "Без аудитории"
        )

    async def _get_expert_by_user_id(self, user_id: UUID) -> Expert:
        query = select(Expert).where(Expert.user_id == user_id)
        result = await self.grade_repo.session.execute(query)
        expert = result.scalar_one_or_none()
        if not expert:
            raise ExpertNotFoundError(
                f"Пользователь {user_id} не является экспертом"
            )
        return expert

    async def _get_expert_by_id(self, expert_id: UUID) -> Expert:
        query = select(Expert).where(Expert.id == expert_id)
        result = await self.grade_repo.session.execute(query)
        expert = result.scalar_one_or_none()
        if not expert:
            raise ExpertNotFoundError(f"Эксперт с ID {expert_id} не найден")
        return expert

    async def _is_user_admin(self, user_id: UUID) -> bool:
        query = select(Admin.id).where(Admin.user_id == user_id)
        result = await self.grade_repo.session.execute(query)
        return result.scalar_one_or_none() is not None

    def _to_grade_schema(self, grade: Grade) -> GradeSchema:
        schema = GradeSchema.model_validate(grade)
        if grade.expert:
            # 🔥 Передаем expert, helper сам найдет expert.user
            schema.expert_name = get_user_full_name(grade.expert)
        return schema

# ============ FINAL SCORE SERVICE ============

class FinalScoreService:
    def __init__(
        self,
        final_score_repo: FinalScoreRepository,
        grade_repo: GradeRepository
    ):
        self.final_score_repo = final_score_repo
        self.grade_repo = grade_repo

    async def get_registration_final_score(
        self, registration_id: UUID
    ) -> FinalScoreSchema:
        """Получить итоговый балл команды."""
        score = await self.final_score_repo.get_final_score_by_registration(
            registration_id
        )
        if not score:
            raise FinalScoreNotFoundError(
                f"Итоговый балл для регистрации {registration_id} не найден"
            )
        return FinalScoreSchema.model_validate(score)

    async def recalculate_final_score(
        self, registration_id: UUID, user_id: UUID
    ) -> FinalScoreSchema:
        """
        Пересчитать итоговый балл (Admin only).
        Формула: среднее арифметическое всех оценок.
        """
        # Проверка прав админа
        if not await self._is_user_admin(user_id):
            raise PermissionDeniedError(
                "Только администратор может пересчитывать итоговый балл"
            )

        # Получить все оценки
        grades = await self.grade_repo.get_grades_by_registration(registration_id)
        if not grades:
            raise DomainError("Нет оценок для пересчета")

        # Вычислить средний балл
        total_score = sum(g.score for g in grades) / len(grades)

        # Создать или обновить итоговый балл
        existing_score = await self.final_score_repo.get_final_score_by_registration(
            registration_id
        )

        if existing_score:
            existing_score.total_score = total_score
            existing_score.calculated_at = datetime.now()
            updated_score = await self.final_score_repo.update_final_score(
                existing_score
            )
        else:
            new_score = FinalScore(
                student_registration_id=registration_id,
                total_score=total_score
            )
            updated_score = await self.final_score_repo.create_final_score(
                new_score
            )

        return FinalScoreSchema.model_validate(updated_score)

    async def _is_user_admin(self, user_id: UUID) -> bool:
        from sqlalchemy import select
        from src.admins.models import Admin
        query = select(Admin.id).where(Admin.user_id == user_id)
        result = await self.final_score_repo.session.execute(query)
        return result.scalar_one_or_none() is not None


# ============ PROTOCOL SERVICE ============

class ProtocolService:
    def __init__(
        self,
        protocol_repo: ProtocolRepository,
        grade_repo: GradeRepository,
        registration_repo: DefenseRegistrationRepository
    ):
        self.protocol_repo = protocol_repo
        self.grade_repo = grade_repo
        self.registration_repo = registration_repo

    async def get_slot_protocols(
        self, slot_id: UUID, user_id: UUID
    ) -> List[ProtocolSchema]:
        """Получить все протоколы слота (Admin или Expert)."""
        # Проверка прав
        is_admin = await self._is_user_admin(user_id)
        is_expert = await self._is_user_expert(user_id)

        if not (is_admin or is_expert):
            raise PermissionDeniedError(
                "Доступ запрещен. Требуются права администратора или эксперта."
            )

        protocols = await self.protocol_repo.get_protocols_by_slot(slot_id)
        return [ProtocolSchema.model_validate(p) for p in protocols]

    async def get_protocol_info(
        self, protocol_id: UUID, user_id: UUID
    ) -> ProtocolSchema:
        """Получить информацию о протоколе."""
        protocol = await self.protocol_repo.get_protocol_by_id(protocol_id)
        if not protocol:
            raise ProtocolNotFoundError(
                f"Протокол с ID {protocol_id} не найден"
            )

        # Проверка прав
        is_admin = await self._is_user_admin(user_id)
        is_expert = await self._is_user_expert(user_id)

        if not (is_admin or is_expert):
            raise PermissionDeniedError("Доступ запрещен")

        return ProtocolSchema.model_validate(protocol)

    async def create_protocol(
        self,
        user_id: UUID,
        defense_slot_id: UUID,
        defense_room_id: UUID
    ) -> ProtocolSchema:
        """Создать протокол защиты (Admin only)."""
        # Проверка прав админа
        admin = await self.protocol_repo.get_admin_by_user_id(user_id)
        if not admin:
            raise AdminNotFoundError(
                "Только администратор может создавать протоколы"
            )

        # Проверка, что комната привязана к слоту
        if not await self.protocol_repo.is_room_assigned_to_slot(
            defense_slot_id, defense_room_id
        ):
            raise RoomNotAssignedToSlotError(
                f"Аудитория {defense_room_id} не привязана к слоту {defense_slot_id}"
            )

        # Создать протокол
        protocol = Protocol(
            admin_id=admin.id,
            defense_slot_id=defense_slot_id,
            defense_room_id=defense_room_id
        )
        created_protocol = await self.protocol_repo.create_protocol(protocol)
        return ProtocolSchema.model_validate(created_protocol)

    async def upload_protocol_pdf(
        self,
        protocol_id: UUID,
        user_id: UUID,
        pdf_url: str
    ) -> ProtocolSchema:
        """Загрузить PDF протокола (Admin only)."""
        # Проверка прав админа
        if not await self._is_user_admin(user_id):
            raise PermissionDeniedError(
                "Только администратор может загружать PDF протокола"
            )

        protocol = await self.protocol_repo.get_protocol_by_id(protocol_id)
        if not protocol:
            raise ProtocolNotFoundError(
                f"Протокол с ID {protocol_id} не найден"
            )

        protocol.pdf_url = pdf_url
        updated_protocol = await self.protocol_repo.update_protocol(protocol)
        return ProtocolSchema.model_validate(updated_protocol)

    async def _is_user_admin(self, user_id: UUID) -> bool:
        from sqlalchemy import select
        from src.admins.models import Admin
        query = select(Admin.id).where(Admin.user_id == user_id)
        result = await self.protocol_repo.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def _is_user_expert(self, user_id: UUID) -> bool:
        from sqlalchemy import select
        from src.experts.models import Expert
        query = select(Expert.id).where(Expert.user_id == user_id)
        result = await self.protocol_repo.session.execute(query)
        return result.scalar_one_or_none() is not None


    async def generate_protocol_document(
        self,
        protocol_id: UUID,
        user_id: UUID,
        template_path: str = "../server/static/template.docx",
        output_dir: str = "./static/protocols/"
    ) -> str:
        """
        Сгенерировать протокол защиты из шаблона DOCX.
        Возвращает путь к сгенерированному файлу.
        """
        # 1. Проверка прав админа
        if not await self._is_user_admin(user_id):
            raise PermissionDeniedError(
                "Только администратор может генерировать протоколы"
            )

        # 2. Получить протокол
        protocol = await self.protocol_repo.get_protocol_by_id(protocol_id)
        if not protocol:
            raise ProtocolNotFoundError(
                f"Протокол с ID {protocol_id} не найден"
            )

        # 3. Собрать данные для шаблона
        data = await self._collect_protocol_data(protocol)

        # 4. Сгенерировать документ
        output_path = await self._render_docx(
            data=data,
            template_path=template_path,
            output_dir=output_dir,
            protocol_id=protocol_id
        )

        # 5. Обновить pdf_url в БД (относительный путь)
        protocol.pdf_url = f"/static/protocols/{protocol_id}.docx"
        await self.protocol_repo.update_protocol(protocol)

        return output_path

    async def _collect_protocol_data(self, protocol: Protocol) -> dict:
        """Собрать все данные для генерации протокола из БД."""
        slot_id = protocol.defense_slot_id
        room_id = protocol.defense_room_id

        # Получить слот и комнату
        slot = await self._get_slot(slot_id)
        room = await self._get_room(room_id)

        # Получить все регистрации на этот слот
        registrations = await self.registration_repo.get_student_registrations(
            defense_slot_id=slot_id
        )
        # Фильтруем по комнате
        registrations = [r for r in registrations if r.defense_room_id == room_id]

        all_students = []
        all_groups = []
        all_questions = []
        all_expert_grades = []
        topics = []

        for reg in registrations:
            project = reg.project
            if not project:
                continue

            topics.append(project.name)

            for member in (project.members or []):
                student = member.student
                if student:
                    # 🔥 Передаем student, helper сам найдет student.user
                    student_name = get_user_full_name(student)
                    all_students.append(student_name)

                    group = getattr(student, 'academ_group', None)
                    if group:
                        all_groups.append(group)

            for grade in (reg.grades or []):
                expert = grade.expert
                # 🔥 Передаем expert, helper сам найдет expert.user
                expert_name = get_user_full_name(expert)
                all_expert_grades.append({
                    'name': expert_name,
                    'score': grade.score
                })

                if grade.text_questions:
                    all_questions.append(grade.text_questions)

        # Имя админа
        admin = await self.protocol_repo.get_admin_by_id(protocol.admin_id)
        # 🔥 Передаем admin, helper сам найдет admin.user
        admin_name = get_user_full_name(admin)

        return {
            'topic': '; '.join(topics) if topics else 'Не указана',
            'students': list(set(all_students)),
            'groups': list(set(all_groups)),
            'clients': all_expert_grades,
            'experts': all_expert_grades,
            'questions': all_questions,
            'summary': '',
            'admin_name': admin_name,
            'date': slot.date.strftime('%d.%m.%Y') if slot.date else datetime.now().strftime('%d.%m.%Y')
        }
    
    async def _render_docx(
        self,
        data: dict,
        template_path: str,
        output_dir: str,
        protocol_id: UUID
    ) -> str:
        """Отрендерить DOCX из шаблона."""
        # Проверка существования шаблона
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Шаблон не найден: {template_path}")

        # Создание директории вывода
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        output_path = os.path.join(output_dir, f"{protocol_id}.docx")

        # Генерация документа
        doc = DocxTemplate(template_path)

        # Расчет средних баллов
        avg_client = 0.0
        avg_expert = 0.0

        if data['clients']:
            avg_client = sum(c['score'] for c in data['clients']) / len(data['clients'])
        if data['experts']:
            avg_expert = sum(e['score'] for e in data['experts']) / len(data['experts'])

        final_score = round(0.5 * avg_client + 0.5 * avg_expert, 2)

        context = {
            'topic': data['topic'],
            'students': ', '.join(data['students']),
            'groups': ', '.join(data['groups']),
            'clients': data['clients'],
            'experts': data['experts'],
            'avg_expert': round(avg_expert, 2),
            'avg_client': round(avg_client, 2),
            'final_score': final_score,
            'questions': "\n".join(data['questions']),
            'summary': data.get('summary', ''),
            'admin_name': data['admin_name'],
            'date': data['date']
        }

        doc.render(context)
        doc.save(output_path)

        return output_path

    # Вспомогательные методы
    async def _get_slot(self, slot_id: UUID) -> DefenseSlot:
        query = select(DefenseSlot).where(DefenseSlot.id == slot_id)
        result = await self.protocol_repo.session.execute(query)
        slot = result.scalar_one_or_none()
        if not slot:
            raise DomainError(f"Слот с ID {slot_id} не найден")
        return slot

    async def _get_room(self, room_id: UUID) -> DefenseRoom:
        query = select(DefenseRoom).where(DefenseRoom.id == room_id)
        result = await self.protocol_repo.session.execute(query)
        room = result.scalar_one_or_none()
        if not room:
            raise DomainError(f"Комната с ID {room_id} не найдена")
        return room

    async def _is_user_admin(self, user_id: UUID) -> bool:
        from sqlalchemy import select
        from src.admins.models import Admin
        query = select(Admin.id).where(Admin.user_id == user_id)
        result = await self.protocol_repo.session.execute(query)
        return result.scalar_one_or_none() is not None
