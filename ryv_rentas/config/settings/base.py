"""Configuración base del proyecto RYV Rentas."""
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps del proyecto
    'authentication',
    'inventario',
    'rentas',
    'solicitudes',
    'historial',
    'reportes',
    'panel_admin',
    'inicio',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = 'authentication.Usuario'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.alertas_globales',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Chihuahua'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sesión expira a los 30 minutos de inactividad
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/rentas/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# Validaciones de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation'
            '.MinimumLengthValidator'
        ),
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation'
            '.CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation'
            '.NumericPasswordValidator'
        ),
    },
]
