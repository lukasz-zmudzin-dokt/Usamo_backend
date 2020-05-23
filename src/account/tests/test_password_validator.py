import unittest
from django.core.exceptions import ValidationError
from ..validators import PasswordValidator


class PasswordValidatorTestCase(unittest.TestCase):

    def test_correct_password(self):
        try:
            correct_password = 'aaaA123!*^'
            PasswordValidator().validate(password=correct_password)
        except ValidationError:
            self.fail('')

    def test_correct_password_with_polish_symbols(self):
        try:
            correct_password = 'aćłąężŹŁ123!*^'
            PasswordValidator().validate(password=correct_password)
        except ValidationError:
            self.fail('')

    def test_password_too_short(self):
        passwords = ['aA123!*', '', 'a', 'A', '1', '!', '1!', 'aA', 'a4']
        for i in passwords:
            self.assertRaises(ValidationError, PasswordValidator().validate, i)

    def test_password_no_lower_case_letters(self):
        password = 'AAAAAAA123!*'
        self.assertRaises(ValidationError, PasswordValidator().validate, password)

    def test_password_no_uppercase_case_letters(self):
        password = 'aaa123!*'
        self.assertRaises(ValidationError, PasswordValidator().validate, password)

    def test_password_no_numbers(self):
        password = 'AAAAAAAaaaabbb!*'
        self.assertRaises(ValidationError, PasswordValidator().validate, password)

    def test_password_no_special_chars(self):
        password = 'AAAAAAA123bbasd'
        self.assertRaises(ValidationError, PasswordValidator().validate, password)
