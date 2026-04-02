"""Configuración de la app de autenticación."""
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Configuración de la app authentication."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    verbose_name = 'Autenticación'
