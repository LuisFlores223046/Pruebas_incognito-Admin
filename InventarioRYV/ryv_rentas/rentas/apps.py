"""Configuración de la app de rentas."""
from django.apps import AppConfig


class RentasConfig(AppConfig):
    """Configuración de la app rentas."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rentas'
    verbose_name = 'Rentas'
