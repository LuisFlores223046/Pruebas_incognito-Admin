"""Configuración de la app de inicio."""
from django.apps import AppConfig


class InicioConfig(AppConfig):
    """Configuración de la app inicio."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inicio'
    verbose_name = 'Inicio'
