"""Comando para crear el usuario administrador inicial."""
from django.core.management.base import BaseCommand
from authentication.models import Usuario


class Command(BaseCommand):
    """Crea el usuario administrador inicial si no existe ninguno."""

    help = 'Crea el usuario administrador inicial si no existe ninguno'

    def handle(self, *args, **kwargs):
        """Ejecuta el comando de creación del admin inicial."""
        if not Usuario.objects.filter(rol='administrador').exists():
            Usuario.objects.create_superuser(
                username='admin',
                password='Admin1234!',
                email='admin@ryvrentas.com',
                rol='administrador',
            )
            self.stdout.write(
                self.style.SUCCESS(
                    'Admin inicial creado: admin / Admin1234!'
                )
            )
        else:
            self.stdout.write(
                'Ya existe un administrador. No se creó nada.'
            )
