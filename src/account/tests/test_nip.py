import unittest
from django.core.exceptions import ValidationError
from ..validators import validate_nip


class NIPTestCase(unittest.TestCase):

    def test_nip_validation_success(self):
        test_nip = '1234563218'
        try:
            validate_nip(test_nip)
        except ValidationError:
            self.fail('Raised an exception')

    def test_nip_validation_too_short(self):
        test_nip = '123456321'
        self.assertRaises(ValidationError, validate_nip, test_nip)

    def test_nip_too_long(self):
        test_nip = '12345632189'
        self.assertRaises(ValidationError, validate_nip, test_nip)

    def test_nip_contains_not_numbers(self):
        test_nip = '12345632hj'
        self.assertRaises(ValidationError, validate_nip, test_nip)

    def test_nip_check_sum_does_not_match(self):
        test_nip = '1234563216'
        self.assertRaises(ValidationError, validate_nip, test_nip)