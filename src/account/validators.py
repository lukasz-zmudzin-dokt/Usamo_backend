from django.core.exceptions import ValidationError
import re


def validate_nip(nip: str):
    nip_regex = "/^\d{3}-(\d{3}-\d{2}|\d{2}-\d{3})-\d{2}$/"
    if re.match(nip_regex, nip) is None:
        raise ValidationError
