#! coding: utf-8
# noinspection PyUnresolvedReferences

from __future__ import absolute_import, unicode_literals

from os.path import dirname

import environ
from .indicators import *

SETTINGS_DIR = environ.Path(__file__) - 1
ROOT_DIR = environ.Path(__file__) - 3  # (/a/b/myfile.py - 3 = /)
APPS_DIR = ROOT_DIR.path(dirname(dirname(dirname(__file__))))

env = environ.Env()
environ.Env.read_env(SETTINGS_DIR('.env'))

DEBUG = True

ADMINS = ()

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Argentina/Buenos_Aires'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-AR'

LANGUAGES = [
  ('es', 'Spanish'),
]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = str(APPS_DIR('media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    str(ROOT_DIR.path('monitoreo/static')),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9!n$10$pksr3j5dv*4bc21ke$%0$zs18+vse=al8dpfzi_9w4y'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
    'async_messages.middleware.AsyncMiddleware'
)

ANONYMOUS_USER_ID = -1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'monitoreo.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'conf.wsgi.application'


def export_vars(_):
    data = {
        'APP_VERSION': env('APP_VERSION', default='local')
    }
    return data


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('monitoreo/templates')),
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'conf.settings.base.export_vars',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'debug': True
        },
    },
]

DJANGO_BASE_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)

VENDOR_APPS = (
    'ordered_model',
    'import_export',
    'django_rq',
    'scheduler',
    'des',
    'solo',
    'admin_reorder',
)

APPS = (
    'monitoreo.apps.dashboard',
    'django_datajsonar',
)

INSTALLED_APPS = DJANGO_BASE_APPS + VENDOR_APPS + APPS

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
           'class': 'logging.StreamHandler',
           'level': 'INFO',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': MEDIA_ROOT + '/cache',
    }
}

GOOGLE_DRIVE_PROJECT_CREDENTIALS = env('GOOGLE_DRIVE_PROJECT_CREDENTIALS',
                                       default="")
GOOGLE_DRIVE_USER_CREDENTIALS = env('GOOGLE_DRIVE_USER_CREDENTIALS',
                                    default='')

EMAIL_BACKEND = 'des.backends.ConfiguredEmailBackend'

DEFAULT_REDIS_HOST = env("DEFAULT_REDIS_HOST", default="localhost")
DEFAULT_REDIS_PORT = env("DEFAULT_REDIS_PORT", default="6379")
DEFAULT_REDIS_DB = env("DEFAULT_REDIS_DB", default="0")

RQ_QUEUES = {
    'default': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
    },
    'indexing': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
    },
    'federation': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
    },
    'indicators': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
    },
    'reports': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
    },
    'imports': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
    },
}

DISTRIBUTION_INDEX_JOB_TIMEOUT = 1000  # Segundos

# Nombre del grupo de usuarios que reciben reportes de indexación
READ_DATAJSON_RECIPIENT_GROUP = 'read_datajson_recipients'

RQ_SHOW_ADMIN_LINK = True

# Metadata blacklists
CATALOG_BLACKLIST = [
    "themeTaxonomy"
]

DATASET_BLACKLIST = [

]

DISTRIBUTION_BLACKLIST = [
    "scrapingFileSheet"
]

FIELD_BLACKLIST = [
    "scrapingDataStartCell",
    "scrapingIdentifierCell",
    "scrapingDataStartCell",
]

ENV_TYPE = env('ENV_TYPE', default='')

DEFAULT_TASKS = [
    {
        'name': 'Lectura de metadatos de red ',
        'callable': 'django_datajsonar.tasks.schedule_full_read_task',
        'start_hour': 3,
        'start_minute': 0,
        'interval': 1,
        'interval_unit': 'hours'
    },
    {
        'name': 'Lectura completa de red',
        'callable': 'django_datajsonar.tasks.schedule_metadata_read_task',
        'start_hour': 3,
        'start_minute': 0,
        'interval': 1,
        'interval_unit': 'days'
    },
    {
        'name': 'Cerrar tareas de lectura',
        'callable': 'django_datajsonar.indexing.tasks.close_read_datajson_task',
        'start_hour': 3,
        'start_minute': 15,
        'interval': 10,
        'interval_unit': 'minutes'
    },
    {
        'name': 'Corrida de federación',
        'callable': 'monitoreo.apps.dashboard.tasks.federation_run',
        'start_hour': 3,
        'start_minute': 0,
        'interval': 4,
        'interval_unit': 'hours'
    },
    {
        'name': 'Generación de indicadores',
        'callable': 'monitoreo.apps.dashboard.indicators_tasks.indicators_run',
        'start_hour': 2,
        'start_minute': 0,
        'interval': 1,
        'interval_unit': 'days'
    },
    {
        'name': 'Envío de reportes',
        'callable': 'monitoreo.apps.dashboard.report_tasks.send_reports',
        'start_hour': 11,
        'start_minute': 0,
        'interval': 1,
        'interval_unit': 'days'
    },
]

DEFAULT_PROCESSES = [
    {
        'name': "Full process",
        'stages': [
            {
                'callable_str': 'django_datajsonar.tasks.schedule_new_read_datajson_task',
                'queue': 'indexing',
                'task': 'django_datajsonar.models.ReadDataJsonTask'

            },
            {

                'callable_str': 'monitoreo.apps.dashboard.tasks.federation_run',
                'queue': 'federation'
            },
            {
                'callable_str': 'monitoreo.apps.dashboard.indicators_tasks.indicators_run',
                'queue': 'indicators'
            },
            {
                'callable_str': 'monitoreo.apps.dashboard.report_tasks.send_reports',
                'queue': 'reports'
            },

        ],
    },
]

DATAJSONAR_STAGES = {
    'Read Datajson (complete)': {
        'callable_str': 'django_datajsonar.tasks.schedule_full_read_task',
        'queue': 'indexing',
        'task': 'django_datajsonar.models.ReadDataJsonTask',
    },
    'Read Datajson (metadata only)': {
        'callable_str': 'django_datajsonar.tasks.schedule_metadata_read_task',
        'queue': 'indexing',
        'task': 'django_datajsonar.models.ReadDataJsonTask',
    },
    'Federation': {
        'callable_str': 'monitoreo.apps.dashboard.tasks.federation_run',
        'queue': 'federation',
        'task': 'monitoreo.apps.dashboard.models.FederationTask'
    },
    'Indicators': {
        'callable_str': 'monitoreo.apps.dashboard.indicators_tasks.indicators_run',
        'queue': 'indicators',
        'task': 'monitoreo.apps.dashboard.models.IndicatorsGenerationTask'
    },
    'Indicator reports': {
        'callable_str': 'monitoreo.apps.dashboard.report_tasks.send_reports',
        'queue': 'reports',
        'task': 'monitoreo.apps.dashboard.models.ReportGenerationTask'
    },
    'Validation reports': {
        'callable_str': 'monitoreo.apps.dashboard.report_tasks.send_validations',
        'queue': 'reports',
        'task': 'monitoreo.apps.dashboard.models.ValidationReportTask'
    }
}

ADMIN_REORDER = (
    str('auth'),
    str('django_datajsonar'),
    str('dashboard'),
    {'app': 'des',
     'label': 'Configuración correo',
     'models': (
        {'model': 'des.DynamicEmailConfiguration',
         'label': 'Configuración correo electrónico'},
     )
     },
    str('scheduler'),
    str('sites'),
)

LOGIN_URL = 'admin:login'
