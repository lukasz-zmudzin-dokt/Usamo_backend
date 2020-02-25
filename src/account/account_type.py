from enum import Enum

class AccountType(Enum):
    STANDARD = 1
    STAFF = 2
    EMPLOYER = 3

ACCOUNT_TYPE_CHOICES = [
    (AccountType.STANDARD.value, 'Standard'),
    (AccountType.STAFF.value, 'Staff'),
    (AccountType.EMPLOYER.value, 'Employer')
]


class StaffType(Enum):
    STAFF_VERIFICATION = 'staff_verification'
    STAFF_CV = 'staff_cv'
    STAFF_JOBS = 'staff_jobs'

    @staticmethod
    def get_all_types():
        return [StaffType.STAFF_VERIFICATION.value, StaffType.STAFF_CV.value, StaffType.STAFF_JOBS.value]

