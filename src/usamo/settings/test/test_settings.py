import os
import dotenv

from ..settings import *

dotenv.read_dotenv(os.path.join(os.path.dirname(__file__), 'test.env'))

envs = {
    'NAME': os.getenv('POSTGRES_DB'),
    'USER': os.getenv('POSTGRES_USER'),
    'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
    'HOST': os.getenv('POSTGRES_HOST')
}

db_from_env = {k: v for k, v in envs.items() if v is not None}

DATABASES['default'].update(db_from_env)
