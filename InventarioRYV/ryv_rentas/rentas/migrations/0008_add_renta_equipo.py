"""Migration: create RentaEquipo model for multi-equipment rentals."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0001_initial'),
        ('rentas', '0007_alter_renta_condicion_devolucion'),
    ]

    operations = [
        migrations.CreateModel(
            name='RentaEquipo',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID',
                )),
                ('cantidad', models.PositiveIntegerField(
                    default=1, verbose_name='cantidad',
                )),
                ('equipo', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='renta_items',
                    to='inventario.equipo',
                    verbose_name='equipo',
                )),
                ('renta', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='rentas.renta',
                    verbose_name='renta',
                )),
            ],
            options={
                'verbose_name': 'equipo de renta',
                'verbose_name_plural': 'equipos de renta',
            },
        ),
    ]
