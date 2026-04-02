"""Formularios para el módulo de rentas."""
from django import forms
from .models import Renta, Cliente
from inventario.models import Equipo


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
            'fecha_inicio',
            'fecha_vencimiento',
            'precio',
            'deposito',
            'notas',
        ]
        widgets = {
            'equipo': forms.Select(
                attrs={'class': 'input-campo'}
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
            'notas': forms.Textarea(
                attrs={'class': 'input-campo', 'rows': 2}
            ),
        }
        labels = {
            'equipo': 'Equipo',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_vencimiento': 'Fecha de vencimiento',
            'precio': 'Precio (MXN)',
            'deposito': 'Depósito (MXN)',
            'notas': 'Notas (opcional)',
        }

    def __init__(self, *args, **kwargs):
        """Filtra equipos disponibles solamente."""
        super().__init__(*args, **kwargs)
        self.fields['equipo'].queryset = Equipo.objects.filter(
            activo=True,
            estado='disponible',
        )

    def clean(self):
        """Valida fechas y RN-001 (una sola renta activa por equipo)."""
        cleaned = super().clean()
        fecha_inicio = cleaned.get('fecha_inicio')
        fecha_vencimiento = cleaned.get('fecha_vencimiento')
        equipo = cleaned.get('equipo')

        if fecha_inicio and fecha_vencimiento:
            if fecha_vencimiento <= fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de vencimiento debe ser posterior '
                    'a la fecha de inicio.'
                )

        # RN-001: Un equipo solo puede tener una renta activa
        if equipo and equipo.tiene_renta_activa():
            raise forms.ValidationError(
                f'El equipo "{equipo.nombre}" ya tiene una '
                'renta activa.'
            )

        return cleaned


class SolicitudRentaForm(forms.Form):
    """
    Formulario para que un empleado solicite una nueva renta (RN-008).
    El administrador la aprobará desde el panel.
    """

    equipo = forms.ModelChoiceField(
        queryset=Equipo.objects.filter(
            activo=True, estado='disponible'
        ),
        label='Equipo',
        widget=forms.Select(attrs={'class': 'input-campo'}),
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
        label='Precio (MXN)',
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
        """Valida que la fecha de vencimiento sea posterior al inicio."""
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        vencimiento = cleaned.get('fecha_vencimiento')
        if inicio and vencimiento and vencimiento <= inicio:
            raise forms.ValidationError(
                'La fecha de vencimiento debe ser posterior '
                'a la fecha de inicio.'
            )
        return cleaned


class FinalizarRentaForm(forms.Form):
    """Formulario de confirmación para finalizar una renta (admin)."""

    confirmacion = forms.BooleanField(
        required=True,
        label='Confirmo que el equipo fue devuelto.',
    )
    notas_devolucion = forms.CharField(
        label='Notas de devolución (opcional)',
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'input-campo', 'rows': 2}
        ),
    )
