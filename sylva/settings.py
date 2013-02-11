# -*- coding: utf-8 -*-
from os import path

# from django.utils.translation import gettext_lazy as _

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ugettext = lambda s: s

PROJECT_NAME = u"SylvaDB"
PROJECT_ROOT = path.dirname(path.abspath(__file__))

ADMINS = (
    ('Sylva', 'info@sylvadb.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': path.join(PROJECT_ROOT, 'sylva.sqlite'),          # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
GRAPHDATABASES = {
    'default': {
        'ENGINE': 'engines.gdb.backends.neo4j',
        'NAME': 'db/sylva',  # Changed to avoid overwrites from testing
        'USER': '',
        'PASSWORD': '',
        'SCHEMA': 'http',
        'HOST': 'localhost',
        'PORT': '7373',  # Changed to avoid overwrites from testing
    },
    'tests': {
        'ENGINE': 'engines.gdb.backends.neo4j',
        'NAME': 'db/data',
        'USER': '',
        'PASSWORD': '',
        'SCHEMA': 'http',
        'HOST': 'localhost',
        'PORT': '7474',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Toronto'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-ca'

# Supported translations
LANGUAGES = (
    ('en', ugettext('English')),
    # ('es', ugettext('Español')),
)

# I18n
LOCALE_PATHS = (
    path.join(PROJECT_ROOT, 'locale'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9s-jun0(l@mv(up-3v3#25sk#6=#g1&%ojnsus7y*nttqq_pr6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    # "django.core.context_processors.auth",
    "django.contrib.auth.context_processors.auth",
    'django.contrib.messages.context_processors.messages',
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.csrf",
    "base.context_processors.project_name",
    "base.context_processors.current_date",
    "base.context_processors.google_api_key",
    "base.context_processors.google_analytics_code",
    "base.context_processors.debug",
    "base.context_processors.logout",
    "base.context_processors.site",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'base.middleware.ProfileMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Override brand
    path.join(PROJECT_ROOT, 'base', 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'accounts',
    'userena',
    'userena.contrib.umessages',
    'guardian',
    'easy_thumbnails',
    'tinymce',
    'base',
    'data',
    'graphs',
    'schemas',
    'engines',
    'tools',
    'search',
    'operators',
    'zebra',
    'payments',
    'south',
)

AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ANONYMOUS_USER_ID = -1
AUTH_PROFILE_MODULE = "accounts.UserProfile"
LOGIN_REDIRECT_URL = '/dashboard/'  # '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'gdb': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'gdb-cache',
        'TIMEOUT': 7 * 24 * 60 * 60,  # One week. It's not changing a lot
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'payments': {
            'handlers': ['console'],
            'level': "INFO",
            'propagate': False,
        },
    }
}

# TinyMCE
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_buttons1': 'bold,italic,underline,strikethrough,separator,link,separator,undo,redo,separator,cleanup,separator,bullist,numlist,separator,code',
    'theme_advanced_buttons2': '',
    'theme_advanced_buttons3': '',
}

# Django settings
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
DEFAULT_FROM_EMAIL = "\"SylvaDB\" <info@sylvadb.com>"

# Profiling
PROFILE_MIDDLEWARE_SORT = ["cumulative", "calls"]
PROFILE_MIDDLEWARE_RESTRICTIONS = [0.2]
PROFILE_MIDDLEWARE_JSON = True

# Userena settings
USERENA_DEFAULT_PRIVACY = "open"
USERENA_DISABLE_PROFILE_LIST = False
USERENA_WITHOUT_USERNAMES = False
USERENA_HIDE_EMAIL = True
USERENA_LANGUAGE_FIELD = "language"
USERENA_SIGNIN_REDIRECT_URL = LOGIN_REDIRECT_URL
USERENA_MUGSHOT_GRAVATAR = True
USERENA_MUGSHOT_DEFAULT = "mm"
USERENA_MUGSHOT_SIZE = 100
USERENA_USE_MESSAGES = False

# Guardian
GUARDIAN_RENDER_403 = True
GUARDIAN_TEMPLATE_403 = '403.html'

# Sylva settings
GOOGLE_ANALYTICS_CODE = "UA-1613313-12"
ACCOUNT_FREE = {
    "name": "Free account",
    "type": 1,  # Free
    "graphs": 10,
    "nodes": 1000,
    "relationships": 10000,
    "storage": 100 * 1024 * 1024,
    "queries": 10,
}
ENABLE_INSTANCES = False
ENABLE_INHERITANCE = False
ENABLE_AUTOCOMPLETE_NODES = True
ENABLE_SEARCH = True
ENABLE_CLONING = False
ENABLE_PROFILE = False
ENABLE_SIGNUP = True
ENABLE_TYPE_VALIDATION_FORMS = False
ENABLE_PAYMENTS = True
ACTIVATION_EMAIL_BETA_MESSAGE = True
MAINTENANCE_MODE = False
PREVIEW_NODES = 200  # Size of the graph preview in the graph screen
MAX_SIZE = 300  # Disable graph preview (Processing) nodes number is above this value
# OPTIONS is a dictionary made available in templates
OPTIONS = {
    "ACCOUNT_FREE": ACCOUNT_FREE,
    "ENABLE_INSTANCES": ENABLE_INSTANCES,
    "ENABLE_INHERITANCE": ENABLE_INHERITANCE,
    "ENABLE_AUTOCOMPLETE_NODES": ENABLE_AUTOCOMPLETE_NODES,
    "ENABLE_SEARCH": ENABLE_SEARCH,
    "ENABLE_SIGNUP": ENABLE_SIGNUP,
    "ENABLE_TYPE_VALIDATION_FORMS": ENABLE_TYPE_VALIDATION_FORMS,
    "MAINTENANCE_MODE": MAINTENANCE_MODE,
    "PREVIEW_NODES": PREVIEW_NODES,
    "DEFAULT_FROM_EMAIL": DEFAULT_FROM_EMAIL,
    "ACTIVATION_EMAIL_BETA_MESSAGE": ACTIVATION_EMAIL_BETA_MESSAGE,
}

# django-zebra

STRIPE_SECRET = ""  # set in local settings
STRIPE_PUBLISHABLE = ""  # set in local settings

ZEBRA_AUTO_CREATE_STRIPE_CUSTOMERS = False
ZEBRA_CUSTOMER_MODEL = 'payments.StripeCustomer'

STRIPE_PLANS = {
    '2': {
        'name': 'Basic',
        'price': 4.99,
        'account_type': 2
    },
    '3': {
        'name': 'Premium',
        'price': 9.99,
        'account_type': 3
    }
}
