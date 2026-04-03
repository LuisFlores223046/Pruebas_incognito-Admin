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
            'imagen',
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
            'imagen': forms.ClearableFileInput(
                attrs={'class': 'input-campo input-campo--file'}
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
            'imagen': 'Imagen de referencia (opcional)',
            'cantidad_total': 'Cantidad total de unidades',
            'cantidad_en_mantenimiento': 'Unidades en mantenimiento',
        }
        help_texts = {
            'cantidad_en_mantenimiento': (
                'Unidades que están fuera de servicio temporalmente.'
            ),
            'imagen': (
                'Foto de referencia del equipo (jpg, png, etc.).'
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
    Se adapta dinámicamente según el tipo de solicitud.
    """

    TIPO_CHOICES = [
        ('alta_equipo', 'Alta de nuevo equipo'),
        ('edicion_equipo', 'Edición de equipo existente'),
        ('baja_equipo', 'Baja de equipo'),
    ]

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label='Tipo de solicitud',
        widget=forms.Select(attrs={'class': 'input-campo', 'id': 'id_tipo_solicitud'}),
    )

    # ── Equipo existente (para edición y baja) ──
    equipo_existente = forms.ModelChoiceField(
        queryset=Equipo.objects.none(),
        required=False,
        label='Equipo a modificar / dar de baja',
        empty_label='— Selecciona un equipo —',
        widget=forms.Select(attrs={'class': 'input-campo', 'id': 'id_equipo_existente'}),
    )

    # ── Campos para alta de equipo ──
    nombre_equipo = forms.CharField(
        label='Nombre del equipo',
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-campo', 'placeholder': 'Ej. Taladro percutor 18V'}),
    )
    descripcion_equipo = forms.CharField(
        label='Descripción',
        required=False,
        widget=forms.Textarea(attrs={'class': 'input-campo', 'rows': 3,
                                     'placeholder': 'Características, marca, modelo...'}),
    )
    cantidad_total = forms.IntegerField(
        label='Cantidad de unidades',
        required=False,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'input-campo', 'min': 1}),
    )

    # ── Comentario / motivo (siempre requerido) ──
    comentario = forms.CharField(
        label='Motivo / observaciones',
        widget=forms.Textarea(
            attrs={'class': 'input-campo', 'rows': 3,
                   'placeholder': 'Explica el motivo de la solicitud...'}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipo_existente'].queryset = Equipo.objects.filter(
            activo=True
        ).order_by('nombre')

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo')

        if tipo == 'alta_equipo':
            if not cleaned.get('nombre_equipo', '').strip():
                self.add_error(
                    'nombre_equipo',
                    'El nombre del equipo es obligatorio para una alta.',
                )
            if not cleaned.get('cantidad_total'):
                self.add_error(
                    'cantidad_total',
                    'La cantidad de unidades es obligatoria.',
                )

        elif tipo in ('edicion_equipo', 'baja_equipo'):
            if not cleaned.get('equipo_existente'):
                self.add_error(
                    'equipo_existente',
                    'Debes seleccionar un equipo.',
                )

        return cleaned
