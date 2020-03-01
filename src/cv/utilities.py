from django.utils.crypto import get_random_string
from usamo import settings
import os
import random
import datetime

def create_unique_filename(prefix, ext):
    full_date = datetime.datetime.now()
    year = full_date.strftime("%Y")
    month = full_date.strftime("%m")
    day = full_date.strftime("%d")

    length = random.randint(32, 48)
    unique_string = get_random_string(length=length)
    unique_filename = unique_string + '.' + ext
    full_path = os.path.join(settings.MEDIA_ROOT, prefix, year, month, day, unique_filename)
    while os.path.exists(full_path):
        length = random.randint(32, 48)
        unique_string = get_random_string(length=length)
        unique_filename = unique_string + '.' + ext
        full_path = os.path.join(settings.MEDIA_ROOT, prefix, year, month, day, unique_filename)

    return unique_filename