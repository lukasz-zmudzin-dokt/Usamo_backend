import unittest
from unittest.mock import Mock

from ..account_status import AccountStatus
from ..account_type import AccountType
from ..account_type import StaffType
from ..permissions import IsEmployerOrAdmin


class IsEmployerOrAdminPermissionTest(unittest.TestCase):

    def setUp(self):
        self.permission = IsEmployerOrAdmin()
        self.request = Mock()
        self.view = Mock()
        self.request.user = Mock()

    def test_user_is_verified_employer(self):
        self.request.user.configure_mock(type=AccountType.EMPLOYER.value, status=AccountStatus.VERIFIED.value)
        self.assertTrue(self.permission.has_permission(self.request, self.view))

    def test_user_is_verified_allowed_staff(self):
        groups = Mock()
        groups.filter(name=StaffType.STAFF_JOBS.value).exists.return_value = True
        self.request.user.configure_mock(type=AccountType.STAFF.value, status=AccountStatus.VERIFIED.value,
                                         groups=groups)
        self.assertTrue(self.permission.has_permission(self.request, self.view))

    def test_user_is_verified_not_allowed_staff(self):
        groups = Mock()
        groups.filter(name=StaffType.STAFF_JOBS.value).exists.return_value = False
        self.request.user.configure_mock(type=AccountType.STAFF.value, status=AccountStatus.VERIFIED.value,
                                         groups=groups)
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_user_is_verified_default(self):
        self.request.user.configure_mock(type=AccountType.STANDARD.value, status=AccountStatus.VERIFIED.value)
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_user_not_verified(self):
        for i in AccountType:
            self.request.user.reset_mock()
            self.request.user.configure_mock(type=i.value, status=AccountStatus.NOT_VERIFIED.value)
            self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_user_is_waiting_for_verification(self):
        for i in AccountType:
            self.request.user.reset_mock()
            self.request.user.configure_mock(type=i.value, status=AccountStatus.WAITING_FOR_VERIFICATION.value)
            self.assertFalse(self.permission.has_permission(self.request, self.view))
