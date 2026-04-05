"""Migration: no-op — fix only needed for DBs that ran the original 0003."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rentas', '0003_add_deposito_devuelto'),
    ]

    operations = []
