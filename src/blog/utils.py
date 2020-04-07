import uuid
import os


def __create_file_path(folder, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(f'uploads/blog/{folder}', filename)


def create_blog_attachment_file_path(instance, filename):
    return __create_file_path('attachment', filename)


def create_blog_header_file_path(instance, filename):
    return __create_file_path('header', filename)

