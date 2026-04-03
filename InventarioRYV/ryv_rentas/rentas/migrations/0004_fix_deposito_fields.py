"""Migration: replace deposito_devuelto with monto_recibido on Renta.

Uses RunSQL because 0003 was edited after it ran, leaving the DB state
out of sync with Django's migration state.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rentas', '0003_add_deposito_devuelto'),
    ]

    operations = [
        # Eliminar la columna que quedó en la BD (no está en el estado de Django)
        migrations.RunSQL(
            sql='ALTER TABLE rentas_renta DROP COLUMN deposito_devuelto;',
            reverse_sql='ALTER TABLE rentas_renta ADD COLUMN deposito_devuelto BOOLEAN NOT NULL DEFAULT 0;',
        ),
        # Agregar la columna que Django ya espera (el estado ya la conoce por 0003 editado)
        migrations.RunSQL(
            sql='ALTER TABLE rentas_renta ADD COLUMN monto_recibido DECIMAL(10,2) NULL;',
            reverse_sql='ALTER TABLE rentas_renta DROP COLUMN monto_recibido;',
        ),
    ]
