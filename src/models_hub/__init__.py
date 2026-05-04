from src.database import Base

# 1. Сначала базовые пользователи
from src.users.models import User
from src.admins.models import Admin
from src.students.models import Student
from src.experts.models import Expert
from src.curators.models import Curator

# 2. Затем проекты (зависят от пользователей/кураторов)
from src.projects.models import Project, ProjectMember, ProjectLink

# 3. ЗАТЕМ расписание (DefenseSlot, DefenseRoom). 
# Важно: они должны быть определены ДО регистраций!
from src.defense.models import DefenseSlot, DefenseRoom, SlotToRoom

# 4. И только потом регистрации (которые ссылаются на defense_room и defense_slot)
from src.registrations.models import StudentRegistration, ExpertRegistration

# 5. Оценки и протоколы
from src.grading.models import Grade, FinalScore
from src.protocols.models import Protocol