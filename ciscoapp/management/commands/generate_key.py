from django.core.management.base import BaseCommand
from ciscoapp.models import ActivationKey

class Command(BaseCommand):
    help = 'Generate a new activation key'

    def handle(self, *args, **options):
        key = ActivationKey.objects.create()
        self.stdout.write(
            self.style.SUCCESS(f'Activation key generated: {key.key}')
        ) 