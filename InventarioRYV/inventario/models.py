"""
Archivo: models.py
Descripción: Modelos para el módulo de inventario del sistema RYV Rentas.
             Define el modelo Equipo que gestiona las herramientas y maquinaria
             disponibles para renta, incluyendo el control de disponibilidad
             por cantidades, según lo definido en RF-05 al RF-12 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.db import models


class Equipo(models.Model):
    """
    Representa una herramienta o maquinaria disponible para renta.

    Gestiona la disponibilidad mediante cantidades granulares que permiten
    controlar cuántas unidades están disponibles, rentadas o en mantenimiento
    en tiempo real, según lo definido en RF-05 y RN-001 del SRS.

    Atributos:
        nombre (str): Nombre descriptivo del equipo.
        descripcion (str): Descripción detallada del equipo. Campo opcional.
        cantidad_total (int): Total de unidades registradas del equipo.
        cantidad_en_renta (int): Unidades actualmente rentadas.
        cantidad_en_mantenimiento (int): Unidades fuera de servicio.
        imagen (ImageField): Imagen de referencia del equipo. Campo opcional.
        activo (bool): Indica si el equipo está activo en el inventario.
        fecha_registro (datetime): Fecha y hora en que se registró el equipo.
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
        """
        Retorna la representación en texto del equipo.

        Retorna:
            str: Nombre del equipo.
        """
        return self.nombre

    @property
    def cantidad_disponible(self):
        """
        Calcula las unidades disponibles para renta en tiempo real.

        Resta las unidades en renta y en mantenimiento del total registrado.
        El resultado nunca es menor a cero.

        Retorna:
            int: Número de unidades disponibles para nueva renta.
        """
        return max(
            0,
            self.cantidad_total
            - self.cantidad_en_renta
            - self.cantidad_en_mantenimiento,
        )

    @property
    def estado(self):
        """
        Determina el estado del equipo para su visualización en el sistema.

        El estado se deriva de las cantidades registradas y puede ser
        uno de los siguientes valores: disponible, parcial, rentado
        o mantenimiento.

        Retorna:
            str: Estado del equipo. Valores posibles: 'disponible',
            'parcial', 'rentado' o 'mantenimiento'.
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
        """
        Retorna el texto legible del estado del equipo para mostrar en plantillas.

        Retorna:
            str: Texto descriptivo del estado. Valores posibles:
            'Disponible', 'Parcialmente disponible',
            'Todo rentado' o 'En mantenimiento'.
        """
        mapa = {
            'disponible': 'Disponible',
            'parcial': 'Parcialmente disponible',
            'rentado': 'Todo rentado',
            'mantenimiento': 'En mantenimiento',
        }
        return mapa.get(self.estado, self.estado.capitalize())

    def tiene_renta_activa(self):
        """
        Verifica si el equipo tiene al menos una unidad actualmente rentada.

        Retorna:
            bool: True si cantidad_en_renta es mayor a cero, False en caso contrario.
        """
        return self.cantidad_en_renta > 0

    def tiene_disponibles(self, cantidad=1):
        """
        Verifica si el equipo tiene suficientes unidades disponibles para renta.

        Parámetros:
            cantidad (int): Número de unidades requeridas. Por defecto es 1.

        Retorna:
            bool: True si hay suficientes unidades disponibles, False en caso contrario.
        """
        return self.cantidad_disponible >= cantidad
