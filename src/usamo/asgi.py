import os
import django
from channels.routing import get_default_application
import dotenv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "usamo.settings.settings")
dotenv.read_dotenv(override=True)
django.setup()
application = get_default_application()