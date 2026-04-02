"""Formularios para el módulo de inventario."""
from django import forms
from .models import Equipo, Categoria


class EquipoForm(forms.ModelForm):
    """Formulario para crear/editar equipos."""

    class Meta:
        model = Equipo
        fields = [
            'nombre',
            'categoria',
            'descripcion',
            'cantidad_total',
            'cantidad_disponible',
            'estado',
        ]
        widgets = {
            'nombre': forms.TextInput(
                attrs={'class': 'input-campo'}
            ),
            'categoria': forms.Select(
                attrs={'class': 'input-campo'}
            ),
            'descripcion': forms.Textarea(
                attrs={'class': 'input-campo', 'rows': 3}
            ),
            'cantidad_total': forms.NumberInput(
                attrs={'class': 'input-campo', 'min': 1}
            ),
            'cantidad_disponible': forms.NumberInput(
                attrs={'class': 'input-campo', 'min': 0}
            ),
            'estado': forms.Select(
                attrs={'class': 'input-campo'}
            ),
        }
        labels = {
            'nombre': 'Nombre del equipo',
            'categoria': 'Categoría',
            'descripcion': 'Descripción',
            'cantidad_total': 'Cantidad total',
            'cantidad_disponible': 'Cantidad disponible',
            'estado': 'Estado',
        }

    def clean(self):
        """Valida que cantidad_disponible no supere cantidad_total."""
        cleaned = super().clean()
        total = cleaned.get('cantidad_total')
        disponible = cleaned.get('cantidad_disponible')
        if total is not None and disponible is not None:
            if disponible > total:
                raise forms.ValidationError(
                    'La cantidad disponible no puede ser mayor '
                    'a la cantidad total.'
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
    categoria_nombre = forms.CharField(
        label='Categoría',
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
