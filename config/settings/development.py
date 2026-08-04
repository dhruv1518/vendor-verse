from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Email — print to terminal during development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
