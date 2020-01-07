# Create your tests here.
from account.models import Account
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from cv import models
from cv.cv_test_data import cv_test_data
from cv.cv_test_data import user_data
import os

class GenerateTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = '/cv/generate/'
        cls.token = 'insert_token_here'
        cls.cv_data = cv_test_data


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
        user = Account.objects.get().user
        self.client.force_authenticate(user=user, token=user.auth_token)
        self.client.post(self.url_cv, self.cv_data, format='json')
        response = self.client.post(self.url, {'picture' : self.picture}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = models.BasicInfo.objects.get()
        self.assertEqual(data.picture, 'cv_pictures/CV_testname_testlastname.png')

        response2 = self.client.get(self.url)
        self.assertEqual(response2.data, '/media/cv_pictures/CV_testname_testlastname.png')
        os.remove(os.path.join('media/cv_pictures', 'CV_testname_testlastname.png')) 

    def test_picture_failure_no_cv(self):
        self.client = APIClient()
        self.client.post(self.url_reg, self.user_data, format='json')
        user = Account.objects.get().user
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
        user = Account.objects.get().user
        self.client.force_authenticate(user=user, token=user.auth_token)
        self.client.post(self.url_cv, self.cv_data, format='json')
        response = self.client.get(self.url)
        self.assertEqual(response.data, 'Picture not found.')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)