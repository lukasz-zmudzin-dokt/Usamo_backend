import json
from rest_framework.test import APITestCase


class RegistrationTestCase(APITestCase):
    url = ''
    @staticmethod
    def read_test_data(filename):
        file_path = f'account/tests/test_data/{filename}'
        with open(file_path) as file:
            data = json.load(file)
        return data
