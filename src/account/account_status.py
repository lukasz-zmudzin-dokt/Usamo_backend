from enum import Enum

class AccountStatus(Enum):
    VERIFIED = 1
    WAITING_FOR_VERIFICATION = 2
    NOT_VERIFIED = 3

ACCOUNT_STATUS_CHOICES = [
    (AccountStatus.VERIFIED.value, 'Verified'),
    (AccountStatus.WAITING_FOR_VERIFICATION.value, 'Waiting for verification'),
    (AccountStatus.NOT_VERIFIED.value, 'Not verified')
]

STATUS_CHOICES_VERBOSE = [
    ('Verified', 'Verified'),
    ('Waiting for verification', 'Waiting for verification'),
    ('Not verified', 'Not verified')
]

STATUS_TO_INT_MAP = {
    'Verified': 1,
    'Waiting for verification': 2,
    'Not verified': 3
}