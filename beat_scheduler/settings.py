"""
Django settings for beat_scheduler project.

Generated by 'django-admin startproject' using Django 4.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from datetime import timedelta, datetime
from pathlib import Path

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-a($=(g((t06d4*@*41=lg-v(xs12#0nr3)fa&o2wuv(&p^3v9!')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get('DEBUG', '0'))
APPEND_SLASH = False

ALLOWED_HOSTS = [
    'localhost',
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]
# Application definition

INSTALLED_APPS = [
    'baton',
    'django.contrib.admin',
    # 'django.contrib.auth',
    'patches.auth.AuthAppConfig',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'django_extensions',
    'django_filters',
    'django_seed',
    "corsheaders",
    'django_celery_beat',
    'health_check',  # required
    'health_check.db',  # stock Django health checkers
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.migrations',
    # 'health_check.contrib.celery',  # requires celery
    # 'health_check.contrib.celery_ping',  # requires celery
    'health_check.contrib.psutil',  # disk and memory utilization; requires psutil
    # 'health_check.contrib.redis',  # requires Redis broker
    # 'health_check.contrib.rabbitmq',  # requires RabbitMQ broker
    'profiles_app',
    # ... (place baton.autodiscover at the very end)
    'baton.autodiscover',
]

HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,  # in MB
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'beat_scheduler.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'beat_scheduler.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE'),
        'USER': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'PORT': os.environ.get('MYSQL_PORT'),
        'HOST': os.environ.get('MYSQL_HOST'),
        'CHARSET': 'utf8mb4',
        'COLLATION': 'utf8mb4_unicode_ci',
        'OPTIONS': {
            'use_unicode': True,
            'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED',
        },
        'TEST': {
            'NAME': os.environ.get('MYSQL_TEST_DATABASE', "test_" + os.environ.get('MYSQL_DATABASE')),
            'USER': os.environ.get('MYSQL_TEST_USER', "test_" + os.environ.get('MYSQL_USER')),
            'PASSWORD': os.environ.get('MYSQL_TEST_PASSWORD', "test_" + os.environ.get('MYSQL_PASSWORD')),
            'CREATE_DB': int(os.environ.get('CREATE_MYSQL_TEST_DB', 0)),
            'CREATE_USER': int(os.environ.get('CREATE_MYSQL_TEST_USER', 0)),
        }
    }
}

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']

AUTH_USER_MODEL = 'profiles_app.UserProfile'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'USER_ID_FIELD': 'version',
    'USER_FIELD': 'version',
}
# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BASE_API_URL = 'api/v1/'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend',
                                'rest_framework.filters.SearchFilter',
                                'rest_framework.filters.OrderingFilter'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'SEARCH_PARAM': 'q',
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ],
    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework_simplejwt.authentication.JWTAuthentication',
    # ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Beat Scheduler',
    'DESCRIPTION': 'Celery Beat Scheduler application',
    'VERSION': '1.0.0',
    'CONTACT': {'email': 'admin@example.com', 'name': 'Web Master'},
    'SERVERS': [
        {'url': 'https://www.example.com'},
    ],
    'SERVE_INCLUDE_SCHEMA': True,
}

BATON = {
    'SITE_HEADER': 'Scheduler',
    'SITE_TITLE': 'Scheduler',
    'INDEX_TITLE': 'Site administration',
    'SUPPORT_HREF': 'https://www.example.com',
    'COPYRIGHT': f'copyright © {datetime.now().year} <a href="https://www.example.com"> example </a>',  # noqa
    'POWERED_BY': '<a href="https://www.example.com"> Dev Team </a>',
    'MENU_TITLE': 'Menu',
    'MESSAGES_TOASTS': True,
    'GRAVATAR_DEFAULT_IMG': 'retro',
    'LOGIN_SPLASH': '/static/core/img/login-splash.png',
    'SEARCH_FIELD': {},
    'MENU': (
        {'type': 'title', 'label': 'main'},
        {
            'type': 'app',
            'name': 'auth',
            'label': _('Authorization'),
            'icon': 'fa fa-lock',
            'default_open': True,
            'models': (
                {
                    'name': 'group',
                    'label': 'Groups'
                },
            )
        },
        {
            'type': 'app',
            'name': 'profiles_app',
            'label': _('Profiles'),
            'icon': 'fa fa-user',
            'default_open': False,
            'apps': ('auth',),
            'models': (
                {
                    'name': 'userprofile',
                    'label': 'Users'
                },
            )
        },
    ),
}

GRAPH_MODELS = {
    'all_application': True,
    'group_models': True,
}

EMAIL_CONFIRMATION_TIMEOUT = 259200  # 72 hours
PASSWORD_RESET_TIMEOUT = 259200  # 72 hours

REDIS = {
    'password': os.environ.get('REDIS_PASSWORD'),
    'host': os.environ.get('REDIS_HOST', 'localhost'),
    'port': os.environ.get('REDIS_PORT', '6379'),
    'db': int(os.environ.get('REDIS_DB_NUMBER', '0')),
}

RABBITMQ = {
    'username': os.environ.get('RABBITMQ_USER'),
    'password': os.environ.get('RABBITMQ_PASSWORD'),
    'host': os.environ.get('RABBITMQ_HOST', 'localhost'),
    'port': os.environ.get('RABBITMQ_PORT', '5672'),
    'vhost': os.environ.get('RABBITMQ_VHOST', '/')
}
BROKER_URL = 'amqp://{username}:{password}@{host}:{port}/{vhost}'.format(**RABBITMQ)
REDIS_URL = 'redis://:{password}@{host}:{port}/{db}'.format(**REDIS)

CELERY_BROKER_URL = BROKER_URL

CELERY_OVERRIDE_BACKENDS = {'redis': 'patches.celery_result_backend.RedisBackend'}
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_EXPIRES = timedelta(days=2)
CELERY_RESULT_SERIALIZER = 'json'

CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = int(os.environ.get('WORKER_ACKS_LATE', 0))
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_DEFAULT_QUEUE = 'celery_default'
CELERY_TASK_ROUTES = {
    'profiles_app.tasks.profiles_hello_world': {'queue': 'celery_hello', 'delivery_mode': 'transient'},
}

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {
    # 'hello-profiles': {
    #     'task': 'profiles_app.tasks.profiles_hello_world',
    #     'schedule': 30.0,  # every 30 seconds
    # },
}

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)

SENTRY_TRACES_SAMPLE_RATE = min(float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', 1.0)), 1.0)
