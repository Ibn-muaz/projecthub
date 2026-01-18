"""Django settings for backend project."""

from pathlib import Path
from datetime import timedelta
import os
import sys

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

# -------------------------------------------------------------------
# ENVIRONMENT DETECTION
# -------------------------------------------------------------------
IS_RENDER = 'RENDER' in os.environ
IS_LOCAL_DEV = not IS_RENDER

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production-12345678901234567890')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool) and IS_LOCAL_DEV

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,.onrender.com', cast=Csv())

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

# -------------------------------------------------------------------
# DATABASE CONFIGURATION - AUTOMATIC
# -------------------------------------------------------------------
# Determine which database to use based on environment
if IS_RENDER:
    # On Render: Always use PostgreSQL from DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print("✅ Using Render PostgreSQL database")
else:
    # Local development: Check for DATABASE_URL in .env
    database_url = config('DATABASE_URL', default='')
    
    if database_url and HAS_DJ_DATABASE_URL:
        # Use PostgreSQL if DATABASE_URL is provided in .env
        DATABASES = {
            'default': dj_database_url.config(
                default=database_url,
                conn_max_age=600
            )
        }
        print("✅ Using local PostgreSQL database (from .env)")
    else:
        # Fallback to SQLite for local development
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
        print("⚠️  Using SQLite database (local development)")
        print("   To use PostgreSQL locally, add DATABASE_URL to .env file")

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# STATIC & MEDIA FILES
# -------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Only include static dir if it exists (for local dev)
_static_dir = BASE_DIR / 'static'
if _static_dir.exists():
    STATICFILES_DIRS = [_static_dir]
else:
    STATICFILES_DIRS = []

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Use S3 for media files in production (recommended)
if IS_RENDER:
    # Set up AWS S3 for media files (recommended for production)
    # Comment out if you want to use Render's ephemeral storage
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    
    if all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME]):
        print("✅ Using AWS S3 for media storage")
    else:
        print("⚠️  Using local media storage (ephemeral on Render)")
        print("   Add AWS credentials to .env for permanent media storage")

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------------------------
# SECURITY SETTINGS
# -------------------------------------------------------------------
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# CSRF settings - Auto-configure for Render
CSRF_TRUSTED_ORIGINS = []
if IS_RENDER:
    # Get your Render URL automatically
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')
    CSRF_TRUSTED_ORIGINS.extend([
        'https://*.onrender.com',
    ])

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# -------------------------------------------------------------------
# REST FRAMEWORK
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# CORS CONFIGURATION
# -------------------------------------------------------------------
CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # In production, only allow specific origins
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', 
                                 default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000', 
                                 cast=Csv())
    if IS_RENDER:
        # Automatically add Render URL to CORS
        RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        if RENDER_EXTERNAL_HOSTNAME:
            CORS_ALLOWED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# Security settings
CSRF_COOKIE_HTTPONLY = False  # Must be False for JavaScript to read CSRF token
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# -------------------------------------------------------------------
# PAYSTACK CONFIGURATION
# -------------------------------------------------------------------
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY', default='')
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY', default='')
PAYSTACK_BASE_URL = config('PAYSTACK_BASE_URL', default='https://api.paystack.com')
PAYSTACK_CALLBACK_URL = config('PAYSTACK_CALLBACK_URL', default='')

# Auto-configure callback URL for Render
if IS_RENDER and not PAYSTACK_CALLBACK_URL:
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        PAYSTACK_CALLBACK_URL = f'https://{RENDER_EXTERNAL_HOSTNAME}/payments/verify/'

# -------------------------------------------------------------------
# EMAIL CONFIGURATION
# -------------------------------------------------------------------
EMAIL_BACKEND = config('EMAIL_BACKEND', 
                      default='django.core.mail.backends.console.EmailBackend' if IS_LOCAL_DEV 
                      else 'django.core.mail.backends.smtp.EmailBackend')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', 
                           default='no-reply@projecthub.local' if IS_LOCAL_DEV 
                           else 'noreply@yourdomain.com')

if not IS_LOCAL_DEV:
    # Production email settings
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# -------------------------------------------------------------------
# PRODUCTION SECURITY SETTINGS
# -------------------------------------------------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# -------------------------------------------------------------------
# LOGGING CONFIGURATION - FIXED FOR RENDER
# -------------------------------------------------------------------
if IS_RENDER:
    # On Render: Only use console logging (filesystem is read-only)
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
            },
            'projecthub': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
else:
    # Local development: Use both console and file logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': BASE_DIR / 'debug.log',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
            },
            'projecthub': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG' if DEBUG else 'INFO',
                'propagate': True,
            },
        },
    }

# -------------------------------------------------------------------
# ENVIRONMENT INFORMATION
# -------------------------------------------------------------------
print(f"\n{'='*60}")
print(f"Environment: {'PRODUCTION (Render)' if IS_RENDER else 'LOCAL DEVELOPMENT'}")
print(f"Debug Mode: {DEBUG}")
print(f"Database: {DATABASES['default']['ENGINE']}")
print(f"Allowed Hosts: {ALLOWED_HOSTS}")
print(f"{'='*60}\n")

if IS_LOCAL_DEV and DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    print("⚠️  WARNING: You are using SQLite database locally.")
    print("   Projects added locally will NOT appear on your Render site.")
    print("   To sync databases, add DATABASE_URL to your .env file pointing to your Render PostgreSQL.")
    print("   Or add projects directly at: https://your-app.onrender.com/admin")
    print()