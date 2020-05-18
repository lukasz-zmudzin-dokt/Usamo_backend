from enum import Enum

class AccountStatus(Enum):
    VERIFIED = 1
    WAITING_FOR_VERIFICATION = 2
    REJECTED = 3
    BLOCKED = 4

ACCOUNT_STATUS_CHOICES = [
    (AccountStatus.VERIFIED.value, 'verified'),
    (AccountStatus.WAITING_FOR_VERIFICATION.value, 'waiting_for_verification'),
    (AccountStatus.REJECTED.value, 'rejected'),
    (AccountStatus.BLOCKED.value, 'blocked')
]

STATUS_CHOICES_VERBOSE = [
    ('verified', 'verified'),
    ('waiting_for_verification', 'waiting_for_verification'),
    ('rejected', 'rejected'),
    ('blocked', 'blocked')
]

STATUS_TO_INT_MAP = {
    'verified': 1,
    'waiting_for_verification': 2,
    'rejected': 3,
    'blocked': 4
}