import dotenv
import dj_database_url
import subprocess
import sys

from ..settings import *

dotenv.read_dotenv(os.path.join(os.path.dirname(__file__), 'prod.env'))

envs = {
    'NAME': os.getenv('POSTGRES_DB'),
    'USER': os.getenv('POSTGRES_USER'),
    'PASSWORD': os.getenv('POSTGRES_PASSWORD')
}

db_from_env = {k: v for k, v in envs.items() if v is not None}
DATABASES['default'].update(db_from_env)

os.environ['PATH'] += os.pathsep + os.path.dirname(sys.executable)
