# apps/usuarios/menu.py
from apps.common.components.menu import MenuItem, MenuSection, registry


registry.register_section(MenuSection(id='administracion', label='Administración', order=90))

registry.register_item(MenuItem(
    id='usuarios',
    label='Usuarios',
    section='administracion',
    url_name='usuarios:list',
    icon='settings',
    permissions=('usuarios.view_usuario',),
    order=10,
))
