from enum import Enum


class AccountType(Enum):
    STANDARD = 1
    STAFF = 2
    EMPLOYER = 3


ACCOUNT_TYPE_CHOICES = [
    (AccountType.STANDARD.value, 'standard'),
    (AccountType.STAFF.value, 'staff'),
    (AccountType.EMPLOYER.value, 'employer')
]

TYPE_CHOICES_VERBOSE = [
    ('standard', 'standard'),
    ('staff', 'staff'),
    ('employer', 'employer')
]

TYPE_TO_INT_MAP = {
    'standard': 1,
    'staff': 2,
    'employer': 3
}

class StaffGroupType(Enum):
    STAFF_VERIFICATION = 'staff_verification'
    STAFF_CV = 'staff_cv'
    STAFF_JOBS = 'staff_jobs'
    STAFF_BLOG_CREATOR = 'staff_blog_creator'
    STAFF_BLOG_MODERATOR = 'staff_blog_moderator'

    @staticmethod
    def get_all_types():
        return [e.value for e in StaffGroupType]


STAFF_GROUP_CHOICES = [
    (StaffGroupType.STAFF_VERIFICATION.value, 'staff_verification'),
    (StaffGroupType.STAFF_CV.value, 'staff_cv'),
    (StaffGroupType.STAFF_JOBS.value, 'staff_jobs'),
    (StaffGroupType.STAFF_BLOG_CREATOR.value, 'staff_blog_creator'),
    (StaffGroupType.STAFF_BLOG_MODERATOR.value, 'staff_blog_moderator')
]
