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