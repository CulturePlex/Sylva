try:
    from sylva.settings import *
except ImportError:
    pass

DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

COMPRESS_ENABLED = False  # By default it's the opposite to 'DEBUG'
