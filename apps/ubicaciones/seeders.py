from django.apps import apps

from apps.common.seeders.base import seed_model, run_seeders

from .data import PAISES_DATA, DEPARTAMENTOS_DATA, PROVINCIAS_DATA, DISTRITOS_DATA

Pais         = apps.get_model("ubicaciones", "Pais")
Departamento = apps.get_model("ubicaciones", "Departamento")
Provincia    = apps.get_model("ubicaciones", "Provincia")
Distrito     = apps.get_model("ubicaciones", "Distrito")


def seed_paises():
    return seed_model(Pais, PAISES_DATA, natural_key="id")

def seed_departamentos():
    return seed_model(Departamento, DEPARTAMENTOS_DATA, natural_key="id")

def seed_provincias():
    return seed_model(Provincia, PROVINCIAS_DATA, natural_key="id")

def seed_distritos():
    return seed_model(Distrito, DISTRITOS_DATA, natural_key="id")

def seed_ubicaciones():
    return run_seeders(
        "ubigeo",
        seed_paises,
        seed_departamentos,
        seed_provincias,
        seed_distritos,
    )