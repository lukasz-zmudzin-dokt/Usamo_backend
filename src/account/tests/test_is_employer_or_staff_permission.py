import unittest
from unittest.mock import Mock

from ..account_status import AccountStatus
from ..account_type import AccountType
from ..account_type import StaffGroupType
from ..permissions import IsEmployer, IsStaffResponsibleForJobs


class IsEmployerOrAdminPermissionTest(unittest.TestCase):

    def setUp(self):
        self.staff_permission = IsStaffResponsibleForJobs()
        self.employer_permission = IsEmployer()
        self.request = Mock()
        self.view = Mock()
        self.request.user = Mock()

    def test_user_is_verified_employer(self):
        self.request.user.configure_mock(type=AccountType.EMPLOYER.value, status=AccountStatus.VERIFIED.value,
                                         is_anonymous=False)
        self.assertTrue(self.employer_permission.has_permission(self.request, self.view))

    def test_user_is_verified_allowed_staff(self):
        groups = Mock()
        groups.filter(name=StaffGroupType.STAFF_JOBS.value).exists.return_value = True
        self.request.user.configure_mock(type=AccountType.STAFF.value, status=AccountStatus.VERIFIED.value,
                                         groups=groups, is_anonymous=False)
        self.assertTrue(self.staff_permission.has_permission(self.request, self.view))

    def test_user_is_verified_not_allowed_staff(self):
        groups = Mock()
        groups.filter(name=StaffGroupType.STAFF_JOBS.value).exists.return_value = False
        self.request.user.configure_mock(type=AccountType.STAFF.value, status=AccountStatus.VERIFIED.value,
                                         groups=groups)
        self.assertFalse(self.staff_permission.has_permission(self.request, self.view))

    def test_user_is_verified_default(self):
        self.request.user.configure_mock(type=AccountType.STANDARD.value, status=AccountStatus.VERIFIED.value)
        self.assertFalse(self.staff_permission.has_permission(self.request, self.view))
        self.assertFalse(self.employer_permission.has_permission(self.request, self.view))

    def test_user_not_verified(self):
        for i in AccountType:
            self.request.user.reset_mock()
            self.request.user.configure_mock(type=i.value, status=AccountStatus.REJECTED.value)
            self.assertFalse(self.employer_permission.has_permission(self.request, self.view))
            self.assertFalse(self.staff_permission.has_permission(self.request, self.view))

    def test_user_is_waiting_for_verification(self):
        for i in AccountType:
            self.request.user.reset_mock()
            self.request.user.configure_mock(type=i.value, status=AccountStatus.WAITING_FOR_VERIFICATION.value)
            self.assertFalse(self.employer_permission.has_permission(self.request, self.view))
            self.assertFalse(self.staff_permission.has_permission(self.request, self.view))

    def test_an_object_has_not_employer_attr(self):
        offer = Mock()
        del offer.employer
        self.request.user.configure_mock(type=AccountType.EMPLOYER.value, status=AccountStatus.VERIFIED.value,
                                         is_anonymous=False)
        self.assertTrue(self.employer_permission.has_permission(self.request, self.view))
        self.assertFalse(self.employer_permission.has_object_permission(self.request, self.view, offer))
        self.assertFalse(self.staff_permission.has_object_permission(self.request, self.view, offer))

    def test_an_offer_belongs_to_the_employer(self):
        offer = Mock()
        self.request.user.configure_mock(type=AccountType.EMPLOYER.value, status=AccountStatus.VERIFIED.value,
                                         is_anonymous=False)
        offer.employer.configure_mock(user_id=self.request.user.id)
        self.assertTrue(self.employer_permission.has_permission(self.request, self.view))
        self.assertTrue(self.employer_permission.has_object_permission(self.request, self.view, offer))
        groups = Mock()
        self.request.user.configure_mock(type=AccountType.STAFF.value, status=AccountStatus.VERIFIED.value,
                                         groups=groups, is_anonymous=False)
        self.assertTrue(self.staff_permission.has_object_permission(self.request, self.view, offer))

    def test_an_offer_does_not_belong_to_the_employer(self):
        offer = Mock()
        another_employer = Mock()
        offer.configure_mock(employer=another_employer)
        self.request.user.configure_mock(type=AccountType.EMPLOYER.value, status=AccountStatus.VERIFIED.value,
                                         is_anonymous=False)
        offer.configure_mock(employer=another_employer)
        self.assertTrue(self.employer_permission.has_permission(self.request, self.view))
        self.assertFalse(self.employer_permission.has_object_permission(self.request, self.view, offer))
        groups = Mock()
        self.request.user.configure_mock(type=AccountType.STAFF.value, status=AccountStatus.VERIFIED.value,
                                         groups=groups, is_anonymous=False)
        self.assertTrue(self.staff_permission.has_object_permission(self.request, self.view, offer))

    def test_allowed_staff_has_an_access_to_the_offer(self):
        offer = Mock()
        employer = Mock()
        offer.configure_mock(employer=employer)
        groups = Mock()
        groups.filter(name=StaffGroupType.STAFF_JOBS.value).exists.return_value = True
        self.request.user.configure_mock(type=AccountType.STAFF.value, status=AccountStatus.VERIFIED.value,
                                         groups=groups, is_anonymous=False)

        self.assertTrue(self.staff_permission.has_permission(self.request, self.view))

    def test_staff_has_no_access_to_the_offer(self):
        offer = Mock()
        employer = Mock()
        offer.configure_mock(employer=employer)
        groups = Mock()
        groups.filter(name=StaffGroupType.STAFF_JOBS.value).exists.return_value = False
        self.request.user.configure_mock(type=AccountType.STAFF.value, status=AccountStatus.VERIFIED.value,
                                         groups=groups)
        self.assertFalse(self.staff_permission.has_permission(self.request, self.view))
