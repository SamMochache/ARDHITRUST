# config/settings/test.py
from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ardhitrust_test",
        "USER": "ardhitrust",
        "PASSWORD": "testpass",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

CELERY_TASK_ALWAYS_EAGER = True       # run tasks synchronously in tests
CELERY_TASK_EAGER_PROPAGATES = True

ARDHISASA_MOCK_MODE = True
IPRS_MOCK_MODE = True

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",  # fast hashing in tests
]

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}