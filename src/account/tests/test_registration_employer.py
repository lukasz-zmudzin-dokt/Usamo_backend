from rest_framework import status
from ..account_status import AccountStatus
from ..account_type import AccountType, ACCOUNT_TYPE_CHOICES
from account.models import EmployerAccount
from .test_registration import RegistrationTestCase


class EmployerRegistrationTestCase(RegistrationTestCase):
    url = '/account/register/employer/'

    def test_registration_employer_success(self):
        registration_data = self.read_test_data('employer_success.json')
        self.assertEquals(EmployerAccount.objects.count(), 0)
        response = self.client.post(self.url, registration_data, format='json')

        self.assertEquals(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        self.assertEquals(response.__dict__['data']['type'], dict(ACCOUNT_TYPE_CHOICES)[AccountType.EMPLOYER.value])
        self.assertEquals(EmployerAccount.objects.count(), 1)
        account = EmployerAccount.objects.get()
        self.assertEquals(account.user.username, registration_data['username'])
        self.assertEquals(account.user.first_name, registration_data['first_name'])
        self.assertEquals(account.user.last_name, registration_data['last_name'])
        self.assertEquals(account.user.email, registration_data['email'])
        self.assertEquals(account.phone_number, registration_data['phone_number'])
        self.assertEquals(account.company_name, registration_data['company_name'])
        self.assertEquals(account.nip, registration_data['nip'])
        self.assertEquals(account.user.status, AccountStatus.WAITING_FOR_VERIFICATION.value)
        self.assertEquals(account.user.type, AccountType.EMPLOYER.value)
        self.assertNotEquals(account.user.password, '')
        self.assertNotEquals(account.user.password, registration_data['password'])

    def test_registration_employer_invalid_nip(self):
        test_data = self.read_test_data('employer_invalid_nip.json')
        response = self.client.post(self.url, test_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)
        self.assertEquals(EmployerAccount.objects.count(), 0)

    def test_registration_employer_missing_fields(self):
        test_data = self.read_test_data('employer_missing_fields.json')
        response = self.client.post(self.url, test_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)
        self.assertEquals(EmployerAccount.objects.count(), 0)
