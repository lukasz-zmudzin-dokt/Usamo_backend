from account.account_type import StaffGroupType
from account.permissions import AbstractIsAllowedStaff


class IsStaffStepsModerator(AbstractIsAllowedStaff):

    def _get_allowed_staff_type(self):
        return StaffGroupType.STAFF_BLOG_MODERATOR
