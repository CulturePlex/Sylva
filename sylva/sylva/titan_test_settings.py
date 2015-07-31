try:
    from sylva.test_settings import *
except ImportError:
    pass

GRAPHDATABASES = {
    'default': {
        'ENGINE': 'engines.gdb.backends.titan',
        'NAME': '',  # Changed to avoid overwrites from testing
        'USER': '',
        'PASSWORD': '',
        'SCHEMA': 'http',
        'HOST': 'localhost',
        'PORT': '8182',  # Changed to avoid overwrites from testing
    },
    'tests': {
        'ENGINE': 'engines.gdb.backends.titan',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'SCHEMA': 'http',
        'HOST': 'localhost',
        'PORT': '8182',
    }
}

ENABLE_REPORTS = False
ENABLE_QUERIES = False
