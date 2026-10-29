# apps/organizacion/menu.py
from apps.common.components.menu import MenuItem, MenuSection, registry


registry.register_section(MenuSection(id='organizacion', label='Organización', order=10))

# Los permisos de cada opción DEBEN coincidir con los que exige su vista
# (spec FR-005).
registry.register_item(MenuItem(
    id='distritos_judiciales',
    label='Distritos judiciales',
    section='organizacion',
    url_name='organizacion:distritos_judiciales_list',
    icon='map-pin',
    permissions=('organizacion.view_distritojudicial',),
    active_patterns=('organizacion:distritos_judiciales_*', 'organizacion:distrito_judicial_*'),
    order=10,
))

registry.register_item(MenuItem(
    id='materias_jurisdiccionales',
    label='Materias jurisdiccionales',
    section='organizacion',
    url_name='organizacion:materias_jurisdiccionales_list',
    icon='scale',
    permissions=('organizacion.view_materiajurisdiccional',),
    active_patterns=('organizacion:materias_jurisdiccionales_*', 'organizacion:materia_jurisdiccional_*'),
    order=20,
))

registry.register_item(MenuItem(
    id='organos_jurisdiccionales',
    label='Órganos jurisdiccionales',
    section='organizacion',
    url_name='organizacion:organos_jurisdiccionales_list',
    icon='building-bank',
    permissions=('organizacion.view_organojurisdiccional',),
    active_patterns=('organizacion:organos_jurisdiccionales_*', 'organizacion:organo_jurisdiccional_*'),
    order=30,
))
