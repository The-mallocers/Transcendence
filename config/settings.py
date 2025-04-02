import atexit
import os
import shutil
import stat
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import environ
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache.backends.redis import RedisCache
from django.middleware.clickjacking import XFrameOptionsMiddleware
from django.middleware.common import CommonMiddleware
from django.middleware.csrf import CsrfViewMiddleware
from django.middleware.security import SecurityMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent
ENV = environ.Env(DEBUG_MODE=True)
ENV.read_env(env_file=os.path.join(BASE_DIR, '.env'))

SECRET_KEY = ENV('DJANGO_SECRET_KEY', default='1234')

# JWT Settings
JWT_SECRET_KEY = ENV('JWT_SECRET_KEY', default='1234')
JWT_EXP_ACCESS_TOKEN = ENV('JWT_EXP_ACCESS_TOKEN', default=10)  # 30 minutes
JWT_EXP_REFRESH_TOKEN = ENV('JWT_EXP_REFRESH_TOKEN', default=30)  # 30 days
JWT_ALGORITH = 'HS256'

#Middlware protected paths
PROTECTED_PATHS = [
    '/*'
]
EXCLUDED_PATHS = [
    '/api/auth/login',
    '/api/*',
    '/pages/auth/login',
    '/auth/login',
    '/auth/register',
    '/pages/auth/register',
    '/',
    '/pages/',
    '/pages/error/',
    '/auth/2fa',
    '/pages/auth/2fa',
    # 'api/chat/AddMsg',
]
ROLE_PROTECTED_PATHS = {
    '/admin/*': ['admin']
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV('DJANGO_DEBUG', default=False)

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

# CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS","https://127.0.0.1").split(",")

# In settings.py
CSRF_TRUSTED_ORIGINS = ['https://localhost:8000', 'https://127.0.0.1:8000']

# Add this to ensure Django knows requests are HTTPS
#Not exactly sure this is needed
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Not exactly sure this is needed
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Application definition
# had to add django.contrib.auth, not sure why

INSTALLED_APPS = [
    # ────────────────────────────────── Django Apps ─────────────────────────────────── #
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ────────────────────────────────── Modules Apps ─────────────────────────────────── #
    'channels',
    'django_extensions',
    'rest_framework',

    # ────────────────────────────────── Custom Apps ─────────────────────────────────── #
    'apps.admin.apps.AdminConfig',
    'apps.auth.apps.AuthConfig',
    'apps.index.apps.IndexConfig',
    'apps.pong.apps.PongConfig',
    'apps.profile.apps.ProfileConfig',
    'apps.shared.apps.SharedConfig',
    'apps.player.apps.PlayerConfig',
    'apps.game.apps.GameConfig',
    'apps.error.apps.ErrorConfig',
    'apps.chat.apps.ChatConfig',
    'apps.tournaments.apps.TournamentsConfig',
    'apps.notifications.apps.NotificationConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'middleware.jwt_middleware.JWTMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'utils.jwt.JWTAuthtication.JWTAuthentication',  # Replace with the actual path to your class
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Optional: Require authentication globally
    ],
}

# ─────────────────────────────────────── Redis ──────────────────────────────────────── #

# REDIS_HOST = 'localhost'
REDIS_HOST = ENV('REDIS_HOST', default='redis')
REDIS_PORT = ENV('REDIS_POST', default='6380')

REDIS_CONNECTIONS = {
    'default': {
        'host': REDIS_HOST,
        'port': REDIS_PORT,
        'db': 0,
        'password': None,  # Set to None if no password required
        'socket_timeout': 5,
        'socket_connect_timeout': 5,
        'retry_on_timeout': True,
        'decode_responses': True,
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
            "capacity": 1500,  # Default is 100
            "expiry": 10,  # Message expiry time in seconds (default: 60)
            "group_expiry": 86400,  # Group expiry time (default: 86400)
            "prefix": "channels:",  # Redis key prefix
        },
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USERNAME'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),  # Match your service name in docker-compose
        'PORT': os.environ.get('DATABASE_PORT'),
    }
}

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_PWD = os.environ.get('ADMIN_PWD')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')

GRFANA_ADMIN_PWD = os.environ.get('GRAFANA_PASSWORD')

if 'test' in sys.argv:
    DATABASES['default']['NAME'] = BASE_DIR / 'test_db.sqlite3'

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_TZ = True
USE_I18N = True
USE_L10N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

#Media
MEDIA_URL = '/media/' #Url publique pour acceder au media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Custom file handler with permissions setting
class PermissionedRotatingFileHandler(RotatingFileHandler):
    def _open(self):
        # Open the file with standard permissions
        rtv = super(PermissionedRotatingFileHandler, self)._open()

        # Set the file permissions to 0o644 (owner can read/write, others can read)
        os.chmod(self.baseFilename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

        return rtv


# Define log directory
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Define log file paths
LOG_FILENAME = datetime.now().strftime('django_%Y%m%d_%H%M%S.log')
LATEST_LOG_FILENAME = 'latest.log'

# Maximum log size in bytes (5MB)
MAX_LOG_SIZE = 5 * 1024 * 1024

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s.%(msecs)03d [%(thread)s %(threadName)s] %(levelname)s %(name)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, LOG_FILENAME),
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'maxBytes': MAX_LOG_SIZE,
            'backupCount': 4,  # Keep 5 files max (original + 4 backups)
        },
        'latest_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, LATEST_LOG_FILENAME),
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'mode': 'w',  # Overwrites the file each time
        },
        'redis_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'redis.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file', 'latest_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {  # Django framework logging
            'handlers': ['console', 'file', 'latest_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {  # Django development server logging
            'handlers': ['console', 'file', 'latest_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {  # Django request logging
            'handlers': ['console', 'file', 'latest_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'websocket': {  # WebSocket specific logging
            'handlers': ['console', 'file', 'latest_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'websocket.protocol': {  # WebSocket protocol-level logging
            'handlers': ['console', 'file', 'latest_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'websocket.client': {  # WebSocket client connections
            'handlers': ['file', 'latest_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.game': {  # Django request logging
            'handlers': ['console', 'file', 'latest_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'utils.redis': {  # Redis logging
            'handlers': ['console', 'redis_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'channels': {  # Django Channels core
            'handlers': ['console', 'file', 'latest_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'channels_redis': {  # Redis backend for Channels
            'handlers': ['console', 'redis_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# Apply permissions to latest.log file if it exists
latest_log_path = os.path.join(LOG_DIR, LATEST_LOG_FILENAME)
if os.path.exists(latest_log_path):
    os.chmod(latest_log_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
