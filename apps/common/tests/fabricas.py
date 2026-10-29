"""
Fábricas de registros mínimos válidos para las pruebas de acceso (feature 002).

Cada función crea el registro con sus campos obligatorios y un nombre único;
los campos adicionales pueden sobrescribirse con `**campos`.
"""
import datetime
from itertools import count

from django.apps import apps


_secuencia = count(1)


def _modelo(app_label, nombre):
    return apps.get_model(app_label, nombre)


def crear_pais(**campos):
    campos.setdefault('nombre', f'País de prueba {next(_secuencia)}')
    return _modelo('ubicaciones', 'Pais').objects.create(**campos)


def crear_departamento(pais=None, **campos):
    campos.setdefault('nombre', f'Departamento de prueba {next(_secuencia)}')
    return _modelo('ubicaciones', 'Departamento').objects.create(pais=pais or crear_pais(), **campos)


def crear_provincia(departamento=None, **campos):
    campos.setdefault('nombre', f'Provincia de prueba {next(_secuencia)}')
    return _modelo('ubicaciones', 'Provincia').objects.create(
        departamento=departamento or crear_departamento(), **campos
    )


def crear_distrito(provincia=None, **campos):
    campos.setdefault('nombre', f'Distrito de prueba {next(_secuencia)}')
    return _modelo('ubicaciones', 'Distrito').objects.create(provincia=provincia or crear_provincia(), **campos)


def crear_distrito_judicial(**campos):
    campos.setdefault('nombre', f'Distrito judicial de prueba {next(_secuencia)}')
    return _modelo('organizacion', 'DistritoJudicial').objects.create(**campos)


def crear_sede_judicial(distrito_judicial=None, **campos):
    campos.setdefault('nombre', f'Sede de prueba {next(_secuencia)}')
    return _modelo('organizacion', 'SedeJudicial').objects.create(
        distrito_judicial=distrito_judicial or crear_distrito_judicial(), **campos
    )


def crear_materia_jurisdiccional(**campos):
    campos.setdefault('nombre', f'Materia de prueba {next(_secuencia)}')
    return _modelo('organizacion', 'MateriaJurisdiccional').objects.create(**campos)


def crear_organo_jurisdiccional(**campos):
    campos.setdefault('nombre', f'Órgano de prueba {next(_secuencia)}')
    return _modelo('organizacion', 'OrganoJurisdiccional').objects.create(**campos)


def crear_persona(**campos):
    n = next(_secuencia)
    campos.setdefault('numero_documento', f'{70000000 + n}')
    campos.setdefault('nombres', 'Nombre')
    campos.setdefault('apellido_paterno', 'Paterno')
    campos.setdefault('apellido_materno', 'Materno')
    campos.setdefault('fecha_nacimiento', datetime.date(1990, 1, 1))
    campos.setdefault('email', f'persona{n}@prueba.pe')
    return _modelo('personas', 'Persona').objects.create(**campos)
