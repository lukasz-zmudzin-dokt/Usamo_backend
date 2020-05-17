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
    ('verified', 'Verified'),
    ('waiting_for_verification', 'Waiting for verification'),
    ('rejected', 'Rejected'),
    ('blocked', 'Blocked')
]

STATUS_TO_INT_MAP = {
    'verified': 1,
    'waiting_for_verification': 2,
    'rejected': 3,
    'blocked': 4
}