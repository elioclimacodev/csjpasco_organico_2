# apps/personas/menu.py
from apps.common.components.menu import MenuItem, MenuSection, registry


registry.register_section(MenuSection(id='personas', label='Personas', order=20))

registry.register_item(MenuItem(
    id='personas',
    label='Personas',
    section='personas',
    url_name='personas:list',
    icon='users',
    permissions=('personas.view_persona',),
    active_patterns=('personas:*',),
    order=10,
))
