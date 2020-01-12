# Create your tests here.
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from cv.models import CV
from cv.cv_test_data import cv_test_data
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from .views import DataView, GenerateView


class GenerateTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = 'cv/generate/'
        cls.user = User.objects.create_user(username='testuser', password='testuser', first_name='test', last_name='test')
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

        delete_request = self._make_request(None, 'delete')
        delete_response = generate_view(delete_request)

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)

    def test_generate_view_invalid(self):
        generate_view = GenerateView.as_view()
        request = self._make_request({'data': 'some rubbish'}, 'post')
        response = generate_view(request)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertRaises(CV.DoesNotExist, lambda: CV.objects.get(cv_id=self.user.id))


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
        cls.picture = SimpleUploadedFile(name='test_image.jpg',
                                         content=open('cv_pic.png', 'rb').read(), content_type='image/png')
