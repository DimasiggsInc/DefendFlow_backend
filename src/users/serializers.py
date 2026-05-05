from src.users.interfaces import RoleSerializerPort
from src.users.schemas import UserWithAdmin, UserWithCurator, UserWithExpert, UserWithStudent
from src.users.models import User
from src.users.utils import register_role

from src.users.schemas import UserRolesEnum



@register_role(UserRolesEnum.CURATOR + "_profile")
class CuratorSerializer(RoleSerializerPort):
    def serialize(self, user: User) -> UserWithCurator:
        return UserWithCurator(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role=UserRolesEnum.CURATOR,
            profile=user.curator_profile
        )

@register_role(UserRolesEnum.ADMIN + "_profile")
class AdminSerializer(RoleSerializerPort):
    def serialize(self, user: User) -> UserWithAdmin:
        return UserWithAdmin(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role=UserRolesEnum.ADMIN,
            profile=user.admin_profile
        )


@register_role(UserRolesEnum.STUDENT + "_profile")
class StudentSerializer(RoleSerializerPort):
    def serialize(self, user: User) -> UserWithStudent:
        return UserWithStudent(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role=UserRolesEnum.STUDENT,
            profile=user.student_profile
        )


@register_role(UserRolesEnum.EXPERT + "_profile")
class ExpertSerializer(RoleSerializerPort):
    def serialize(self, user: User) -> UserWithExpert:
        return UserWithExpert(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role=UserRolesEnum.EXPERT,
            profile=user.expert_profile
        )
