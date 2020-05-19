import uuid
import os


def __create_file_path(folder, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(f'blogs/{folder}', filename)


def create_blog_attachment_file_path(instance, filename):
    return __create_file_path('attachments', filename)


def create_blog_header_file_path(instance, filename):
    return __create_file_path('headers', filename)


def create_category_header_file_path(instance, filename):
    return __create_file_path('category_headers', filename)