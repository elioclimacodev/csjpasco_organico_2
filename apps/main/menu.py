# apps/main/menu.py
from apps.common.components.menu import MenuItem, registry


registry.register_item(MenuItem(
    id='inicio',
    label='Inicio',
    url_name='main:index',
    icon='home',
    visible_to_authenticated=True,
    order=0,
))
