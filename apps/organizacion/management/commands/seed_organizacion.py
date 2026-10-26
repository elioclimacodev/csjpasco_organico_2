from django.core.management.base import BaseCommand
from apps.common.seeders import seed_generic_models
# Importa tus datos (ajusta la ruta según donde los hayas guardado)
from apps.organizacion.data import (
    DISTRITOS_JUDICIALES_DATA, 
    # SEDES_JUDICIALES_DATA, 
    # INSTANCIA_JUDICIAL_DATA
)
# Importa tus modelos
from apps.organizacion.models import DistritoJudicial#, SedeJudicial, InstanciaJudicial

class Command(BaseCommand):
    help = 'Alimenta la base de datos de la institución de forma masiva y genérica'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando proceso de seed...'))

        # EL ORDEN ES VITAL: Los padres siempre deben ir antes que los hijos
        config = [
            {
                "model": DistritoJudicial,
                "data": DISTRITOS_JUDICIALES_DATA,
                # No tiene fk_mappings porque es el nivel raíz
                "fk_mappings": {} 
            },
            # {
            #     "model": SedeJudicial,
            #     "data": SEDES_JUDICIALES_DATA,
            #     # Le decimos a la función: "El campo 'distrito_judicial' apunta al modelo DistritoJudicial"
            #     "fk_mappings": {
            #         "distrito_judicial": DistritoJudicial
            #     }
            # },
            # {
            #     "model": InstanciaJudicial,
            #     "data": INSTANCIA_JUDICIAL_DATA,
            #     "fk_mappings": {
            #         "sede_judicial": SedeJudicial
            #     }
            # }
        ]

        # Ejecutar la función genérica
        seed_generic_models(config)

        self.stdout.write(self.style.SUCCESS('¡Proceso de seed finalizado con éxito!'))