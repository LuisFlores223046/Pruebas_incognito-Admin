"""Formularios para el módulo de rentas."""
from django import forms
from django.db.models import F, ExpressionWrapper, IntegerField
from .models import Renta, Cliente
from inventario.models import Equipo


def equipos_con_disponibles():
    """QuerySet de equipos activos con al menos 1 unidad disponible."""
    return Equipo.objects.filter(activo=True).annotate(
        calc_disp=ExpressionWrapper(
            F('cantidad_total')
            - F('cantidad_en_renta')
            - F('cantidad_en_mantenimiento'),
            output_field=IntegerField(),
        )
    ).filter(calc_disp__gt=0)


class RentaForm(forms.ModelForm):
    """
    Formulario para crear una renta (admin).
    Incluye campos del cliente integrados.
    """

    # Campos del cliente
    cliente_nombre = forms.CharField(
        label='Nombre del cliente',
        widget=forms.TextInput(attrs={'class': 'input-campo'}),
    )
    cliente_telefono = forms.CharField(
        label='Teléfono del cliente',
        widget=forms.TextInput(attrs={'class': 'input-campo'}),
    )
    cliente_direccion = forms.CharField(
        label='Dirección (opcional)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-campo'}),
    )
    cliente_correo = forms.EmailField(
        label='Correo electrónico (opcional)',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'input-campo'}),
    )

    class Meta:
        model = Renta
        fields = [
            'equipo',
            'cantidad',
            'fecha_inicio',
            'fecha_vencimiento',
            'precio',
            'deposito',
            'metodo_pago',
            'notas',
        ]
        widgets = {
            'equipo': forms.Select(
                attrs={'class': 'input-campo'}
            ),
            'cantidad': forms.NumberInput(
                attrs={'class': 'input-campo', 'min': 1}
            ),
            'fecha_inicio': forms.DateInput(
                attrs={'class': 'input-campo', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'fecha_vencimiento': forms.DateInput(
                attrs={'class': 'input-campo', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'precio': forms.NumberInput(
                attrs={'class': 'input-campo', 'step': '0.01'}
            ),
            'deposito': forms.NumberInput(
                attrs={'class': 'input-campo', 'step': '0.01'}
            ),
            'metodo_pago': forms.Select(
                attrs={'class': 'input-campo'}
            ),
            'notas': forms.Textarea(
                attrs={'class': 'input-campo', 'rows': 2}
            ),
        }
        labels = {
            'equipo': 'Equipo',
            'cantidad': 'Cantidad de unidades a rentar',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_vencimiento': 'Fecha de vencimiento',
            'precio': 'Precio total (MXN)',
            'deposito': 'Depósito (MXN)',
            'metodo_pago': 'Método de pago del depósito',
            'notas': 'Notas (opcional)',
        }

    def __init__(self, *args, **kwargs):
        """Filtra equipos con unidades disponibles."""
        super().__init__(*args, **kwargs)
        self.fields['equipo'].queryset = equipos_con_disponibles()

    def clean(self):
        """Valida fechas y disponibilidad del equipo."""
        cleaned = super().clean()
        fecha_inicio = cleaned.get('fecha_inicio')
        fecha_vencimiento = cleaned.get('fecha_vencimiento')
        equipo = cleaned.get('equipo')
        cantidad = cleaned.get('cantidad') or 1

        if fecha_inicio and fecha_vencimiento:
            if fecha_vencimiento <= fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de vencimiento debe ser posterior '
                    'a la fecha de inicio.'
                )

        if equipo:
            if not equipo.tiene_disponibles(cantidad):
                raise forms.ValidationError(
                    f'Solo hay {equipo.cantidad_disponible} unidad(es) '
                    f'disponible(s) de "{equipo.nombre}". '
                    f'No se pueden rentar {cantidad}.'
                )

        return cleaned


class SolicitudRentaForm(forms.Form):
    """
    Formulario para que un empleado solicite una nueva renta (RN-008).
    El administrador la aprobará desde el panel.
    """

    equipo = forms.ModelChoiceField(
        queryset=Equipo.objects.none(),
        label='Equipo',
        widget=forms.Select(attrs={'class': 'input-campo'}),
    )
    cantidad = forms.IntegerField(
        label='Cantidad de unidades a rentar',
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={'class': 'input-campo', 'min': 1}
        ),
    )
    cliente_nombre = forms.CharField(
        label='Nombre del cliente',
        widget=forms.TextInput(attrs={'class': 'input-campo'}),
    )
    cliente_telefono = forms.CharField(
        label='Teléfono del cliente',
        widget=forms.TextInput(attrs={'class': 'input-campo'}),
    )
    cliente_direccion = forms.CharField(
        label='Dirección (opcional)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-campo'}),
    )
    cliente_correo = forms.EmailField(
        label='Correo electrónico (opcional)',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'input-campo'}),
    )
    fecha_inicio = forms.DateField(
        label='Fecha de inicio',
        widget=forms.DateInput(
            attrs={'class': 'input-campo', 'type': 'date'},
            format='%Y-%m-%d',
        ),
    )
    fecha_vencimiento = forms.DateField(
        label='Fecha de vencimiento',
        widget=forms.DateInput(
            attrs={'class': 'input-campo', 'type': 'date'},
            format='%Y-%m-%d',
        ),
    )
    precio = forms.DecimalField(
        label='Precio total (MXN)',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'input-campo', 'step': '0.01'}
        ),
    )
    deposito = forms.DecimalField(
        label='Depósito (MXN)',
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={'class': 'input-campo', 'step': '0.01'}
        ),
    )
    metodo_pago = forms.ChoiceField(
        label='Método de pago del depósito',
        choices=[('', '— Selecciona —')] + [
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia bancaria'),
            ('tarjeta', 'Tarjeta'),
            ('otro', 'Otro'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'input-campo'}),
    )
    notas = forms.CharField(
        label='Notas (opcional)',
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'input-campo', 'rows': 2}
        ),
    )
    comentario = forms.CharField(
        label='Comentario para el administrador',
        widget=forms.Textarea(
            attrs={'class': 'input-campo', 'rows': 2}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipo'].queryset = equipos_con_disponibles()

    def clean(self):
        """Valida fechas y disponibilidad."""
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        vencimiento = cleaned.get('fecha_vencimiento')
        equipo = cleaned.get('equipo')
        cantidad = cleaned.get('cantidad') or 1

        if inicio and vencimiento and vencimiento <= inicio:
            raise forms.ValidationError(
                'La fecha de vencimiento debe ser posterior '
                'a la fecha de inicio.'
            )
        if equipo and not equipo.tiene_disponibles(cantidad):
            raise forms.ValidationError(
                f'Solo hay {equipo.cantidad_disponible} unidad(es) '
                f'disponible(s) de "{equipo.nombre}".'
            )
        return cleaned


class FinalizarRentaForm(forms.Form):
    """Formulario de confirmación para finalizar una renta (admin)."""

    confirmacion = forms.BooleanField(
        required=True,
        label='Confirmo que el equipo fue devuelto.',
    )
    monto_recibido = forms.DecimalField(
        label='Monto recibido del cliente (MXN)',
        max_digits=10,
        decimal_places=2,
        min_value=0,
        required=False,
        widget=forms.NumberInput(
            attrs={'class': 'input-campo', 'step': '0.01',
                   'placeholder': '0.00', 'id': 'id_monto_recibido'}
        ),
        help_text='Cuánto pagó el cliente al momento de la devolución.',
    )
    metodo_pago_cierre = forms.ChoiceField(
        label='Método de pago al cierre',
        choices=[('', '— Selecciona —')] + [
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia bancaria'),
            ('tarjeta', 'Tarjeta'),
            ('otro', 'Otro'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'input-campo'}),
    )
    notas_devolucion = forms.CharField(
        label='Notas de devolución (opcional)',
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'input-campo', 'rows': 2}
        ),
    )
