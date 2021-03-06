#! coding: utf-8
import os
# noinspection PyUnresolvedReferences
from .base import *
import raven

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Admin name', 'admin_name@devartis.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
    }
}

MEDIA_ROOT = env('MEDIA_ROOT')
STATIC_ROOT = env('STATIC_ROOT')
SECRET_KEY = env('DJANGO_SECRET_KEY')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

RAVEN_CONFIG = {
    'dsn': env('RAVEN_DSN', default=""),
}

INSTALLED_APPS += 'raven.contrib.django.raven_compat',

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
