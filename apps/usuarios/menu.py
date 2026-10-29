# apps/usuarios/menu.py
from apps.common.components.menu import MenuItem, MenuSection, UserMenuItem, registry


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

registry.register_user_item(UserMenuItem(
    id='cerrar_sesion',
    label='Cerrar sesión',
    kind='post',
    url_name='usuarios:cerrar_sesion',
    icon='logout',
    visible_to_authenticated=True,
    order=1000,
))
