"""Configuración de la app panel_admin."""
from django.apps import AppConfig


class PanelAdminConfig(AppConfig):
    """Configuración de la app panel_admin."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'panel_admin'
    verbose_name = 'Panel de Administración'
