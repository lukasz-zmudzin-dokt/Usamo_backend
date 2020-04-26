from rest_framework import permissions

from account.account_type import StaffGroupType
from account.permissions import AbstractIsAllowedStaff
from account.account_status import AccountStatus
from datetime import datetime, timezone, timedelta


class IsStaffBlogCreator(AbstractIsAllowedStaff):

    def _get_allowed_staff_type(self):
        return StaffGroupType.STAFF_BLOG_CREATOR

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'author') and obj.author.user_id == request.user.id


class IsStaffBlogModerator(AbstractIsAllowedStaff):

    def _get_allowed_staff_type(self):
        return StaffGroupType.STAFF_BLOG_MODERATOR

    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and hasattr(obj, 'author')


class IsUserCommentAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.status == AccountStatus.VERIFIED.value

    def has_object_permission(self, request, view, obj):
        now = datetime.now(timezone.utc)
        then = obj.date_created
        diff = now - then
        max_diff = timedelta(minutes=1)
        return obj.author.id == request.user.id if hasattr(obj, 'author') and diff < max_diff else False
