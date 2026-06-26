"""
Django settings for the Web-Based Supply Chain Platform.

Backend: Django REST Framework. Auth: JWT (SimpleJWT).
Database: SQLite for development, PostgreSQL in production (via DATABASE_URL).
"""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from backend/.env
load_dotenv(BASE_DIR / '.env')


def env_bool(name, default=False):
    return os.getenv(name, str(default)).lower() in ('1', 'true', 'yes', 'on')


SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-j8=5+=a8t_)zj@jyb!xl67gsgx4$$8n=#s&1kq)+%29f^$7b+r',
)

DEBUG = env_bool('DEBUG', True)

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',

    # Local apps (each maps to a core module of the platform)
    'users',
    'products',
    'orders',
    'payments',
    'commissions',
    'notifications',
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
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# Uses DATABASE_URL (e.g. postgres://...) when provided, otherwise SQLite.

# DATABASE_URL may be present-but-empty in .env; fall back to SQLite then.
_database_url = os.getenv('DATABASE_URL') or f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
DATABASES = {
    'default': dj_database_url.parse(_database_url, conn_max_age=600),
}


# Custom user model with role-based accounts
AUTH_USER_MODEL = 'users.User'


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# Static & media files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# CORS (React dev server)
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173',
).split(',')
CORS_ALLOW_CREDENTIALS = True


# ---------------------------------------------------------------------------
# Third-party service configuration (graceful no-op when keys are absent)
# ---------------------------------------------------------------------------

# Paystack (payments & split payments)
PAYSTACK_SECRET_KEY = os.getenv('sk_test_552ada5cbd1a49a34db6637077060be31cb8bd47', '')
PAYSTACK_PUBLIC_KEY = os.getenv('pk_test_35c6e38440ab7ecae3cdea105b14b3a8de01cb34', '')
# Platform commission percentage taken from each transaction
PLATFORM_COMMISSION_PERCENT = float(os.getenv('PLATFORM_COMMISSION_PERCENT', '5'))
# Referral commission percentage awarded to community promoters
REFERRAL_COMMISSION_PERCENT = float(os.getenv('REFERRAL_COMMISSION_PERCENT', '2'))

# Africa's Talking (SMS notifications)
AT_USERNAME = os.getenv('AT_USERNAME', '')
AT_API_KEY = os.getenv('AT_API_KEY', '')
AT_SENDER_ID = os.getenv('AT_SENDER_ID', '')

# SendGrid (transactional email)
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@agric-platform.co.ke')

# Frontend base URL (used in notification links)
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
