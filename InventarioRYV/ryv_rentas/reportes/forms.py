"""Formularios para el módulo de reportes."""
from django import forms


class ReporteRentasForm(forms.Form):
    """Formulario para generar reporte de rentas por periodo (RN-012)."""

    periodo_inicio = forms.DateField(
        label='Fecha de inicio',
        widget=forms.DateInput(
            attrs={'class': 'input-campo', 'type': 'date'},
            format='%Y-%m-%d',
        ),
    )
    periodo_fin = forms.DateField(
        label='Fecha de fin',
        widget=forms.DateInput(
            attrs={'class': 'input-campo', 'type': 'date'},
            format='%Y-%m-%d',
        ),
    )

    def clean(self):
        """Valida que fecha inicio sea anterior o igual a fecha fin."""
        cleaned = super().clean()
        inicio = cleaned.get('periodo_inicio')
        fin = cleaned.get('periodo_fin')
        if inicio and fin and fin < inicio:
            raise forms.ValidationError(
                'La fecha de fin debe ser posterior a la fecha de inicio.'
            )
        return cleaned
