from rest_framework import permissions
from account.account_type import StaffGroupType
from account.permissions import AbstractIsAllowedStaff, IsStandardUser


class IsCVOwner(IsStandardUser):

    def has_object_permission(self, request, view, obj):
        if request.user.type == AccountType.STANDARD.value:
            return obj.cv_user.user_id == request.user.id if hasattr(obj, 'cv_user') else False


class IsStaffResponsibleForCVs(AbstractIsAllowedStaff):

    def _get_allowed_staff_type(self):
        return StaffGroupType.STAFF_CV

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'cv_user')
