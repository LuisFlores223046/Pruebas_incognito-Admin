"""Formularios para el módulo de inventario."""
from django import forms
from .models import Equipo


class EquipoForm(forms.ModelForm):
    """Formulario para crear/editar equipos."""

    class Meta:
        model = Equipo
        fields = [
            'nombre',
            'descripcion',
            'cantidad_total',
            'cantidad_en_mantenimiento',
        ]
        widgets = {
            'nombre': forms.TextInput(
                attrs={'class': 'input-campo'}
            ),
            'descripcion': forms.Textarea(
                attrs={'class': 'input-campo', 'rows': 3}
            ),
            'cantidad_total': forms.NumberInput(
                attrs={'class': 'input-campo', 'min': 1}
            ),
            'cantidad_en_mantenimiento': forms.NumberInput(
                attrs={'class': 'input-campo', 'min': 0}
            ),
        }
        labels = {
            'nombre': 'Nombre del equipo',
            'descripcion': 'Descripción',
            'cantidad_total': 'Cantidad total de unidades',
            'cantidad_en_mantenimiento': 'Unidades en mantenimiento',
        }
        help_texts = {
            'cantidad_en_mantenimiento': (
                'Unidades que están fuera de servicio temporalmente.'
            ),
        }

    def clean(self):
        """Valida que mantenimiento no supere el total."""
        cleaned = super().clean()
        total = cleaned.get('cantidad_total')
        mant = cleaned.get('cantidad_en_mantenimiento')
        if total is not None and mant is not None:
            if mant >= total:
                raise forms.ValidationError(
                    'Las unidades en mantenimiento no pueden ser '
                    'iguales o mayores a la cantidad total.'
                )
        return cleaned


class SolicitudEquipoForm(forms.Form):
    """
    Formulario para que un empleado solicite cambios en equipos.
    El administrador revisará y aprobará la solicitud.
    """

    TIPO_CHOICES = [
        ('alta_equipo', 'Alta de nuevo equipo'),
        ('edicion_equipo', 'Edición de equipo existente'),
        ('baja_equipo', 'Baja de equipo'),
    ]
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label='Tipo de solicitud',
        widget=forms.Select(attrs={'class': 'input-campo'}),
    )
    comentario = forms.CharField(
        label='Descripción / Motivo',
        widget=forms.Textarea(
            attrs={'class': 'input-campo', 'rows': 4}
        ),
    )
    # Campos para alta de equipo
    nombre_equipo = forms.CharField(
        label='Nombre del equipo',
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-campo'}),
    )
    descripcion_equipo = forms.CharField(
        label='Descripción del equipo',
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'input-campo', 'rows': 2}
        ),
    )
    cantidad_total = forms.IntegerField(
        label='Cantidad total',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'input-campo'}),
    )
