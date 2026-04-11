"""
Archivo: models.py
Descripción: Modelos para el módulo de rentas del sistema RYV Rentas.
             Define los modelos Cliente, Renta y RentaEquipo que gestionan
             el ciclo de vida completo de una renta, desde su registro hasta
             su cierre, según lo definido en RF-13 al RF-19, RN-001 al RN-005
             y RN-010 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.db import models


class Cliente(models.Model):
    """
    Representa un cliente que renta equipo o maquinaria de RYV Rentas.

    Solo almacena datos de contacto básicos. No se guardan datos financieros
    sensibles como números de tarjeta o cuentas bancarias, cumpliendo con
    RN-010 y RNF-006 del SRS.

    Atributos:
        nombre (str): Nombre completo del cliente. Campo obligatorio.
        telefono (str): Número de teléfono de contacto. Campo obligatorio.
        direccion (str): Dirección del cliente. Campo opcional.
        correo (str): Correo electrónico del cliente. Campo opcional.
        notas (str): Observaciones adicionales sobre el cliente. Campo opcional.
        fecha_registro (datetime): Fecha y hora en que se registró el cliente.
    """

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
        """
        Retorna la representación en texto del cliente.

        Retorna:
            str: Nombre completo del cliente.
        """
        return self.nombre


class Renta(models.Model):
    """
    Representa el ciclo de vida completo de una renta de equipo o maquinaria.

    Gestiona el flujo desde la creación de la renta (estado activa) hasta
    su cierre (finalizada o vencida), incluyendo el control de pagos,
    depósitos, condición de devolución y alertas de vencimiento,
    según lo definido en RF-13 al RF-19 y RN-001 al RN-004 del SRS.

    Atributos:
        equipo (Equipo): Equipo principal asociado a la renta.
        cliente (Cliente): Cliente que realiza la renta.
        registrada_por (Usuario): Usuario que registró la renta en el sistema.
        fecha_inicio (date): Fecha en que inicia la renta.
        fecha_vencimiento (date): Fecha límite de devolución del equipo.
        fecha_devolucion (date): Fecha real en que se devolvió el equipo. Campo opcional.
        precio (Decimal): Precio total de la renta en pesos mexicanos (MXN).
        deposito (Decimal): Depósito de garantía entregado por el cliente en MXN.
        monto_recibido (Decimal): Monto recibido del cliente al cerrar la renta. Campo opcional.
        cambio_entregado (Decimal): Cambio devuelto al cliente al cierre. Campo opcional.
        metodo_pago (str): Método de pago utilizado para el depósito.
        metodo_pago_cierre (str): Método de pago utilizado al cerrar la renta.
        cantidad (int): Número de unidades rentadas del equipo principal.
        estado (str): Estado actual de la renta: activa, finalizada o vencida.
        condicion_devolucion (str): Condición del equipo al momento de la devolución.
        cargo_daños (Decimal): Cargo adicional por daños al equipo. Campo opcional.
        notas (str): Observaciones adicionales sobre la renta. Campo opcional.
        created_at (datetime): Fecha y hora en que se registró la renta.
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
        """
        Retorna la representación en texto de la renta.

        Retorna:
            str: Cadena con el equipo, cliente y estado actual de la renta.
        """
        return f"{self.equipo} - {self.cliente} ({self.estado})"

    @property
    def saldo_pendiente(self):
        """
        Calcula el saldo que el cliente aún debe pagar al devolver el equipo.

        Resta el depósito entregado al precio total de la renta.
        El resultado nunca es menor a cero.

        Retorna:
            Decimal: Monto pendiente de pago en MXN.
        """
        return max(self.precio - self.deposito, 0)

    @property
    def sobrante_deposito(self):
        """
        Calcula el sobrante del depósito si fue mayor al precio total.

        Retorna:
            Decimal: Monto sobrante en MXN si el depósito supera el precio,
            o None si el depósito es menor o igual al precio.
        """
        if self.deposito > self.precio:
            return self.deposito - self.precio
        return None

    @property
    def cambio_a_devolver(self):
        """
        Calcula el cambio que se le regresa al cliente al cerrar la renta.

        Solo disponible cuando monto_recibido está registrado. Un valor
        positivo indica cambio a devolver al cliente; un valor negativo
        indica que el cliente aún tiene saldo pendiente.

        Retorna:
            Decimal: Diferencia entre monto recibido y saldo pendiente en MXN,
            o None si monto_recibido no ha sido registrado.
        """
        if self.monto_recibido is None:
            return None
        return self.monto_recibido - self.saldo_pendiente

    @property
    def dias_para_vencer(self):
        """
        Calcula los días restantes hasta el vencimiento de la renta.

        Un valor negativo indica que la renta ya venció. Solo aplica
        para rentas con estado activa, cumpliendo con RN-004 del SRS.

        Retorna:
            int: Días restantes hasta la fecha de vencimiento,
            o None si la renta no está activa.
        """
        from datetime import date
        if self.estado == 'activa':
            return (self.fecha_vencimiento - date.today()).days
        return None

    @property
    def esta_por_vencer(self):
        """
        Verifica si la renta vence en 3 días o menos pero aún no ha vencido.

        Activa las alertas visuales en el dashboard según RN-004 del SRS,
        que establece el umbral de alerta en 3 días antes del vencimiento.

        Retorna:
            bool: True si la renta vence en 3 días o menos, False en caso contrario.
        """
        dias = self.dias_para_vencer
        return dias is not None and 0 <= dias <= 3

    @property
    def esta_vencida_sin_cerrar(self):
        """
        Verifica si la renta ya venció pero sigue registrada como activa.

        Identifica rentas que requieren atención inmediata por haber superado
        su fecha de vencimiento sin ser finalizadas.

        Retorna:
            bool: True si la renta venció y aún está activa, False en caso contrario.
        """
        dias = self.dias_para_vencer
        return dias is not None and dias < 0

    @property
    def nombre_equipo_display(self):
        """
        Retorna el nombre del equipo formateado para vistas de lista.

        Si la renta tiene múltiples equipos asociados mediante items,
        muestra el nombre del primero seguido de la cantidad adicional.

        Retorna:
            str: Nombre del equipo principal, con indicador de equipos
            adicionales si aplica, o '—' si no hay equipo asociado.
        """
        items = list(self.items.select_related('equipo').all())
        if items:
            if len(items) > 1:
                return f'{items[0].equipo.nombre} (+{len(items) - 1} más)'
            return items[0].equipo.nombre
        return self.equipo.nombre if self.equipo_id else '—'

    @property
    def cantidad_total_equipos(self):
        """
        Calcula la cantidad total de unidades rentadas en todos los items.

        Si la renta tiene items asociados, suma sus cantidades. En caso
        contrario retorna la cantidad del equipo principal.

        Retorna:
            int: Total de unidades rentadas en la renta.
        """
        items = list(self.items.all())
        if items:
            return sum(i.cantidad for i in items)
        return self.cantidad


class RentaEquipo(models.Model):
    """
    Representa un equipo incluido dentro de una renta.

    Permite asociar múltiples herramientas o equipos a una misma renta,
    indicando la cantidad de unidades rentadas por cada uno.

    Atributos:
        renta (Renta): Renta a la que pertenece este item.
        equipo (Equipo): Equipo asociado al item de la renta.
        cantidad (int): Número de unidades rentadas de este equipo.
    """

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
        """
        Retorna la representación en texto del item de renta.

        Retorna:
            str: Cadena con la cantidad y nombre del equipo rentado.
        """
        return f'{self.cantidad}x {self.equipo.nombre}'
