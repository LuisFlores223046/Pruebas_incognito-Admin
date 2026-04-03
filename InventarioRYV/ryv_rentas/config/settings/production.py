"""Configuración para entorno de producción (PythonAnywhere)."""
from .base import *  # noqa: F401, F403
from decouple import config

DEBUG = False
ALLOWED_HOSTS = [
    config('PYTHONANYWHERE_HOST'),  # ej: tuusuario.pythonanywhere.com
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': config('DB_PATH'),  # ruta absoluta en PythonAnywhere
    }
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
