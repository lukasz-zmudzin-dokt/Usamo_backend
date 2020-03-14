import unittest
from unittest.mock import Mock

from ..account_status import AccountStatus
from ..account_type import AccountType
from ..account_type import StaffGroupType
from ..permissions import CanStaffVerifyCV


class CanVerifyCVPermissionTest(unittest.TestCase):

    def setUp(self):
        self.permission = CanStaffVerifyCV()
        self.request = Mock()
        self.view = Mock()
        self.request.user = Mock()

    def tearDown(self) -> None:
        self.request.user.reset_mock()

    def test_user_is_staff_and_can_verify_cv(self):
        groups = Mock()
        groups.filter(name=StaffGroupType.STAFF_CV.value).exists.return_value = True
        self.request.user.configure_mock(type=AccountType.STAFF.value, status=AccountStatus.VERIFIED.value,
                                         groups=groups)
        self.assertTrue(self.permission.has_permission(self.request, self.view))

    def test_user_is_staff_and_can_not_verify_cv(self):
        groups = Mock()
        groups.filter(name=StaffGroupType.STAFF_CV.value).exists.return_value = False

        self.request.user.configure_mock(type=AccountType.STAFF.value, status=AccountStatus.VERIFIED.value,
                                         groups=groups)
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_user_is_staff_not_verified(self):
        self.request.user.configure_mock(type=AccountType.STAFF.value,
                                         status=AccountStatus.WAITING_FOR_VERIFICATION.value)
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_user_is_employer(self):
        self.request.user.configure_mock(type=AccountType.EMPLOYER.value, status=AccountStatus.VERIFIED.value)
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_user_is_default(self):
        self.request.user.configure_mock(type=AccountType.STANDARD.value, status=AccountStatus.VERIFIED.value)
        self.assertFalse(self.permission.has_permission(self.request, self.view))