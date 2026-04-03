"""Modelos para el módulo de reportes."""
from django.db import models


class ReporteGenerado(models.Model):
    """
    Registro de un reporte PDF generado por el administrador.
    No almacena el archivo, solo los metadatos para regenerarlo.
    """

    TIPO_CHOICES = [
        ('inventario', 'Inventario'),
        ('rentas', 'Rentas por periodo'),
    ]
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='tipo de reporte',
    )
    generado_por = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='generado por',
    )
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de generación',
    )
    periodo_inicio = models.DateField(
        null=True,
        blank=True,
        verbose_name='periodo inicio',
    )
    periodo_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name='periodo fin',
    )
    archivo_nombre = models.CharField(
        max_length=200,
        verbose_name='nombre de archivo',
    )

    class Meta:
        verbose_name = 'reporte generado'
        verbose_name_plural = 'reportes generados'
        ordering = ['-fecha_generacion']

    def __str__(self):
        """Representación en texto del reporte."""
        return (
            f"{self.get_tipo_display()} — "
            f"{self.fecha_generacion.strftime('%Y-%m-%d %H:%M')}"
        )
