try:
    from sylva.settings import *
except ImportError:
    pass

DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

COMPRESS_ENABLED = False
# COMPRESS_ENABLED = True  # By default it's the opposite to 'DEBUG'
# COMPRESS_ROOT = STATIC_ROOT

# # About the next two lines, the usual thing is do the reverse thing, first
# # create the 'COMPRESS_URL' and after that link it to 'STATIC_URL'
# STATIC_URL = 'http://localhost:8001/static/'
# COMPRESS_URL = STATIC_URL

# COMPRESS_OFFLINE = True
# COMPRESS_OFFLINE_CONTEXT = {
#     'base_template': 'base.html',
#     'STATIC_PREFIX': STATIC_URL,
#     'as_modal': True,
#     'OPTIONS': {
#         'ENABLE_ANALYTICS': True
#     },
# }
