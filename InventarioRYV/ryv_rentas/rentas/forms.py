"""Formularios para el módulo de rentas."""
from decimal import Decimal
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
    Los equipos se añaden como filas dinámicas en la vista/template.
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
            'fecha_inicio',
            'fecha_vencimiento',
            'precio',
            'deposito',
            'metodo_pago',
            'notas',
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(
                attrs={'class': 'input-campo', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'fecha_vencimiento': forms.DateInput(
                attrs={'class': 'input-campo', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'precio': forms.NumberInput(
                attrs={'class': 'input-campo', 'step': '0.01',
                       'id': 'id_precio_renta'}
            ),
            'deposito': forms.NumberInput(
                attrs={'class': 'input-campo', 'step': '0.01',
                       'id': 'id_deposito_renta'}
            ),
            'metodo_pago': forms.Select(
                attrs={'class': 'input-campo'}
            ),
            'notas': forms.Textarea(
                attrs={'class': 'input-campo', 'rows': 2}
            ),
        }
        labels = {
            'fecha_inicio': 'Fecha de inicio',
            'fecha_vencimiento': 'Fecha de vencimiento',
            'precio': 'Precio total (MXN)',
            'deposito': 'Depósito (MXN)',
            'metodo_pago': 'Método de pago del depósito',
            'notas': 'Notas (opcional)',
        }

    def clean(self):
        """Valida fechas y depósito mínimo."""
        cleaned = super().clean()
        fecha_inicio = cleaned.get('fecha_inicio')
        fecha_vencimiento = cleaned.get('fecha_vencimiento')
        precio = cleaned.get('precio')
        deposito = cleaned.get('deposito') or Decimal('0')

        if fecha_inicio and fecha_vencimiento:
            if fecha_vencimiento <= fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de vencimiento debe ser posterior '
                    'a la fecha de inicio.'
                )

        if precio and precio > 0:
            minimo = (precio * Decimal('0.5')).quantize(Decimal('0.01'))
            if deposito < minimo:
                self.add_error(
                    'deposito',
                    f'El depósito mínimo es el 50% del precio '
                    f'(${minimo}). Ingresa al menos ${minimo}.',
                )

        if deposito and deposito > 0:
            if not cleaned.get('metodo_pago'):
                self.add_error(
                    'metodo_pago',
                    'Selecciona el método de pago del depósito.',
                )

        return cleaned


class SolicitudRentaForm(forms.Form):
    """
    Formulario para que un empleado solicite una nueva renta (RN-008).
    Los equipos se añaden como filas dinámicas; el resto son campos estándar.
    """

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
            attrs={'class': 'input-campo', 'step': '0.01',
                   'id': 'id_precio_solic'}
        ),
    )
    deposito = forms.DecimalField(
        label='Depósito (MXN)',
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={'class': 'input-campo', 'step': '0.01',
                   'id': 'id_deposito_solic'}
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

    def clean(self):
        """Valida fechas y depósito mínimo."""
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        vencimiento = cleaned.get('fecha_vencimiento')
        precio = cleaned.get('precio')
        deposito = cleaned.get('deposito') or Decimal('0')

        if inicio and vencimiento and vencimiento <= inicio:
            raise forms.ValidationError(
                'La fecha de vencimiento debe ser posterior '
                'a la fecha de inicio.'
            )

        if precio and precio > 0:
            minimo = (precio * Decimal('0.5')).quantize(Decimal('0.01'))
            if deposito < minimo:
                self.add_error(
                    'deposito',
                    f'El depósito mínimo es el 50% del precio '
                    f'(${minimo}). Ingresa al menos ${minimo}.',
                )

        if deposito and deposito > 0:
            if not cleaned.get('metodo_pago'):
                self.add_error(
                    'metodo_pago',
                    'Selecciona el método de pago del depósito.',
                )

        return cleaned


class FinalizarRentaForm(forms.Form):
    """Formulario de confirmación para finalizar una renta (admin)."""

    condicion_devolucion = forms.ChoiceField(
        label='Condición del equipo al devolver',
        choices=[
            ('bueno', 'Bueno — sin daños'),
            ('daños_menores', 'Daños menores'),
            ('inservible', 'Inservible / Pérdida total'),
            ('extraviado', 'Extraviado'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'radio-condicion'}),
    )
    cargo_daños = forms.DecimalField(
        label='Cargo por daños (MXN)',
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        required=False,
        widget=forms.NumberInput(
            attrs={'class': 'input-campo', 'step': '0.01',
                   'placeholder': '0.00'}
        ),
        help_text='Monto adicional a cobrar por daños al equipo.',
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

    def clean(self):
        cleaned = super().clean()
        condicion = cleaned.get('condicion_devolucion')
        cargo = cleaned.get('cargo_daños')

        if condicion and condicion != 'bueno':
            if not cargo:
                self.add_error(
                    'cargo_daños',
                    'Debes indicar el cargo por daños '
                    '(obligatorio para esta condición).',
                )
        return cleaned
