import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = 'youdsdsdsr-secret-key'
DEBUG = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {
            "service": "my_service",
            "passfile": ".pgpass",

        },
    }
}

INSTALLED_APPS = [
    'fitnessappdb',  # Replace with your app name
]
