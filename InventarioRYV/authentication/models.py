"""
Archivo: models.py
Descripción: Modelos de autenticación para el sistema RYV Rentas.
             Define el modelo de usuario personalizado que extiende
             AbstractUser de Django, agregando el campo de rol para
             el control de acceso definido en RF-03 y RN-008 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario personalizado que extiende AbstractUser de Django.

    Agrega el campo rol para diferenciar permisos entre Administrador
    y Empleado dentro del sistema, siguiendo las reglas de acceso
    definidas en RF-03 y RN-008 del SRS.

    Atributos:
        rol (str): Rol asignado al usuario. Puede ser 'administrador'
        o 'empleado'. Por defecto es 'empleado'.
    """

    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('empleado', 'Empleado'),
    ]
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='empleado',
        verbose_name='rol',
    )

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def es_administrador(self):
        """
        Verifica si el usuario tiene rol de Administrador.

        Returns:
            bool: True si el rol del usuario es 'administrador', False en caso contrario.
        """
        return self.rol == 'administrador'

    def es_empleado(self):
        """
        Verifica si el usuario tiene rol de Empleado.

        Returns:
            bool: True si el rol del usuario es 'empleado', False en caso contrario.
        """
        return self.rol == 'empleado'
