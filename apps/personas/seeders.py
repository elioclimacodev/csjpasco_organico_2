from django.apps import apps

from apps.common.seeders.base import seed_model, run_seeders

from .data import PERSONAS_DATA


Persona = apps.get_model('personas', 'Persona')

def insert_personas():
    return seed_model(Persona, PERSONAS_DATA, natural_key='id')

def seed_personas():
    return run_seeders(
        'personas',
        insert_personas,
    )