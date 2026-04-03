"""Configuración de la app de solicitudes."""
from django.apps import AppConfig


class SolicitudesConfig(AppConfig):
    """Configuración de la app solicitudes."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'solicitudes'
    verbose_name = 'Solicitudes'
