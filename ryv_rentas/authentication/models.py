"""Modelos de autenticación para RYV Rentas."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario personalizado con campo de rol.
    Roles disponibles: administrador, empleado.
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
        """Retorna True si el usuario es administrador."""
        return self.rol == 'administrador'

    def es_empleado(self):
        """Retorna True si el usuario es empleado."""
        return self.rol == 'empleado'
