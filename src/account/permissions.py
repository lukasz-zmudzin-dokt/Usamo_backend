from abc import abstractmethod

from rest_framework import permissions

from .account_status import AccountStatus
from .account_type import AccountType, StaffGroupType


class AbstractIsUserOrAllowedStaffPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return user and user.status == AccountStatus.VERIFIED.value \
               and (self._is_allowed_staff(user) or self._is_user_allowed(user))

    def _is_allowed_staff(self, user) -> bool:
        staff_type = self._get_allowed_staff_type().value
        return user.type == AccountType.STAFF.value and user.groups.filter(name=staff_type).exists()

    def _is_user_allowed(self, user) -> bool:
        return user.type == (self._get_user_type()).value

    @abstractmethod
    def _get_allowed_staff_type(self):
        return

    @abstractmethod
    def _get_user_type(self):
        return


class IsEmployerOrAllowedStaff(AbstractIsUserOrAllowedStaffPermission):
    message = {'errors': 'User is neither an employer nor staff'}

    def _get_allowed_staff_type(self):
        return StaffGroupType.STAFF_JOBS

    def _get_user_type(self):
        return AccountType.EMPLOYER

    def has_object_permission(self, request, view, obj):
        if request.user.type == AccountType.EMPLOYER.value:
            return obj.employer.id == request.user.id if hasattr(obj, 'employer') else False
        return super()._is_allowed_staff(request.user)


class AbstractCanStaffVerifyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        allowed_type = self._get_staff_type().value
        user = request.user
        return user and user.type == AccountType.STAFF.value \
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
