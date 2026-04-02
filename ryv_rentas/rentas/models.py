"""Modelos para el módulo de rentas."""
from django.db import models


class Cliente(models.Model):
    """Cliente que renta equipo. Solo datos de contacto (RN-010)."""

    nombre = models.CharField(
        max_length=200,
        verbose_name='nombre',
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name='teléfono',
    )
    direccion = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='dirección',
    )
    correo = models.EmailField(
        blank=True,
        verbose_name='correo electrónico',
    )
    notas = models.TextField(
        blank=True,
        verbose_name='notas',
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de registro',
    )

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'
        ordering = ['nombre']

    def __str__(self):
        """Representación en texto del cliente."""
        return self.nombre


class Renta(models.Model):
    """
    Renta de un equipo a un cliente.
    Gestiona el ciclo de vida: activa → finalizada/vencida.
    """

    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('finalizada', 'Finalizada'),
        ('vencida', 'Vencida'),
    ]
    equipo = models.ForeignKey(
        'inventario.Equipo',
        on_delete=models.PROTECT,
        related_name='rentas',
        verbose_name='equipo',
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='rentas',
        verbose_name='cliente',
    )
    registrada_por = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='rentas_registradas',
        verbose_name='registrada por',
    )
    fecha_inicio = models.DateField(
        verbose_name='fecha de inicio',
    )
    fecha_vencimiento = models.DateField(
        verbose_name='fecha de vencimiento',
    )
    fecha_devolucion = models.DateField(
        null=True,
        blank=True,
        verbose_name='fecha de devolución',
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='precio (MXN)',
    )
    deposito = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='depósito (MXN)',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activa',
        verbose_name='estado',
    )
    notas = models.TextField(
        blank=True,
        verbose_name='notas',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='creada el',
    )

    class Meta:
        verbose_name = 'renta'
        verbose_name_plural = 'rentas'
        ordering = ['fecha_vencimiento']

    def __str__(self):
        """Representación en texto de la renta."""
        return f"{self.equipo} - {self.cliente} ({self.estado})"

    @property
    def dias_para_vencer(self):
        """
        Días restantes hasta el vencimiento.
        Retorna None si la renta no está activa.
        Valor negativo indica que ya venció.
        """
        from datetime import date
        if self.estado == 'activa':
            return (self.fecha_vencimiento - date.today()).days
        return None

    @property
    def esta_por_vencer(self):
        """True si vence en 3 días o menos (pero aún no venció)."""
        dias = self.dias_para_vencer
        return dias is not None and 0 <= dias <= 3

    @property
    def esta_vencida_sin_cerrar(self):
        """True si ya venció pero sigue con estado activa."""
        dias = self.dias_para_vencer
        return dias is not None and dias < 0
