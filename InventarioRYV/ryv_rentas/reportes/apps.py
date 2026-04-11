"""
Archivo: apps.py
Descripción: Configuración de la aplicación de reportes para el sistema RYV Rentas.
             Define los parámetros de registro de la app reportes dentro
             del proyecto Django.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.apps import AppConfig


class ReportesConfig(AppConfig):
    """
    Configuración de la aplicación reportes.

    Registra la app dentro del proyecto Django y define
    sus parámetros básicos de configuración.

    Atributos:
        default_auto_field (str): Tipo de campo automático para las claves
        primarias. Se usa BigAutoField por defecto.
        name (str): Nombre interno de la aplicación dentro del proyecto.
        verbose_name (str): Nombre legible de la aplicación para el panel
        de administración de Django.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reportes'
    verbose_name = 'Reportes'
