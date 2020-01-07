# Create your tests here.
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from cv.models import CV
from cv.cv_test_data import cv_test_data


class GenerateTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = 'cv/generate/'
        cls.token = 'insert_token_here'
        cls.cv_data = cv_test_data


class DataTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = 'cv/data/'
        cls.token = 'insert_token_here'
        cls.cv_data = cv_test_data


class PictureTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = 'cv/picture/'
        cls.token = 'insert_token_here'
        cls.cv_data = cv_test_data
        cls.picture = SimpleUploadedFile(name='test_image.png',
                                         content=open('cv_pic.png', 'rb').read(), content_type='image/png')
