from rest_framework import permissions

from account.account_type import StaffGroupType
from account.permissions import AbstractIsAllowedStaff


class IsStaffBlogCreator(AbstractIsAllowedStaff):

    def _get_allowed_staff_type(self):
        return StaffGroupType.STAFF_BLOG_CREATOR

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'author') and obj.author.user_id == request.user.id


class IsStaffBlogModerator(AbstractIsAllowedStaff):

    def _get_allowed_staff_type(self):
        return StaffGroupType.STAFF_BLOG_MODERATOR

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'author')