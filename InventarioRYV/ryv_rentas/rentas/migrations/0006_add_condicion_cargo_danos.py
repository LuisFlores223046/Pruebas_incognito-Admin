"""Migration: add condicion_devolucion and cargo_daños to Renta."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentas', '0005_add_pago_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='renta',
            name='condicion_devolucion',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('bueno', 'Bueno — sin daños'),
                    ('daños_menores', 'Daños menores'),
                    ('inservible', 'Inservible / Pérdida total'),
                ],
                blank=True,
                default='',
                verbose_name='condición al devolver',
            ),
        ),
        migrations.AddField(
            model_name='renta',
            name='cargo_daños',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='cargo por daños (MXN)',
            ),
        ),
    ]
