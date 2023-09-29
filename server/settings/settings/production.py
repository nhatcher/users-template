import environ
import sentry_sdk

from .common import *  # noqa

env = environ.Env()

# Take environment variables from .env file
environ.Env.read_env("/etc/django.env")

sentry_sdk.init(
    dsn=env("SENTRY_DNS"),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

DEBUG = False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
ALLOWED_HOSTS = [env("HOST")]

APP_URL = env("APP_URL")
STATIC_ROOT = env("STATIC_ROOT")

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

SECRET_KEY = env("SECRET_KEY")

EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

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
        "file": {
            "class": "logging.FileHandler",
            "filename": "debug.log",
            "formatter": "verbose",
        },
        "sentry": {
            "class": "sentry_sdk.integrations.logging.EventHandler",
        },
    },
    "root": {
        "handlers": ["file", "sentry"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
