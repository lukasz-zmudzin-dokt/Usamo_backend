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