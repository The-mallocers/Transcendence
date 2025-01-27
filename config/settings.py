import os
import sys
from pathlib import Path

import environ
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
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
    '/api/auth/register',
    '/auth/login',
    '/auth/register',
]
ROLE_PROTECTED_PATHS = {
    '/admin/*': ['admin']
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV('DJANGO_DEBUG', default=False)

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1'
]

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

    # ────────────────────────────────── Custom Apps ─────────────────────────────────── #
    'apps.admin.apps.AdminConfig',
    'apps.api.apps.ApiConfig',
    'apps.auth.apps.AuthConfig',
    'apps.componentBuilder.apps.ComponentbuilderConfig',
    'apps.index.apps.IndexConfig',
    'apps.pageBuilder.apps.PagebuilderConfig',
    'apps.pong.apps.PongConfig',
    'apps.profile.apps.ProfileConfig',
    'apps.shared.apps.SharedConfig'
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'transcendence.sqlite3',
        'TEST': {
            'NAME': BASE_DIR / 'test_db.sqlite3',
        },
    }
}

if 'test' in sys.argv:
    DATABASES['default']['NAME'] = BASE_DIR / 'test_db.sqlite3'

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


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