from rest_framework import permissions

from .account_status import AccountStatus
from .account_type import AccountType, StaffType


class IsEmployerOrAllowedStaff(permissions.BasePermission):
    message = {'errors': 'User is neither an employer nor an admin'}

    def has_permission(self, request, view):
        user = request.user
        return user and user.status == AccountStatus.VERIFIED.value \
               and (self.__is_user_allowed_staff(user) or self.__is_user_employer(user))

    def has_object_permission(self, request, view, obj):
        user = request.user
        if self.__is_user_employer(user):
        ## TODO: check if the employer has created this job offer
            return False
        return True

    @staticmethod
    def __is_user_allowed_staff(user) -> bool:
        return user.type == AccountType.STAFF.value and user.groups.filter(name=StaffType.STAFF_JOBS.value).exists()

    @staticmethod
    def __is_user_employer(user) -> bool:
        return user.type == AccountType.EMPLOYER.value
