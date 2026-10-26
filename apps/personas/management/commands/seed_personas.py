from django.core.management.base import BaseCommand

from apps.personas.seeders import seed_personas


class Command(BaseCommand):
    help = 'Carga inicial de datos de personas.'

    def handle(self, *args, **options):
        result = seed_personas()
        self.stdout.write(self.style.SUCCESS(f'OK: {result}'))