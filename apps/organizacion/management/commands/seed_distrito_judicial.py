import logging

from django.core.management import BaseCommand
from django.db import transaction


# Registro del log producido por este comando.
logger = logging.getLogger(__name__)

JUDICIAL_DISTRICTS_DATA = [
    {"nombre": "AMAZONAS",                                                          "siglas": 'CSJAM',     "latitud": -6.23065,    "longitud": -77.86939,      "activo": True},
    {"nombre": "ANCASH",                                                            "siglas": 'CSJA',     "latitud": -9.53069,    "longitud": -77.52871,      "activo": True},
    {"nombre": "APURIMAC",                                                          "siglas": 'CSJAP',     "latitud": -13.63439,   "longitud": -72.88359,      "activo": True},
    {"nombre": "AREQUIPA",                                                          "siglas": 'CSJAR',     "latitud": -16.39878,   "longitud": -71.53018,      "activo": True},
    {"nombre": "AYACUCHO",                                                          "siglas": 'CSJAY',     "latitud": -13.15990,   "longitud": -74.22665,      "activo": True},
    {"nombre": "CAJAMARCA",                                                         "siglas": 'CSJCA',     "latitud": -7.157385,   "longitud": -78.518151,     "activo": True},
    {"nombre": "CALLAO",                                                            "siglas": 'CSJCL',     "latitud": -12.05682,   "longitud": -77.14274,      "activo": True},
    {"nombre": "CAÑETE",                                                            "siglas": 'CSJC',     "latitud": -13.075613,  "longitud": -76.380117,     "activo": True},
    {"nombre": "LIMA NORTE",                                                        "siglas": 'CSJLN',     "latitud": -11.989268,  "longitud": -77.059805,     "activo": True},
    {"nombre": "CUSCO",                                                             "siglas": 'CSJC---',     "latitud": -13.519121,  "longitud": -71.977614,     "activo": True},
    {"nombre": "HUANCAVELICA",                                                      "siglas": 'CSJH',     "latitud": -12.788521,  "longitud": -74.973677,     "activo": True},
    {"nombre": "HUANUCO",                                                           "siglas": 'CSJH---',     "latitud": -9.928915,   "longitud": -76.240019,     "activo": True},
    {"nombre": "HUAURA",                                                            "siglas": 'CSJH----',     "latitud": -11.113439,  "longitud": -77.610304,     "activo": True},
    {"nombre": "ICA",                                                               "siglas": 'CSJI',     "latitud": -14.066904,  "longitud": -75.726435,     "activo": True},
    {"nombre": "JUNIN",                                                             "siglas": None,     "latitud": -12.059723,  "longitud": -75.214649,     "activo": True},
    {"nombre": "LA LIBERTAD",                                                       "siglas": None,     "latitud": -8.111309,   "longitud": -79.027301,     "activo": True},
    {"nombre": "LAMBAYEQUE",                                                        "siglas": None,     "latitud": -6.771365,   "longitud": -79.837967,     "activo": True},
    {"nombre": "LIMA",                                                              "siglas": None,     "latitud": -12.054089,  "longitud": -77.030472,     "activo": True},
    {"nombre": "LORETO",                                                            "siglas": None,     "latitud": -3.754010,   "longitud": -73.249660,     "activo": True},
    {"nombre": "PIURA",                                                             "siglas": None,     "latitud": -5.198128,   "longitud": -80.625603,     "activo": True},
    {"nombre": "PUNO",                                                              "siglas": None,     "latitud": -15.840943,  "longitud": -70.027944,     "activo": True},
    {"nombre": "SAN MARTIN",                                                        "siglas": None,     "latitud": -6.034848,   "longitud": -76.974203,     "activo": True},
    {"nombre": "TACNA",                                                             "siglas": None,     "latitud": -18.010575,  "longitud": -70.254109,     "activo": True},
    {"nombre": "UCAYALI",                                                           "siglas": None,     "latitud": -8.384436,   "longitud": -74.533211,     "activo": True},
    {"nombre": "DEL SANTA",                                                         "siglas": None,     "latitud": -9.08042,    "longitud": -78.57729,      "activo": True},
    {"nombre": "TUMBES",                                                            "siglas": None,     "latitud": -3.553765,   "longitud": -80.429017,     "activo": True},
    {"nombre": "MADRE DE DIOS",                                                     "siglas": None,     "latitud": -12.59622,   "longitud": -69.18394,      "activo": True},
    {"nombre": "MOQUEGUA",                                                          "siglas": None,     "latitud": -17.19457,   "longitud": -70.93405,      "activo": True},
    {"nombre": "PASCO",                                                             "siglas": "CSJPA",  "latitud": -10.692306,  "longitud": -76.259542,     "activo": True},
    {"nombre": "LIMA SUR",                                                          "siglas": None,     "latitud": -12.159356,  "longitud": -76.954637,     "activo": True},
    {"nombre": "SULLANA",                                                           "siglas": None,     "latitud": -4.910680,   "longitud": -80.695692,     "activo": True},
    {"nombre": "LIMA ESTE",                                                         "siglas": None,     "latitud": -12.055907,  "longitud": -76.952814,     "activo": True},
    {"nombre": "PUENTE PIEDRA - VENTANILLA",                                        "siglas": 'CSJPPV',     "latitud": -11.876191,  "longitud": -77.122897,     "activo": True},
    {"nombre": "SELVA CENTRAL",                                                     "siglas": None,     "latitud": -11.071643,  "longitud": -75.338033,     "activo": True},
    {"nombre": "CORTE SUPREMA",                                                     "siglas": None,     "latitud": None,        "longitud": None,           "activo": True},
]

@transaction.atomic
def seed_distrito_judicial():
    '''
    Rellena el modelo DistritoJudicial con datos reales de los Distritos Judiciales
    del páis. Se usa el campo 'nombre' para buscar y si existe, actualiza sus campos.
    '''
    from apps.organizacion.models import DistritoJudicial

    created = 0
    updated = 0

    for data in JUDICIAL_DISTRICTS_DATA:
        jd, created = DistritoJudicial.objects.get_or_create(
            nombre=data['nombre'],
            defaults={
                'siglas'    : data['siglas'],
                'latitud'   : data['latitud'],
                'longitud'  : data['longitud'],
                'activo'    : data['activo'],
            }
        )

        if created:
            created += 1
        else:
            # Actualiza los campos en caso hayan cambiado.
            updated_fields = []
            for field in ('siglas', 'latitud', 'longitud', 'activo'):
                if getattr(jd, field) != data[field]:
                    setattr(jd, field, data[field])
                    updated_fields.append(field)
                if updated_fields:
                    jd.save(updated_fields=updated_fields)
                    updated += 1

    logger.info(f'Distritos Judiciales creados {created}, actualizados {updated}.')


class Command(BaseCommand):
    help = 'Llena el modelo "DistritoJudicial" con datos de los Distritos Judiciales del Perú (INEI).'
    
    def handle(self, *args, **options):
        try:
            seed_distrito_judicial()
            self.stdout.write(self.style.SUCCESS('Se ha completado el llenado del modelo DistritoJudicial.'))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'Error: {exc}'))
            raise