"""Configuración de la app de inventario."""
from django.apps import AppConfig


class InventarioConfig(AppConfig):
    """Configuración de la app inventario."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'
    verbose_name = 'Inventario'
