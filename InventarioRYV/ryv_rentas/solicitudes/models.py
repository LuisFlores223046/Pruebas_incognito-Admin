"""Modelos para el módulo de solicitudes."""
from django.db import models


class Solicitud(models.Model):
    """
    Solicitud de cambio enviada por un empleado.
    El administrador la aprueba o rechaza (RN-008).
    """

    TIPO_CHOICES = [
        ('alta_equipo', 'Alta de equipo'),
        ('edicion_equipo', 'Edición de equipo'),
        ('baja_equipo', 'Baja de equipo'),
        ('nueva_renta', 'Nueva renta'),
        ('cierre_renta', 'Cierre de renta'),
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name='tipo',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='estado',
    )
    solicitante = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.CASCADE,
        related_name='solicitudes_enviadas',
        verbose_name='solicitante',
    )
    equipo = models.ForeignKey(
        'inventario.Equipo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='equipo',
    )
    renta = models.ForeignKey(
        'rentas.Renta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='renta',
    )
    comentario = models.TextField(
        verbose_name='comentario',
    )
    datos_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name='datos adicionales (JSON)',
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de creación',
    )
    fecha_resolucion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='fecha de resolución',
    )
    resuelto_por = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_resueltas',
        verbose_name='resuelto por',
    )

    class Meta:
        verbose_name = 'solicitud'
        verbose_name_plural = 'solicitudes'
        ordering = ['-fecha_creacion']

    def __str__(self):
        """Representación en texto de la solicitud."""
        return (
            f"{self.get_tipo_display()} - "
            f"{self.solicitante} ({self.get_estado_display()})"
        )
