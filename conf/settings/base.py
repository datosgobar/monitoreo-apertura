#! coding: utf-8
# noinspection PyUnresolvedReferences

from __future__ import absolute_import, unicode_literals

from os.path import dirname

import environ
from django_datajsonar import strings

# noinspection PyUnresolvedReferences
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
    'admin_shortcuts',
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
    'monitoreo.apps.validator',
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
        'callable': 'monitoreo.apps.dashboard.federation_tasks.federation_run',
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

                'callable_str': 'monitoreo.apps.dashboard.federation_tasks.federation_run',
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

STAGE_TITLES = {
    'COMPLETE_READ': 'Read Datajson (complete)',
    'METADATA_READ': 'Read Datajson (metadata only)',
    'FEDERATION': 'Federation',
    'INDICATORS_GENERATION': 'Indicators',
    'INDICATORS_REPORT': 'Indicator reports',
    'VALIDATION_REPORT': 'Validation reports',
    'NEWS_REPORT': 'Newly added dataset reports',
    'MISSING_REPORT': 'Not present datasets reports',
}

DATAJSONAR_STAGES = {
    STAGE_TITLES['COMPLETE_READ']: {
        'callable_str': 'django_datajsonar.tasks.schedule_full_read_task',
        'queue': 'indexing',
        'task': 'django_datajsonar.models.ReadDataJsonTask',
    },
    STAGE_TITLES['METADATA_READ']: {
        'callable_str': 'django_datajsonar.tasks.schedule_metadata_read_task',
        'queue': 'indexing',
        'task': 'django_datajsonar.models.ReadDataJsonTask',
    },
    STAGE_TITLES['FEDERATION']: {
        'callable_str': 'monitoreo.apps.dashboard.federation_tasks.federation_run',
        'queue': 'federation',
        'task': 'monitoreo.apps.dashboard.models.FederationTask'
    },
    STAGE_TITLES['INDICATORS_GENERATION']: {
        'callable_str': 'monitoreo.apps.dashboard.indicators_tasks.indicators_run',
        'queue': 'indicators',
        'task': 'monitoreo.apps.dashboard.models.IndicatorsGenerationTask'
    },
    STAGE_TITLES['INDICATORS_REPORT']: {
        'callable_str': 'monitoreo.apps.dashboard.report_tasks.send_reports',
        'queue': 'reports',
        'task': 'monitoreo.apps.dashboard.models.ReportGenerationTask'
    },
    STAGE_TITLES['VALIDATION_REPORT']: {
        'callable_str': 'monitoreo.apps.dashboard.report_tasks.send_validations',
        'queue': 'reports',
        'task': 'monitoreo.apps.dashboard.models.ValidationReportTask'
    },
    STAGE_TITLES['NEWS_REPORT']: {
        'callable_str': 'monitoreo.apps.dashboard.report_tasks.send_newly_reports',
        'queue': 'reports',
        'task': 'monitoreo.apps.dashboard.models.NewlyReportGenerationTask'
    },
    STAGE_TITLES['MISSING_REPORT']: {
        'callable_str': 'monitoreo.apps.dashboard.report_tasks.send_not_present_reports',
        'queue': 'reports',
        'task': 'monitoreo.apps.dashboard.models.NotPresentReportGenerationTask'
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

ADMIN_SHORTCUTS = [
    {
        'shortcuts': [
            {
                'title': 'Home',
                'url_name': 'admin:index',
            },
            {
                'title': 'Usuarios',
                'url_name': 'admin:auth_user_changelist',
            },
            {
                'title': 'Jurisdicciones',
                'url_name': 'admin:django_datajsonar_jurisdiction_changelist',
                'icon': 'file-alt',
            },
            {
                'title': 'Nodos',
                'url_name': 'admin:django_datajsonar_node_changelist',
                'icon': 'university',
            },
            {
                'title': 'Datasets',
                'url_name': 'admin:django_datajsonar_dataset_changelist',
                'icon': 'database',
            }
        ]
    },
    {
        'title': 'Rutinas',
        'shortcuts': [
            {
                'title': 'Lectura de nodos',
                'url_name': 'admin:django_datajsonar_readdatajsontask_changelist',
                'icon': 'search',
            },
            {
                'title': 'Federación',
                'url_name': 'admin:dashboard_federationtask_changelist',
                'icon': 'lightbulb',
            },
            {
                'title': 'Generación de indicadores',
                'url_name': 'admin:dashboard_indicatorsgenerationtask_changelist',
            },
            {
                'title': 'Tareas programadas',
                'url_name': 'admin:django_datajsonar_synchronizer_changelist',
                'icon': 'cogs',
            },
        ]
    },
]

ADMIN_SHORTCUTS_SETTINGS = {
    'show_on_all_pages': True,
    'hide_app_list': False,
    'open_new_window': False,
}

SYNCHRO_DEFAULT_CONF = [
    {
        'title': 'Corrida de federación (1)',
        'stages': [
            STAGE_TITLES['METADATA_READ'],
            STAGE_TITLES['FEDERATION']
        ],
        'scheduled_time': '06:00',
        'week_days': strings.WEEK_DAYS
     },
    {
        'title': 'Corrida de federación (2)',
        'stages': [
            STAGE_TITLES['METADATA_READ'],
            STAGE_TITLES['FEDERATION']
        ],
        'scheduled_time': '10:00',
        'week_days': strings.WEEK_DAYS
    },
    {
        'title': 'Corrida de federación (3)',
        'stages': [
            STAGE_TITLES['METADATA_READ'],
            STAGE_TITLES['FEDERATION']
        ],
        'scheduled_time': '14:00',
        'week_days': strings.WEEK_DAYS
    },
    {
        'title': 'Corrida de federación (4)',
        'stages': [
            STAGE_TITLES['METADATA_READ'],
            STAGE_TITLES['FEDERATION']
        ],
        'scheduled_time': '18:00',
        'week_days': strings.WEEK_DAYS
    },
    {
        'title': 'Corrida de generación de indicadores',
        'stages': [
            STAGE_TITLES['COMPLETE_READ'],
            STAGE_TITLES['INDICATORS_GENERATION']
        ],
        'scheduled_time': '22:00'
    },
    {
        'title': 'Corrida de reportes de validación',
        'stages': [
            STAGE_TITLES['METADATA_READ'],
            STAGE_TITLES['VALIDATION_REPORT']
        ],
        'scheduled_time': '08:00',
        'week_days': strings.WEEK_DAYS
    },
    {
        'title': 'Corrida de reporte semanal de indicadores',
        'stages': [
            STAGE_TITLES['INDICATORS_REPORT']
        ],
        'scheduled_time': '08:00',
        'week_days': [strings.MON]
    },
    {
        'title': 'Corrida de novedades',
        'stages': [
            STAGE_TITLES['NEWS_REPORT']
        ],
        'scheduled_time': '08:00',
        'week_days': strings.WEEK_DAYS
    },
    {
        'title': 'Corrida de datasets faltantes',
        'stages': [
            STAGE_TITLES['METADATA_READ'],
            STAGE_TITLES['MISSING_REPORT']
        ],
        'scheduled_time': '08:00',
        'week_days': strings.WEEK_DAYS
    }

]
