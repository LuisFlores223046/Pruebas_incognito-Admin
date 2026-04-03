"""Configuración de la app de reportes."""
from django.apps import AppConfig


class ReportesConfig(AppConfig):
    """Configuración de la app reportes."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reportes'
    verbose_name = 'Reportes'
