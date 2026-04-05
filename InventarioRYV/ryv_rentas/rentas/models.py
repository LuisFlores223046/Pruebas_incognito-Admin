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

    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia bancaria'),
        ('tarjeta', 'Tarjeta'),
        ('otro', 'Otro'),
    ]

    CONDICION_CHOICES = [
        ('bueno', 'Bueno — sin daños'),
        ('daños_menores', 'Daños menores'),
        ('inservible', 'Inservible / Pérdida total'),
        ('extraviado', 'Extraviado'),
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
    monto_recibido = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='monto recibido al cierre (MXN)',
        help_text='Cantidad que pagó el cliente al devolver el equipo.',
    )
    cambio_entregado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='cambio entregado (MXN)',
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        blank=True,
        default='',
        verbose_name='método de pago (depósito)',
    )
    metodo_pago_cierre = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        blank=True,
        default='',
        verbose_name='método de pago (cierre)',
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name='cantidad',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activa',
        verbose_name='estado',
    )
    condicion_devolucion = models.CharField(
        max_length=20,
        choices=CONDICION_CHOICES,
        blank=True,
        default='',
        verbose_name='condición al devolver',
    )
    cargo_daños = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='cargo por daños (MXN)',
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
    def saldo_pendiente(self):
        """Lo que el cliente aún debe pagar al devolver (precio - depósito)."""
        return max(self.precio - self.deposito, 0)

    @property
    def sobrante_deposito(self):
        """Cuánto sobró si el depósito fue mayor al precio total."""
        if self.deposito > self.precio:
            return self.deposito - self.precio
        return None

    @property
    def cambio_a_devolver(self):
        """
        Cambio que se le regresa al cliente.
        Solo disponible cuando monto_recibido está registrado.
        Positivo = cambio a devolver; negativo = todavía debe.
        """
        if self.monto_recibido is None:
            return None
        return self.monto_recibido - self.saldo_pendiente

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

    @property
    def nombre_equipo_display(self):
        """Nombre del equipo para vistas de lista (soporta múltiples items)."""
        items = list(self.items.select_related('equipo').all())
        if items:
            if len(items) > 1:
                return f'{items[0].equipo.nombre} (+{len(items) - 1} más)'
            return items[0].equipo.nombre
        return self.equipo.nombre if self.equipo_id else '—'

    @property
    def cantidad_total_equipos(self):
        """Cantidad total de unidades rentadas en todos los items."""
        items = list(self.items.all())
        if items:
            return sum(i.cantidad for i in items)
        return self.cantidad


class RentaEquipo(models.Model):
    """Equipo incluido en una renta. Permite múltiples herramientas por renta."""

    renta = models.ForeignKey(
        Renta,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='renta',
    )
    equipo = models.ForeignKey(
        'inventario.Equipo',
        on_delete=models.PROTECT,
        related_name='renta_items',
        verbose_name='equipo',
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name='cantidad',
    )

    class Meta:
        verbose_name = 'equipo de renta'
        verbose_name_plural = 'equipos de renta'

    def __str__(self):
        return f'{self.cantidad}x {self.equipo.nombre}'
