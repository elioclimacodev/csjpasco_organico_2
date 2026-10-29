from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common'

    def ready(self):
        # Registra el system check del menú.
        from apps.common import checks  # noqa: F401

        # Importa el módulo `menu` de cada app instalada para que registre
        # sus secciones e ítems. common no importa ningún módulo de negocio
        # por nombre (Principio IV).
        autodiscover_modules('menu')
