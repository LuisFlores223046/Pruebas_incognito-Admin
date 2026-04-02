"""Modelos para el módulo de inventario."""
from django.db import models


class Categoria(models.Model):
    """Categoría de equipos (ej: Herramienta eléctrica, Maquinaria)."""

    nombre = models.CharField(
        max_length=100,
        verbose_name='nombre',
    )

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['nombre']

    def __str__(self):
        """Representación en texto de la categoría."""
        return self.nombre


class Equipo(models.Model):
    """
    Equipo o herramienta disponible para renta.
    Gestiona disponibilidad y estado operativo.
    """

    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('rentado', 'Rentado'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    nombre = models.CharField(
        max_length=200,
        verbose_name='nombre',
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipos',
        verbose_name='categoría',
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='descripción',
    )
    cantidad_total = models.PositiveIntegerField(
        default=1,
        verbose_name='cantidad total',
    )
    cantidad_disponible = models.PositiveIntegerField(
        default=1,
        verbose_name='cantidad disponible',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name='estado',
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='activo',
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de registro',
    )

    class Meta:
        verbose_name = 'equipo'
        verbose_name_plural = 'equipos'
        ordering = ['nombre']

    def __str__(self):
        """Representación en texto del equipo."""
        return self.nombre

    def tiene_renta_activa(self):
        """Retorna True si el equipo tiene al menos una renta activa."""
        return self.rentas.filter(estado='activa').exists()
