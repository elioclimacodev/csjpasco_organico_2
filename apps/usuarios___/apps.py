from django.core.management import load_command_class
from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
    verbose_name = 'Usuarios'

    def ready(self):
        from apps.usuarios.management.commands import crearsuperusuario
        # Fuerza la carga del comando personalizado 'createsuperuser'
        # sobrescribiendo el comando nativo de Django.
        load_command_class('apps.usuarios', 'crearsuperusuario')