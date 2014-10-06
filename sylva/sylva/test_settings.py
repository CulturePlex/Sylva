try:
    from sylva.settings import *
except ImportError:
    pass

DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

TEST = True

COMPRESS_ENABLED = True  # By default it's the opposite to 'DEBUG'
COMPRESS_ROOT = STATIC_ROOT

COMPRESS_URL = STATIC_URL

COMPRESS_OFFLINE = True
COMPRESS_OFFLINE_CONTEXT = {
    'base_template': 'base.html',
    'STATIC_PREFIX': STATIC_URL,
    'as_modal': True,
    'OPTIONS': {
        'ENABLE_ANALYTICS': True
    },
}
