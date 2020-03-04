# Create your tests here.
from account.models import Account
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from cv import models
from cv.models import CV
from cv.models import BasicInfo
from cv.cv_test_data import cv_test_data
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from django.db import models
from .views import DataView, GenerateView
from cv.cv_test_data import user_data
import os


class GenerateTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = 'cv/generate/'
        cls.user = Account.objects.create_user(username='testuser', password='testuser', first_name='test', last_name='test', email='pan@test.com')
        cls.token = Token.objects.get_or_create(user=cls.user)

    def _make_request(self, data, method):
        api_factory = APIRequestFactory()

        if method == 'post':
            request = api_factory.post(self.url, data, format='json')
            force_authenticate(request, self.user, self.token)
        elif method == 'get':
            request = api_factory.get(self.url, data, format='json')
            force_authenticate(request, self.user, self.token)
        elif method == 'delete':
            request = api_factory.delete(self.url, data, format='json')
            force_authenticate(request, self.user, self.token)
        else:
            request = None

        self.assertIsNotNone(request, 'should provide valid http method')
        return request

    def test_generate_view_valid(self):
        generate_view = GenerateView.as_view()
        request = self._make_request(cv_test_data, 'post')
        response = generate_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(CV.objects.get(cv_id=self.user.id), CV)

        get_request = self._make_request(None, 'get')
        get_response = generate_view(get_request)

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(CV.objects.count(), 1)

        delete_request = self._make_request(None, 'delete')
        delete_response = generate_view(delete_request)

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(CV.objects.count(), 0)

    def test_generate_view_invalid(self):
        generate_view = GenerateView.as_view()
        request = self._make_request({'data': 'some rubbish'}, 'post')
        response = generate_view(request)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertRaises(CV.DoesNotExist, lambda: CV.objects.get(cv_id=self.user.id))

class DataTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = '/cv/data/'
        cls.token = 'insert_token_here'
        cls.cv_data = cv_test_data

class PictureTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = '/cv/picture/'
        cls.url_reg = '/account/register/'
        cls.url_cv = '/cv/generate/'
        cls.cv_data = cv_test_data
        cls.picture = SimpleUploadedFile(name='test_image.png',
                                         content=open('cv/cv_pic.png', 'rb').read(), content_type='image/png')
        cls.user_data = user_data
    
    def test_picture_success(self):
        self.client = APIClient()
        self.client.post(self.url_reg, self.user_data, format='json')
        user = Account.objects.get()
        self.client.force_authenticate(user=user, token=user.auth_token)
        self.client.post(self.url_cv, self.cv_data, format='json')
        response = self.client.post(self.url, {'picture' : self.picture}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data1 = BasicInfo.objects.get()
        self.assertTrue(data1.picture)

        self.client.delete(self.url)
        data2 = BasicInfo.objects.get()
        self.assertFalse(data2.picture)
        self.client.delete(self.url_cv)

    def test_picture_failure_no_cv(self):
        self.client = APIClient()
        self.client.post(self.url_reg, self.user_data, format='json')
        user = Account.objects.get()
        self.client.force_authenticate(user=user, token=user.auth_token)

        response = self.client.post(self.url, {'picture' : self.picture}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, 'CV not found.')
        response2 = self.client.get(self.url)

        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response2.data, 'CV not found.')  
    
    def test_picture_failure_not_uploaded(self):
        self.client = APIClient()
        self.client.post(self.url_reg, self.user_data, format='json')
        user = Account.objects.get()
        self.client.force_authenticate(user=user, token=user.auth_token)
        self.client.post(self.url_cv, self.cv_data, format='json')
        response = self.client.get(self.url)
        self.assertEqual(response.data, 'Picture not found.')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.delete(self.url_cv)

    def test_picture_on_delete(self):
        self.client = APIClient()
        self.client.post(self.url_reg, self.user_data, format='json')
        user = Account.objects.get()
        self.client.force_authenticate(user=user, token=user.auth_token)
        self.client.post(self.url_cv, self.cv_data, format='json')
        response1 = self.client.post(self.url, {'picture' : self.picture}, format='multipart')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        data1 = BasicInfo.objects.get()
        self.assertTrue(data1.picture)
        response2 = self.client.delete(self.url)
        data2 = BasicInfo.objects.get()
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertFalse(data2.picture)
        self.client.delete(self.url_cv)
