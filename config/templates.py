import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DIRS = [
    # Directorio de plantillas a nivel de proyecto.
    BASE_DIR / 'templates',

    # locations.
    # BASE_DIR / 'apps' / 'locations' / 'countries' / 'templates',
    
    # users.
    BASE_DIR / 'apps' / 'users' / 'templates',
    BASE_DIR / 'apps' / 'users' / 'registration' / 'templates',
    BASE_DIR / 'apps' / 'users' / 'authentication' / 'templates',
    BASE_DIR / 'apps' / 'users' / 'password' / 'templates',
    
    # hr - Recursos Humanos.
    BASE_DIR / 'apps' / 'hr' / 'regimes' / 'templates',
    BASE_DIR / 'apps' / 'hr' / 'regimen' / 'templates',
    
    # it - Tecnologías de la Información.
    BASE_DIR / 'apps' / 'it' / 'equipos' / 'templates',
]
