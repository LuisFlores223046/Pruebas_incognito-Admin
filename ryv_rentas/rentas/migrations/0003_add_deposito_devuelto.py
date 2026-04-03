"""Migration: add monto_recibido field to Renta."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentas', '0002_add_cantidad_to_renta'),
    ]

    operations = [
        migrations.AddField(
            model_name='renta',
            name='monto_recibido',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='monto recibido al cierre (MXN)',
                help_text='Cantidad que pagó el cliente al devolver el equipo.',
            ),
        ),
    ]
