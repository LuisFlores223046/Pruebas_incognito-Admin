"""Migration: add imagen field to Equipo."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0002_refactor_inventario'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipo',
            name='imagen',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='equipos/',
                verbose_name='imagen de referencia',
            ),
        ),
    ]
