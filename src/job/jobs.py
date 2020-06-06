import os


def delete_zip_file(path):
    if os.path.isfile(path):
        os.remove(path)
