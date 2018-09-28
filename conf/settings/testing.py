#! coding: utf-8
import logging
# noinspection PyUnresolvedReferences
from .base import *


INSTALLED_APPS += ("django_nose", )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': env('DATABASE_HOST'),
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
    }
}

# we don't want logging while running tests.
logging.disable(logging.CRITICAL)
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
DEBUG = False
TEMPLATE_DEBUG = False
TESTS_IN_PROGRESS = True
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

RQ_QUEUES = {
    'default': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
    'high': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
    'low': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
    'scrapping': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'DEFAULT_TIMEOUT': 3600,
        'ASYNC': False,
    },
    'indexing': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
}
