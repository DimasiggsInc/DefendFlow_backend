from src.database import Base  # noqa

# 1. Сначала базовые пользователи
from src.users.models import User  # noqa
from src.admins.models import Admin  # noqa
from src.students.models import Student  # noqa
from src.experts.models import Expert  # noqa
from src.curators.models import Curator  # noqa

# 2. Затем проекты (зависят от пользователей/кураторов)
from src.projects.models import Project, ProjectMember, ProjectLink  # noqa

# 3. ЗАТЕМ расписание (DefenseSlot, DefenseRoom). 
# Важно: они должны быть определены ДО регистраций!
from src.defense.models import DefenseSlot, DefenseRoom, SlotToRoom  # noqa

# 4. И только потом регистрации (которые ссылаются на defense_room и defense_slot)
from src.registrations.models import StudentRegistration, ExpertRegistration  # noqa

# 5. Оценки и протоколы
from src.grading.models import Grade, FinalScore  # noqa
from src.protocols.models import Protocol  # noqa