from rest_framework import permissions
from account.account_type import *
from account.permissions import AbstractIsAllowedStaff, IsStandardUser


class IsCVOwner(IsStandardUser):

    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and obj.cv_user.user_id == request.user.id \
            and hasattr(obj, 'cv_user') 


class IsStaffResponsibleForCVs(AbstractIsAllowedStaff):

    def _get_allowed_staff_type(self):
        return StaffGroupType.STAFF_CV

    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and hasattr(obj, 'cv_user')
