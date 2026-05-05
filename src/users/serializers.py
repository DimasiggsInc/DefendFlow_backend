from src.users.interfaces import RoleSerializerPort
from src.users.schemas import UserWithAdmin, UserWithCurator, UserWithExpert, UserWithStudent
from src.users.models import User
from src.users.utils import register_role



@register_role("curator_profile")
class CuratorSerializer(RoleSerializerPort):
    def serialize(self, user: User) -> UserWithCurator:
        return UserWithCurator(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role="curator",
            profile=user.curator_profile
        )

@register_role("admin_profile")
class AdminSerializer(RoleSerializerPort):
    def serialize(self, user: User) -> UserWithAdmin:
        return UserWithAdmin(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role="admin",
            profile=user.admin_profile
        )


@register_role("student_profile")
class StudentSerializer(RoleSerializerPort):
    def serialize(self, user: User) -> UserWithStudent:
        return UserWithStudent(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role="student",
            profile=user.student_profile
        )


@register_role("expert_profile")
class ExpertSerializer(RoleSerializerPort):
    def serialize(self, user: User) -> UserWithExpert:
        return UserWithExpert(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role="expert",
            profile=user.expert_profile
        )
