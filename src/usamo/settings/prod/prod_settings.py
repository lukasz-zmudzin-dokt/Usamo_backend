import os
import dj_database_url
import pdfkit
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY')
PASS_RESET_URL = os.getenv('PASS_RESET_URL')

DEBUG = False

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = 'DENY'

ALLOWED_HOSTS = ['usamodzielnieni-frontend.herokuapp.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'django_apscheduler',
    'phonenumber_field',
    'rest_framework',
    'rest_framework.authtoken',
    'whitenoise.runserver_nostatic',
    'corsheaders',
    'job.apps.JobConfig',
    'chat.apps.ChatConfig',
    'cv.apps.CvConfig',
    'videos.apps.VideosConfig',
    'account.apps.AccountConfig',
    'blog.apps.BlogConfig',
    'helpline.apps.HelplineConfig',
    'notification.apps.NotificationConfig',
    'steps.apps.StepsConfig',
    'notifications',
    'drf_yasg',
    'django_rest_passwordreset',
    'django_filters',
    'knox'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'usamo.middlewares.FilesSizeValidatorMiddleware'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('knox.auth.TokenAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

REST_KNOX = {
  'TOKEN_TTL': timedelta(minutes=2400),
}

ROOT_URLCONF = 'usamo.urls'

MAX_UPLOAD_MB_SIZE = "15"
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = "usamo.routing.application"

DATABASES = {
    'default': {}
}
db_from_env = dj_database_url.config(default = 'postgresql://postgres:postgres@localhost:5432/usamo_test')
DATABASES['default'].update(db_from_env)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [],
        },
    },
}
redis_url = os.environ.get('REDIS_URL')
if redis_url:
    CHANNEL_LAYERS['default']["CONFIG"]["hosts"] = [redis_url]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'account.validators.PasswordValidator',
    }
]

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE = True

AUTH_USER_MODEL = 'account.Account'

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

SWAGGER_ENABLED = False
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
    'SHOW_REQUEST_HEADERS': True,
    'LOGIN_URL': 'rest_framework:login',
    'LOGOUT_URL': 'rest_framework:logout',
    'USE_SESSION_AUTH': False,
    'DOC_EXPANSION': 'list',
    'APIS_SORTER': 'alpha',
    'JSON_EDITOR': True,
    'api_version': '0.1',
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
    ],
}
DJANGO_NOTIFICATIONS_CONFIG = {'USE_JSONFIELD': True}
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# APScheduler
SCHEDULER_CONFIG = {
    "apscheduler.jobstores.default": {
        "class": "django_apscheduler.jobstores:DjangoJobStore"
    },
    'apscheduler.executors.processpool': {
        "type": "threadpool"
    },
}
SCHEDULER_AUTOSTART = True

TEST_RUNNER = 'usamo.tests.TempMediaRunner'

def _get_pdfkit_config():
    wkhtmltopdf_bin = os.environ.get('WKHTMLTOPDF_BINARY')
    if wkhtmltopdf_bin:
        return pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_bin)
