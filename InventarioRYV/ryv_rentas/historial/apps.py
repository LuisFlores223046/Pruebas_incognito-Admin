"""Configuración de la app de historial."""
from django.apps import AppConfig


class HistorialConfig(AppConfig):
    """Configuración de la app historial."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'historial'
    verbose_name = 'Historial'
