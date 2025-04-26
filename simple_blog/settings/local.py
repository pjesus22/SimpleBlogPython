from .base import *  # noqa: F403, F405

DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [  # noqa: F405
    'django_extensions',
]


CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False

SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

SECURE_SSL_REDIRECT = False
