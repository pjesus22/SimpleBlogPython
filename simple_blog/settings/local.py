from .base import *  # NOQA F403

INSTALLED_APPS += [  # NOQA F405
    'django_extensions',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_testing.sqlite3',  # NOQA F405
    }
}
