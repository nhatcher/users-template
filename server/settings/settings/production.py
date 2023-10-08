import sentry_sdk
import configparser

from .common import *  # noqa

# Take secrets and settings from the config file
config = configparser.ConfigParser(interpolation=None)
config.read("/etc/server_config.ini")

DEBUG = False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
ALLOWED_HOSTS = [config["django"]["host"]]

APP_URL = config["django"]["app_url"]
STATIC_ROOT = config["django"]["static_root"]
SECRET_KEY = config["django"]["database"]

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config["database"]["name"],
        "USER": config["database"]["user"],
        "PASSWORD": config["database"]["password"],
        "HOST": "127.0.0.1",
        "PORT": "",
    }
}

EMAIL_HOST = config["email"]["host"]
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = config["email"]["host_user"]
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = config["email"]["host_password"]


sentry_sdk.init(
    dsn=config["sentry"]["dns"],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

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
