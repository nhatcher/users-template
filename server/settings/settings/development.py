from pathlib import Path

from .common import *  # noqa

DEBUG = True

# BASE_DIR is where manage.py lives
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# We use a sqlite3 database during development
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

APP_URL = "http://localhost:2080/"

# This is a crucial security setting used for various purposes, including generating CSRF tokens,
# session management, and more. During development any value will work fine.
SECRET_KEY = "It doesn't really matter"

# emails are never sent during development, you will find  the content in your terminal
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# We log everything to the terminal
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
