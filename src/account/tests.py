# Create your tests here.
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from account.account_status import AccountStatus
from account.models import Account


class RegistrationTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/account/register/'
        cls.registration_data = {
            'username': 'testusername',
            'email': 'test@email.com',
            'password': 'testpassword',
            'first_name': 'testname',
            'last_name': 'testlastname',
            'phone_number': '+48123456789',
            'facility_name': 'test facility name',
            'facility_address': 'testState, testStreet testNum'
        }


    def test_registration_success(self):
        self.assertEquals(Account.objects.count(), 0)
        response = self.client.post(self.url, self.registration_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self.assertEquals(Account.objects.count(), 1)
        self.assertEquals(Account.objects.get().user.username, self.registration_data['username'])
        self.assertEquals(Account.objects.get().user.first_name, self.registration_data['first_name'])
        self.assertEquals(Account.objects.get().user.last_name, self.registration_data['last_name'])
        self.assertEquals(Account.objects.get().user.email, self.registration_data['email'])
        self.assertEquals(Account.objects.get().phone_number, self.registration_data['phone_number'])
        self.assertEquals(Account.objects.get().facility_address, self.registration_data['facility_address'])
        self.assertEquals(Account.objects.get().facility_name, self.registration_data['facility_name'])
        self.assertEquals(Account.objects.get().status, AccountStatus.WAITING_FOR_VERIFICATION.value)

        self.assertNotEquals(Account.objects.get().user.password, '')
        self.assertNotEquals(Account.objects.get().user.password, self.registration_data['password'])



    def test_registration_username_exists(self):
        self.assertEquals(Account.objects.count(), 0)
        User.objects.create_user(self.registration_data['username'], '', '')
        self.assertEquals(Account.objects.count(), 1)

        response = self.client.post(self.url, self.registration_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEquals(response.content, b'{"username":["A user with that username already exists."]}')


    def test_registration_missing_field(self):
        for key in self.registration_data.keys():
            reg_data_with_missing_field = {k: v for (k, v) in self.registration_data.items() if k != key}
            response = self.client.post(self.url, reg_data_with_missing_field, format='json')
            self.assertContains(response, text=f'{key}', status_code=status.HTTP_406_NOT_ACCEPTABLE)
            self.assertContains(response, text='is required', status_code=status.HTTP_406_NOT_ACCEPTABLE)


    def test_registration_invalid_phone_number(self):
        invalid_phone_numbers = ['fdgdf', '+48qwertyghjk', '+481234567890', '+48h123456789', '123456789',
                                 '456', '1345678']
        for pn in invalid_phone_numbers:
            self.registration_data['phone_number'] = pn
            response = self.client.post(self.url, self.registration_data, format='json')
            self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEquals(response.content, b'{"phone_number":"Phone number is invalid"}')


