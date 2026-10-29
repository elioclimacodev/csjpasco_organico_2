# apps/common/checks.py
from django.core.checks import Error, Tags, register
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import NoReverseMatch, reverse

from apps.common.components.menu import BADGE_VARIANTS, USER_ITEM_KINDS, registry


# Profundidad máxima del menú: primer nivel, desplegable y dropend.
PROFUNDIDAD_MAXIMA = 3


def _error_ruta(url_name, obj_id):
    """Devuelve un error E102 si `url_name` no se resuelve sin argumentos."""
    try:
        reverse(url_name)
    except NoReverseMatch:
        return Error(
            f'Menú: la ruta "{url_name}" de "{obj_id}" no se puede resolver sin argumentos.',
            hint='Use una ruta existente que no requiera argumentos.',
            id='common.E102',
        )
    return None


def _error_icono(icon, obj_id):
    """Devuelve un error E108 si no existe el parcial del ícono."""
    try:
        get_template(f'components/icons/{icon}.html')
    except TemplateDoesNotExist:
        return Error(
            f'Menú: no existe el ícono "{icon}" de "{obj_id}".',
            hint=f'Cree templates/components/icons/{icon}.html.',
            id='common.E108',
        )
    return None


def _validar_item(item, nivel, secciones, ids_vistos, errores):
    """Valida un ítem y, recursivamente, sus hijos."""
    if item.id in ids_vistos:
        errores.append(Error(f'Menú: el id "{item.id}" está duplicado.', id='common.E101'))
    ids_vistos.add(item.id)

    if nivel > PROFUNDIDAD_MAXIMA:
        errores.append(Error(
            f'Menú: "{item.id}" supera la profundidad máxima de {PROFUNDIDAD_MAXIMA} niveles.',
            id='common.E107',
        ))

    # La sección solo se declara en primer nivel y debe estar registrada.
    if nivel == 1 and item.section is not None and item.section not in secciones:
        errores.append(Error(f'Menú: la sección "{item.section}" de "{item.id}" no está registrada.', id='common.E106'))
    if nivel > 1 and item.section is not None:
        errores.append(Error(f'Menú: "{item.id}" es un hijo y no debe declarar sección.', id='common.E106'))

    if item.children:
        if item.url_name or item.url or item.permissions:
            errores.append(Error(
                f'Menú: el contenedor "{item.id}" no debe declarar destino ni permisos propios.',
                id='common.E104',
            ))
        if item.columns < 1:
            errores.append(Error(f'Menú: "{item.id}" declara menos de una columna.', id='common.E110'))
    else:
        if bool(item.url_name) == bool(item.url):
            errores.append(Error(
                f'Menú: la hoja "{item.id}" debe declarar exactamente un destino (url_name o url).',
                id='common.E103',
            ))
        if item.columns != 1:
            errores.append(Error(f'Menú: la hoja "{item.id}" no puede declarar columnas.', id='common.E110'))
        if not item.permissions and not item.visible_to_authenticated:
            errores.append(Error(
                f'Menú: la hoja "{item.id}" no declara permisos ni es visible para todo autenticado; '
                'nunca se mostraría.',
                id='common.E105',
            ))
        if item.url_name and (error := _error_ruta(item.url_name, item.id)):
            errores.append(error)
        if item.url and not item.url.startswith('https://'):
            errores.append(Error(f'Menú: la URL externa de "{item.id}" debe usar https://.', id='common.E111'))

    if item.icon and (error := _error_icono(item.icon, item.id)):
        errores.append(error)

    if item.badge and not item.badge.text.strip():
        errores.append(Error(
            f'Menú: la insignia de "{item.id}" no tiene texto; el color no puede ser el único significado.',
            id='common.E112',
        ))

    if item.badge and item.badge.variant not in BADGE_VARIANTS:
        errores.append(Error(
            f'Menú: la variante de insignia "{item.badge.variant}" de "{item.id}" no está permitida.',
            hint=f'Use una de: {", ".join(BADGE_VARIANTS)}.',
            id='common.E109',
        ))

    for hijo in item.children:
        _validar_item(hijo, nivel + 1, secciones, ids_vistos, errores)


@register(Tags.urls)
def check_menu(app_configs, **kwargs):
    """
    Valida las declaraciones del menú registradas por las apps
    (contracts/menu-declaration.md §Reglas verificadas por el system check).
    """
    errores = []
    secciones = {seccion.id for seccion in registry.sections()}

    ids_vistos = set()
    for item in registry.items():
        _validar_item(item, 1, secciones, ids_vistos, errores)

    for opcion in registry.user_items():
        if opcion.kind not in USER_ITEM_KINDS:
            errores.append(Error(
                f'Menú: el tipo "{opcion.kind}" de la opción de usuario "{opcion.id}" no está permitido.',
                hint=f'Use uno de: {", ".join(USER_ITEM_KINDS)}.',
                id='common.E113',
            ))
        if error := _error_ruta(opcion.url_name, opcion.id):
            errores.append(error)
        if opcion.icon and (error := _error_icono(opcion.icon, opcion.id)):
            errores.append(error)
        if not opcion.permissions and not opcion.visible_to_authenticated:
            errores.append(Error(
                f'Menú: la opción de usuario "{opcion.id}" no declara permisos ni es visible para todo '
                'autenticado; nunca se mostraría.',
                id='common.E105',
            ))

    return errores
