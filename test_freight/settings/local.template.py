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

ALLIANCE_ID = 498125261

FREIGHT_PARAMETERS = {
    "collateral_rate": 0.01,
    "max_size": 300000,
    "min_price": 5000000,
    "recommended_collateral": 5000000000,
    "recommended_size": 5000000000,
}