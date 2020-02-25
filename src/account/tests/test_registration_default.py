from .test_registration import RegistrationTestCase
from rest_framework import status
from ..account_status import AccountStatus
from ..account_type import AccountType, ACCOUNT_TYPE_CHOICES
from ..models import DefaultAccount


class DefaultRegistrationTestCase(RegistrationTestCase):

    url = '/account/register/'

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

