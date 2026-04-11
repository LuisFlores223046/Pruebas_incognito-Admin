"""
Archivo: models.py
Descripción: Modelos para el módulo de solicitudes del sistema RYV Rentas.
             Define el modelo Solicitud que gestiona el flujo de aprobación
             entre el Empleado y el Administrador para cambios en inventario
             y rentas, según lo definido en RF-06, RF-08, RF-10, RF-12,
             RF-14, RF-18 y RN-008 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.db import models


class Solicitud(models.Model):
    """
    Representa una solicitud de cambio enviada por el Empleado al Administrador.

    Gestiona el flujo de aprobación para operaciones de alta, edición y baja
    de equipos, así como el registro y cierre de rentas. El Administrador
    aprueba o rechaza cada solicitud desde el panel de administración,
    cumpliendo con RN-008 del SRS.

    Atributos:
        tipo (str): Tipo de operación solicitada. Puede ser alta_equipo,
        edicion_equipo, baja_equipo, nueva_renta o cierre_renta.
        estado (str): Estado actual de la solicitud: pendiente, aprobada
        o rechazada. Por defecto es 'pendiente'.
        solicitante (Usuario): Empleado que envió la solicitud.
        equipo (Equipo): Equipo involucrado en la solicitud. Campo opcional.
        renta (Renta): Renta involucrada en la solicitud. Campo opcional.
        Solo aplica para solicitudes de tipo nueva_renta y cierre_renta.
        comentario (str): Motivo u observaciones del Empleado. Obligatorio.
        datos_json (dict): Datos adicionales de la solicitud serializados
        en formato JSON. Campo opcional.
        fecha_creacion (datetime): Fecha y hora en que se creó la solicitud.
        fecha_resolucion (datetime): Fecha y hora en que el Administrador
        resolvió la solicitud. Campo opcional.
        resuelto_por (Usuario): Administrador que aprobó o rechazó la
        solicitud. Campo opcional.
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
        """
        Retorna la representación en texto de la solicitud.

        Retorna:
            str: Cadena con el tipo de solicitud, el solicitante
            y el estado actual.
        """
        return (
            f"{self.get_tipo_display()} - "
            f"{self.solicitante} ({self.get_estado_display()})"
        )
