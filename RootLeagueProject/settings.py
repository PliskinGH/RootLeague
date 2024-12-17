"""
Django settings for RootLeagueProject project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

ROOTLEAGUE_ENV = os.environ.get('ROOTLEAGUE_ENV')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY',
                        'cfc=c8^234om(oe6@2y(tvft%n+_94zmk#zp5!8=e1u2+x$vzl')

# SECURITY WARNING: don't run with debug turned on in production!
ROOTLEAGUE_DEBUG = os.environ.get('ROOTLEAGUE_DEBUG')
if (ROOTLEAGUE_DEBUG == "False" or ROOTLEAGUE_DEBUG == "0"):
    DEBUG = False
elif (ROOTLEAGUE_DEBUG == "True" or ROOTLEAGUE_DEBUG == "1"):
    DEBUG = True
elif (ROOTLEAGUE_ENV == 'PRODUCTION' or ROOTLEAGUE_ENV == 'TEST'):
    DEBUG = False
else:
    DEBUG = True

DEBUG_PROPAGATE_EXCEPTIONS = (os.environ.get('ROOTLEAGUE_EXCEPTIONS') in ['True', '1'])

ALLOWED_HOSTS = os.environ.get('ROOTLEAGUE_ALLOWED_HOSTS', '').split(' ')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'extra_views',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_select2',
    'crispy_formset_modal',
    'import_export',
    'django_admin_inline_paginator',
    "mailer",
    'authentification',
    'matchmaking',
    'league',
    'misc',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

# Toolbar
if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
DEBUG_TOOLBAR_CONFIG = {}
DEBUG_TOOLBAR_CONFIG['IS_RUNNING_TESTS'] = False

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

ROOT_URLCONF = 'RootLeagueProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

WSGI_APPLICATION = 'RootLeagueProject.wsgi.application'

# Emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'rootdigitalleague.email@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('ROOTLEAGUE_EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = 587
 


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', 
        'NAME': os.environ.get('ROOTLEAGUE_DATABASE', ''), 
        'USER': os.environ.get('ROOTLEAGUE_DATABASE_USER', ''), 
        'PASSWORD': os.environ.get('ROOTLEAGUE_DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('ROOTLEAGUE_DATABASE_HOST', ''),
        'PORT': os.environ.get('ROOTLEAGUE_DATABASE_PORT', ''),
        'ATOMIC_REQUESTS': True,
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Auth and user management
LOGIN_URL = '/auth/'
LOGIN_REDIRECT_URL = 'index'
AUTH_USER_MODEL = 'authentification.Player'


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

if ROOTLEAGUE_ENV == 'PRODUCTION':
    # Static files settings
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

    # Extra places for collectstatic to find static files.
    STATICFILES_DIRS = (
        os.path.join(PROJECT_ROOT, 'static'),
    )
    
    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    WHITENOISE_MANIFEST_STRICT = False
    
    #
    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES['default'].update(db_from_env)

    # HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
