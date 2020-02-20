from rest_framework import status
from rest_framework.test import APITestCase
from .account_status import AccountStatus
from .account_type import AccountType, ACCOUNT_TYPE_CHOICES
from .models import DefaultAccount, EmployerAccount, StaffAccount, Account
import json
from django.test import SimpleTestCase
from .validators import validate_nip
from django.core.exceptions import ValidationError


class NIPTestCase(SimpleTestCase):

    def test_nip_validation_success(self):
        test_nip = '1234563218'
        try:
            validate_nip(test_nip)
        except ValidationError:
            self.fail('Raised an exception')

    def test_nip_validation_too_short(self):
        test_nip = '123456321'
        self.assertRaises(ValidationError, validate_nip, test_nip)

    def test_nip_too_long(self):
        test_nip = '12345632189'
        self.assertRaises(ValidationError, validate_nip, test_nip)

    def test_nip_contains_not_numbers(self):
        test_nip = '12345632hj'
        self.assertRaises(ValidationError, validate_nip, test_nip)

    def test_nip_check_sum_does_not_match(self):
        test_nip = '1234563216'
        self.assertRaises(ValidationError, validate_nip, test_nip)


class RegistrationTestCase(APITestCase):

    @staticmethod
    def read_test_data(filename):
        file_path = f'account/test_data/{filename}'
        with open(file_path) as file:
            data = json.load(file)
        return data

    @classmethod
    def setUp(cls):
        cls.url = '/account/register/'
        cls.employer_url = '/account/register/employer/'
        cls.staff_url = '/account/register/staff/'

    def test_registration_default_success(self):
        registration_data = self.read_test_data('default_success.json')
        self.assertEquals(DefaultAccount.objects.count(), 0)
        response = self.client.post(self.url, registration_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.__dict__['data']['type'], dict(ACCOUNT_TYPE_CHOICES)[AccountType.STANDARD.value])
        self.assertEquals(DefaultAccount.objects.count(), 1)
        account = DefaultAccount.objects.get()
        self.assertEquals(account.user.username, registration_data['username'])
        self.assertEquals(account.user.first_name, registration_data['first_name'])
        self.assertEquals(account.user.last_name, registration_data['last_name'])
        self.assertEquals(account.user.email, registration_data['email'])
        self.assertEquals(account.phone_number, registration_data['phone_number'])
        self.assertEquals(account.facility_address, registration_data['facility_address'])
        self.assertEquals(account.facility_name, registration_data['facility_name'])
        self.assertEquals(account.user.status, AccountStatus.WAITING_FOR_VERIFICATION.value)
        self.assertEquals(account.user.type, AccountType.STANDARD.value)
        self.assertNotEquals(account.user.password, '')
        self.assertNotEquals(account.user.password, registration_data['password'])

    def test_registration_default_invalid_phone(self):
        test_data = self.read_test_data('default_invalid_phone.json')
        response = self.client.post(self.url, test_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.content, b'{"phone_number":"Phone number is invalid"}')
        self.assertEquals(DefaultAccount.objects.count(), 0)

    def test_registration_default_missing_field(self):
        test_data = self.read_test_data('default_missing_fields.json')
        response = self.client.post(self.url, test_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEquals(DefaultAccount.objects.count(), 0)

    def test_registration_employer_success(self):
        registration_data = self.read_test_data('employer_success.json')
        self.assertEquals(EmployerAccount.objects.count(), 0)
        response = self.client.post(self.employer_url, registration_data, format='json')

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.__dict__['data']['type'], dict(ACCOUNT_TYPE_CHOICES)[AccountType.EMPLOYER.value])
        self.assertEquals(EmployerAccount.objects.count(), 1)
        account = EmployerAccount.objects.get()
        self.assertEquals(account.user.username, registration_data['username'])
        self.assertEquals(account.user.first_name, registration_data['first_name'])
        self.assertEquals(account.user.last_name, registration_data['last_name'])
        self.assertEquals(account.user.email, registration_data['email'])
        self.assertEquals(account.phone_number, registration_data['phone_number'])
        self.assertEquals(account.company_name, registration_data['company_name'])
        self.assertEquals(account.company_address, registration_data['company_address'])
        self.assertEquals(account.nip, registration_data['nip'])
        self.assertEquals(account.user.status, AccountStatus.WAITING_FOR_VERIFICATION.value)
        self.assertEquals(account.user.type, AccountType.EMPLOYER.value)
        self.assertNotEquals(account.user.password, '')
        self.assertNotEquals(account.user.password, registration_data['password'])

    def test_registration_employer_invalid_nip(self):
        test_data = self.read_test_data('employer_invalid_nip.json')
        response = self.client.post(self.employer_url, test_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(EmployerAccount.objects.count(), 0)

    def test_registration_employer_missing_fields(self):
        test_data = self.read_test_data('employer_missing_fields.json')
        response = self.client.post(self.employer_url, test_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEquals(EmployerAccount.objects.count(), 0)

    def test_registration_staff_success(self):
        registration_data = self.read_test_data('staff_success.json')
        self.assertEquals(StaffAccount.objects.count(), 0)
        response = self.client.post(self.staff_url, registration_data, format='json')

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.__dict__['data']['type'], dict(ACCOUNT_TYPE_CHOICES)[AccountType.STAFF.value])
        self.assertEquals(Account.objects.count(), 1)
        self.assertEquals(StaffAccount.objects.count(), 1)
        account = Account.objects.get()
        self.assertEquals(account.username, registration_data['username'])
        self.assertEquals(account.first_name, registration_data['first_name'])
        self.assertEquals(account.last_name, registration_data['last_name'])
        self.assertEquals(account.email, registration_data['email'])
        self.assertEquals(account.status, AccountStatus.VERIFIED.value)
        self.assertEquals(account.type, AccountType.STAFF.value)
        self.assertNotEquals(account.password, '')
        self.assertNotEquals(account.password, registration_data['password'])
