# Create your tests here.
from unittest.mock import MagicMock

from account.account_status import AccountStatus
from account.models import Account, DefaultAccount, Address
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from cv import models
from cv.cv_test_data import cv_test_data, user_data
from cv.models import CV
from cv.models import BasicInfo
from cv.serializers import CVSerializer
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from django.db import models
import os


def create_user(username='testuser', verified=True):
    email = '%s@test.com' % username
    user = Account.objects.create_user(username=username, password='testuser', first_name='test',
                                       last_name='test', email=email)
    if verified:
        user.status=AccountStatus.VERIFIED.value
    return user


def create_default(user):
    address = Address.objects.create(
        city="Warszawa",
        street="Testowa",
        street_number="420",
        postal_code="69-420"
    )
    return DefaultAccount.objects.create(user=user, phone_number='+48123456789', facility_name='test facility',
                                         facility_address=address)


def create_mock_document():
    mock_file = MagicMock(spec=File)
    mock_file.name = 'TestFileName'
    mock_file.read.return_value = "fake file contents"
    return mock_file


def create_cv(user):
    cv_serializer = CVSerializer(data=cv_test_data)
    if cv_serializer.is_valid():
        cv_serializer.validated_data['cv_user'] = user
        cv = cv_serializer.create(cv_serializer.validated_data)
        return cv
    return None


class CVGeneratorTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = '/cv/generator/'
        cls.url_id = lambda self, id: '/cv/generator/%s/' % id
        cls.user = create_user()
        cls.default_user = create_default(cls.user)
        cls.token = Token.objects.get_or_create(user=cls.user)

    def test_generate_view_valid(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, cv_test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cv_id = response.data['cv_id']
        self.assertIsInstance(CV.objects.get(cv_id=cv_id), CV)
        self.assertTrue(CV.objects.filter(cv_id=cv_id).exists())

        get_response = self.client.get(self.url_id(cv_id))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(self.url_id(cv_id))
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(CV.objects.count(), 0)
        self.assertFalse(CV.objects.filter(cv_id=cv_id).exists())

    def test_generate_view_invalid(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {'data': 'some rubbish'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(
            CV.DoesNotExist, lambda: CV.objects.get(cv_id=self.user.id))


class DataTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = '/cv/data/'
        cls.token = 'insert_token_here'
        cls.cv_data = cv_test_data


class PictureTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/cv/picture/%s/' % id
        cls.picture = SimpleUploadedFile(name='test_image.png',
                                         content=open('cv/cv_pic.png', 'rb').read(), content_type='image/png')
        cls.user = create_user()
        cls.default_user = create_default(cls.user)
        cls.cv = create_cv(cls.default_user)

    def test_picture_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url(self.cv.cv_id), {'picture': self.picture}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data1 = CV.objects.get(cv_id=self.cv.cv_id).basic_info
        self.assertTrue(data1.picture)

        self.client.delete(self.url(self.cv.cv_id))
        data2 = CV.objects.get(cv_id=self.cv.cv_id).basic_info
        self.assertFalse(data2.picture)
        self.client.delete(self.url(self.cv.cv_id))

    def test_picture_failure_no_cv(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url("00000000-0000-0000-0000-000000000000"), {'picture': self.picture}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response2 = self.client.get(self.url("00000000-0000-0000-0000-000000000000"))

        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)

    def test_picture_failure_not_uploaded(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url(self.cv.cv_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_picture_on_delete(self):
        self.client.force_authenticate(user=self.user)
        response1 = self.client.post(
            self.url(self.cv.cv_id), {'picture': self.picture}, format='multipart')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        data1 = CV.objects.get(cv_id=self.cv.cv_id).basic_info
        self.assertTrue(data1.picture)

        self.client.delete(self.url(self.cv.cv_id))
        data2 = CV.objects.get(cv_id=self.cv.cv_id).basic_info
        self.assertFalse(data2.picture)
