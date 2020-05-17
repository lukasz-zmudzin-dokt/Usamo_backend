import re

from django.core.exceptions import ValidationError


def validate_nip(nip: str):
    nip_regex = re.compile("^[0-9]{10}$")
    if nip_regex.match(nip) is None:
        raise ValidationError('Niepoprawny NIP')

    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    checksum = 0
    for i in range(len(nip)-1):
        checksum += weights[i] * int(nip[i])
    checksum %= 11
    if checksum != int(nip[9]):
        raise ValidationError('Niepoprawny NIP')


def validate_postal_code(postal_code: str):
    postal_code_regex = re.compile("[0-9]{2}-[0-9]{3}")
    if postal_code_regex.match(postal_code) is None:
        raise ValidationError('Niepoprawny kod pocztowy')


def validate_street_number(street_number: str):
    street_number_regex = re.compile("\d{1,3}")
    if street_number_regex.match(street_number) is None:
        raise ValidationError('Niepoprawny kod pocztowy')