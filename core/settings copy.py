
import os
from pathlib import Path
from decouple import config
from django.core.exceptions import ImproperlyConfigured
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = config('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("The SECRET_KEY environment variable is not set.")



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application defiition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Required for allauth
    'django.contrib.sites',
    
    #cors    
    'corsheaders',  
    
    #search filter
    'django_filters',
     'company',


    #Added apps
    "customer",
    "materials",
    "order",
    'users',
    'arebia_mejlis',
    #Authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'rest_framework_simplejwt',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR/'templates',
            ],
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

WSGI_APPLICATION = 'core.wsgi.application'

# For static files (Option A)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


#Auth settings
SITE_ID = 1
AUTH_USER_MODEL = 'users.CustomUser'


ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_LOGIN_METHODS = ["username"]
ACCOUNT_SIGNUP_FIELDS = ["username", "email", "password1", "password2"]
print("ACCOUNT_LOGIN_METHODS =", ACCOUNT_LOGIN_METHODS)
print("ACCOUNT_SIGNUP_FIELDS =", ACCOUNT_SIGNUP_FIELDS)


ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/5m',  # 5 attempts per 5 minutes
    'confirm_email': '3h',   # One confirmation every 3 hours
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'jwt-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'jwt-refresh',
    'REGISTER_SERIALIZER': 'users.serializers.UserSerializer',
}

#simplejwt settings

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # your Next.js frontend
    "http://10.11.0.65:3000"  # LAN IP
]



CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

FRONTEND_URL = 'http://localhost:3000'

DB_LIVE=config('DB_LIVE')

if DB_LIVE in ['False',False]:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

else:
    DATABASES = {
            'default': {
                'ENGINE': 'wwdjango.db.backends.postgresql',
                'NAME': config('DB_NAME'),
                'USER':config('DB_USER'),
                'PASSWORD':config('DB_PASSWORD'),
                'HOST': config('DB_HOST'),
                'PORT': config('DB_PORT'),
            }
        }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT=BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import logging
from logging.handlers import RotatingFileHandler

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {   # Logs to terminal
            'class': 'logging.StreamHandler',
        },
        'file_info': {  # Rotating log for normal info/debug logs
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'orders.log',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 5,             # keep 5 old log files
            'level': 'INFO',
            'formatter': 'verbose',
        },
        'file_error': {  # Rotating log for errors only
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'errors.log',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 5,
            'level': 'ERROR',
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name}:{lineno} - {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_info', 'file_error'],
            'level': 'INFO',
            'propagate': True,
        },
        'orders': {  # Your custom logger for order app
            'handlers': ['console', 'file_info', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
