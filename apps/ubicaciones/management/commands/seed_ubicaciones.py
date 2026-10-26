# ubigeo/management/commands/seed_ubigeo.py
from django.core.management.base import BaseCommand
from apps.ubicaciones.seeders import seed_ubicaciones

class Command(BaseCommand):
    help = "Carga inicial de datos de ubigeo (países, departamentos, provincias, distritos)."

    def handle(self, *args, **options):
        result = seed_ubicaciones()
        self.stdout.write(self.style.SUCCESS(f"OK: {result}"))