# apps/core/breadcrumbs.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class Breadcrumb:
    """
    Representa un único nivel dentro de una ruta de navegación (breadcrumb).

    Si `url` es None, el nivel se renderiza como texto plano (no clickeable),
    lo cual se usa típicamente para el nivel actual de la página.
    """
    label: str
    url: Optional[str] = None