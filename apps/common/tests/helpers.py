from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission


_contador = 0


def crear_usuario(permisos=(), grupos=(), **campos):
    """
    Crea un usuario activo para pruebas.

    `CustomUserManager.create_user` crea los usuarios inactivos por defecto,
    y Django no concede permisos a usuarios inactivos; por eso aquí se
    fuerza `is_active=True`.

    :param permisos: Permisos con formato 'app_label.codename'.
    :param grupos: Nombres de grupos a los que se agrega el usuario (se
        crean si no existen).
    :param campos: Campos adicionales del usuario (p. ej., first_name).
    """
    global _contador
    _contador += 1

    campos.setdefault('numero_documento', f'{40000000 + _contador}')
    campos.setdefault('email', f'usuario{_contador}@prueba.pe')
    campos.setdefault('is_active', True)

    usuario = get_user_model().objects.create_user(
        tipo_documento='DNI',
        password='clave-de-prueba',
        **campos,
    )

    for permiso in permisos:
        app_label, codename = permiso.split('.')
        usuario.user_permissions.add(
            Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename,
            )
        )

    for nombre in grupos:
        grupo, _ = Group.objects.get_or_create(name=nombre)
        usuario.groups.add(grupo)

    return usuario
