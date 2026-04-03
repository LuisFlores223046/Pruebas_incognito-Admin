"""Migration: add metodo_pago, metodo_pago_cierre, cambio_entregado to Renta."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentas', '0004_fix_deposito_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='renta',
            name='metodo_pago',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('efectivo', 'Efectivo'),
                    ('transferencia', 'Transferencia bancaria'),
                    ('tarjeta', 'Tarjeta'),
                    ('otro', 'Otro'),
                ],
                blank=True,
                default='',
                verbose_name='método de pago (depósito)',
            ),
        ),
        migrations.AddField(
            model_name='renta',
            name='metodo_pago_cierre',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('efectivo', 'Efectivo'),
                    ('transferencia', 'Transferencia bancaria'),
                    ('tarjeta', 'Tarjeta'),
                    ('otro', 'Otro'),
                ],
                blank=True,
                default='',
                verbose_name='método de pago (cierre)',
            ),
        ),
        migrations.AddField(
            model_name='renta',
            name='cambio_entregado',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='cambio entregado (MXN)',
            ),
        ),
    ]
