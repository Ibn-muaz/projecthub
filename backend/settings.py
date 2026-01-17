"""Django settings for backend project."""

from pathlib import Path
from datetime import timedelta
import os

# Import python-decouple to read .env file
from decouple import config, Csv

# Try to import dj_database_url for production (Render)
try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production-12345678901234567890')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    # Local apps
    'accounts',
    'projects',
    'core',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# Use DATABASE_URL from environment (Render provides this)
# Falls back to SQLite for local development
if HAS_DJ_DATABASE_URL and os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL', default=''),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'

# Only include static dir if it exists (for local dev)
_static_dir = BASE_DIR / 'static'
if _static_dir.exists():
    STATICFILES_DIRS = [_static_dir]
else:
    STATICFILES_DIRS = []

STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise for serving static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Media files (uploaded project documents)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'document': ['.pdf', '.doc', '.docx', '.txt'],
    'software': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
}

# Security settings for file uploads
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Cache settings for better performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG  # True in production
CSRF_COOKIE_SECURE = not DEBUG  # True in production

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]


# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '50/hour',
        'user': '200/hour',
    },
}


# Simple JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# CORS configuration
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', 
                             default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000', 
                             cast=Csv())

# Allow all origins in development
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True


# Security settings – these should be True/strict in production
CSRF_COOKIE_HTTPONLY = False  # Must be False for JavaScript to read CSRF token
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Paystack configuration (read from .env file)
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY', default='sk_test_e66649d8ec088de0c3d8a13a4eaa4da358ff5a33')
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY', default='pk_test_9be5827fe2a4ffcd8eeaf923b83dc6e5563acf42')
PAYSTACK_BASE_URL = config('PAYSTACK_BASE_URL', default='https://api.paystack.com')
PAYSTACK_CALLBACK_URL = config('PAYSTACK_CALLBACK_URL', default='')

# Email backend (console by default for development)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='no-reply@projecthub.local')

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True