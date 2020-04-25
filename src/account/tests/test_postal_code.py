import unittest
from django.core.exceptions import ValidationError
from ..validators import validate_postal_code


class PostalCodeValidatorTestCase(unittest.TestCase):

    def test_postal_code_validation_success(self):
        postal_code = '12-235'
        try:
            validate_postal_code(postal_code)
        except ValidationError:
            self.fail('Raised an exception')

    def test_postal_code_contains_non_numbers(self):
        postal_code = '12-dfd'
        self.assertRaises(ValidationError, validate_postal_code, postal_code)

    def test_postal_code_too_long(self):
        postal_code = '123-345'
        self.assertRaises(ValidationError, validate_postal_code, postal_code)

    def test_postal_code_too_short(self):
        postal_code = '1345'
        self.assertRaises(ValidationError, validate_postal_code, postal_code)

    def test_postal_code_without_divider(self):
        postal_code = '13455'
        self.assertRaises(ValidationError, validate_postal_code, postal_code)
