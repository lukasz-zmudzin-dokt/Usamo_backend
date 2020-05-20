import uuid
import os


def __create_file_path(folder, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(f'job/{folder}', filename)


def create_job_offer_image_path(instance, filename):
    return __create_file_path('offers', filename)

