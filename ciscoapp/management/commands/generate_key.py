from django.core.management.base import BaseCommand
from ciscoapp.models import ActivationKey

class Command(BaseCommand):
    help = 'Genera una nueva clave de activación'

    def handle(self, *args, **options):
        key = ActivationKey.objects.create()
        self.stdout.write(
            self.style.SUCCESS(f'Clave de activación generada: {key.key}')
        ) 