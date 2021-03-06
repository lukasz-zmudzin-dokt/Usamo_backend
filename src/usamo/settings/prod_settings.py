import os
import dj_database_url
from datetime import timedelta


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY')
FRONT_URL = os.getenv('FRONT_URL')
CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'kontakt@usamodzielnieni.pl')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_TEMPLATE_ID = os.getenv('SENDGRID_TEMPLATE_ID')
WKHTMLTOPDF_BINARY = '/usr/local/bin/wkhtmltopdf'

DEBUG = False

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_HSTS_SECONDS = 0 # disable at start, after that need to configure starting from low values like 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = 'DENY'

ALLOWED_HOSTS = ['127.0.0.1']

CORS_ORIGIN_WHITELIST = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'whitenoise.runserver_nostatic',
    'phonenumber_field',
    'rest_framework',
    'rest_framework.authtoken',
    'job.apps.JobConfig',
    'chat.apps.ChatConfig',
    'cv.apps.CvConfig',
    'videos.apps.VideosConfig',
    'account.apps.AccountConfig',
    'blog.apps.BlogConfig',
    'helpline.apps.HelplineConfig',
    'notification.apps.NotificationConfig',
    'steps.apps.StepsConfig',
    'tiles.apps.TilesConfig',
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
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': '5432'
    }
} 

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
    'sec-websocket-protocol',
    'sec-websocket-key',
    'sec-websocket-extensions',
    'sec-websocket-version',
    'upgrade',
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

STATIC_ROOT = '/var/www/api.usamodzielnieni.pl/static/'
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
MEDIA_ROOT = '/var/www/api.usamodzielnieni.pl/media/'
MEDIA_URL = '/media/'


TEST_RUNNER = 'usamo.tests.TempMediaRunner'