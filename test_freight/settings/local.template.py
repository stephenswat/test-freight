from .base import *

SECRET_KEY = 'sekrit'

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ESI_CALLBACK = ""
ESI_CLIENT_ID = ""
ESI_SECRET_KEY = ""
ESI_USER_AGENT = ""
