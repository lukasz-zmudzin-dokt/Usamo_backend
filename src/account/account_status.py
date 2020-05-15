from enum import Enum

class AccountStatus(Enum):
    VERIFIED = 1
    WAITING_FOR_VERIFICATION = 2
    REJECTED = 3
    BLOCKED = 4

ACCOUNT_STATUS_CHOICES = [
    (AccountStatus.VERIFIED.value, 'Verified'),
    (AccountStatus.WAITING_FOR_VERIFICATION.value, 'Waiting for verification'),
    (AccountStatus.REJECTED.value, 'Rejected'),
    (AccountStatus.BLOCKED.value, 'Blocked')
]

STATUS_CHOICES_VERBOSE = [
    ('Verified', 'Verified'),
    ('Waiting for verification', 'Waiting for verification'),
    ('Rejected', 'Rejected'),
    ('Blocked', 'Blocked')
]

STATUS_TO_INT_MAP = {
    'Verified': 1,
    'Waiting for verification': 2,
    'Rejected': 3,
    'Blocked': 4
}