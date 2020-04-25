import unittest
from ..validators import validate_street_number
from django.core.exceptions import ValidationError


class TestValidateStreetNumber(unittest.TestCase):

    def test_postal_code_validation_success(self):
        valid_street_numbers = ('12', '123', '12/34', '12c')
        try:
            for i in valid_street_numbers:
                validate_street_number(i)
        except ValidationError:
            self.fail('Raised an exception')
