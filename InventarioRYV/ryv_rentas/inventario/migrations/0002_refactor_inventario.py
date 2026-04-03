"""
Migration: refactor inventario
- Remove Categoria model
- Remove categoria FK from Equipo
- Remove estado field from Equipo
- Remove cantidad_disponible field (now a property)
- Add cantidad_en_renta to Equipo
- Add cantidad_en_mantenimiento to Equipo
"""
from django.db import migrations, models


def migrate_data_forward(apps, schema_editor):
    """
    Inicializa cantidad_en_renta basándose en la diferencia entre
    cantidad_total y cantidad_disponible (datos existentes).
    """
    Equipo = apps.get_model('inventario', 'Equipo')
    for equipo in Equipo.objects.all():
        disponible = getattr(equipo, 'cantidad_disponible', equipo.cantidad_total)
        en_renta = max(0, equipo.cantidad_total - disponible)
        equipo.cantidad_en_renta = en_renta
        equipo.cantidad_en_mantenimiento = 0
        equipo.save()


def migrate_data_backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0001_initial'),
    ]

    operations = [
        # 1. Agregar nuevos campos
        migrations.AddField(
            model_name='equipo',
            name='cantidad_en_renta',
            field=models.PositiveIntegerField(default=0, verbose_name='en renta'),
        ),
        migrations.AddField(
            model_name='equipo',
            name='cantidad_en_mantenimiento',
            field=models.PositiveIntegerField(default=0, verbose_name='en mantenimiento'),
        ),
        # 2. Migración de datos
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
        # 3. Eliminar campos obsoletos
        migrations.RemoveField(
            model_name='equipo',
            name='cantidad_disponible',
        ),
        migrations.RemoveField(
            model_name='equipo',
            name='estado',
        ),
        migrations.RemoveField(
            model_name='equipo',
            name='categoria',
        ),
        # 4. Eliminar modelo Categoria
        migrations.DeleteModel(
            name='Categoria',
        ),
    ]
