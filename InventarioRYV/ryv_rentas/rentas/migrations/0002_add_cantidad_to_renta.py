"""Migration: add cantidad field to Renta."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='renta',
            name='cantidad',
            field=models.PositiveIntegerField(default=1, verbose_name='cantidad'),
        ),
    ]
