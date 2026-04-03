"""Modelos para el módulo de inventario."""
from django.db import models


class Equipo(models.Model):
    """
    Equipo o herramienta disponible para renta.
    Gestiona disponibilidad por cantidades granulares.
    """

    nombre = models.CharField(
        max_length=200,
        verbose_name='nombre',
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='descripción',
    )
    cantidad_total = models.PositiveIntegerField(
        default=1,
        verbose_name='cantidad total',
    )
    cantidad_en_renta = models.PositiveIntegerField(
        default=0,
        verbose_name='en renta',
    )
    cantidad_en_mantenimiento = models.PositiveIntegerField(
        default=0,
        verbose_name='en mantenimiento',
    )
    imagen = models.ImageField(
        upload_to='equipos/',
        blank=True,
        null=True,
        verbose_name='imagen de referencia',
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

    @property
    def cantidad_disponible(self):
        """Unidades disponibles para renta (calculado)."""
        return max(
            0,
            self.cantidad_total
            - self.cantidad_en_renta
            - self.cantidad_en_mantenimiento,
        )

    @property
    def estado(self):
        """
        Estado derivado del equipo para visualización.
        Puede ser: disponible, parcial, rentado, mantenimiento.
        """
        disp = self.cantidad_disponible
        if disp == self.cantidad_total:
            return 'disponible'
        if disp > 0:
            return 'parcial'
        if self.cantidad_en_renta > 0:
            return 'rentado'
        return 'mantenimiento'

    def get_estado_display(self):
        """Texto del estado para mostrar en templates."""
        mapa = {
            'disponible': 'Disponible',
            'parcial': 'Parcialmente disponible',
            'rentado': 'Todo rentado',
            'mantenimiento': 'En mantenimiento',
        }
        return mapa.get(self.estado, self.estado.capitalize())

    def tiene_renta_activa(self):
        """True si hay al menos una unidad en renta activa."""
        return self.cantidad_en_renta > 0

    def tiene_disponibles(self, cantidad=1):
        """True si hay suficientes unidades disponibles."""
        return self.cantidad_disponible >= cantidad
