from abc import abstractmethod

from rest_framework import permissions

from .account_status import AccountStatus
from .account_type import AccountType, StaffGroupType


class AbstractIsAllowedStaff(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return user and not user.is_anonymous and user.status == AccountStatus.VERIFIED.value and self._is_allowed_staff(user)

    def _is_allowed_staff(self, user) -> bool:
        staff_group_type = self._get_allowed_staff_type().value
        return user.type == AccountType.STAFF.value and user.groups.filter(name=staff_group_type).exists()

    @abstractmethod
    def _get_allowed_staff_type(self):
        return


class AbstractIsAllowedUser(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return user and not user.is_anonymous and user.status == AccountStatus.VERIFIED.value and self._is_user_allowed(user)

    def _is_user_allowed(self, user) -> bool:
        return user.type == (self._get_allowed_user_type()).value

    @abstractmethod
    def _get_allowed_user_type(self):
        return


class IsEmployer(AbstractIsAllowedUser):

    def _get_allowed_user_type(self):
        return AccountType.EMPLOYER

    def has_object_permission(self, request, view, obj):
        if request.user.type == AccountType.EMPLOYER.value:
            return obj.employer.user_id == request.user.id if hasattr(obj, 'employer') else False


class IsStaffResponsibleForJobs(AbstractIsAllowedStaff):

    def _get_allowed_staff_type(self):
        return StaffGroupType.STAFF_JOBS

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'employer')


class AbstractCanStaffVerifyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        allowed_type = self._get_staff_type().value
        user = request.user
        return user and not user.is_anonymous and user.type == AccountType.STAFF.value \
               and user.status == AccountStatus.VERIFIED.value \
               and user.groups.filter(name=allowed_type).exists()

    @abstractmethod
    def _get_staff_type(self) -> StaffGroupType:
        pass


class CanStaffVerifyCV(AbstractCanStaffVerifyPermission):

    def _get_staff_type(self):
        return StaffGroupType.STAFF_CV


class CanStaffVerifyUsers(AbstractCanStaffVerifyPermission):

    def _get_staff_type(self):
        return StaffGroupType.STAFF_VERIFICATION
