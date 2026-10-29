from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from apps.common.components.menu import MenuItem, MenuSection, UserMenuItem, registry


class MenuRegistryTests(SimpleTestCase):
    """Registro único del menú (data-model §1 MenuRegistry; spec FR-003)."""

    def test_registro_idempotente_ante_el_mismo_objeto(self):
        item = MenuItem(id='inicio', label='Inicio', url_name='main:index', visible_to_authenticated=True)

        with registry.isolated():
            registry.register_item(item)
            registry.register_item(item)

            self.assertEqual(registry.items(), (item,))

    def test_id_duplicado_con_distinto_contenido_lanza_error(self):
        with registry.isolated():
            registry.register_item(MenuItem(id='inicio', label='Inicio', url_name='main:index'))

            with self.assertRaises(ImproperlyConfigured):
                registry.register_item(MenuItem(id='inicio', label='Otra', url_name='main:index'))

    def test_seccion_duplicada_con_distinto_contenido_lanza_error(self):
        with registry.isolated():
            registry.register_section(MenuSection(id='organizacion', label='Organización'))

            with self.assertRaises(ImproperlyConfigured):
                registry.register_section(MenuSection(id='organizacion', label='Otra'))

    def test_opcion_de_usuario_duplicada_con_distinto_contenido_lanza_error(self):
        with registry.isolated():
            registry.register_user_item(
                UserMenuItem(id='salir', label='Cerrar sesión', kind='post', url_name='usuarios:cerrar_sesion')
            )

            with self.assertRaises(ImproperlyConfigured):
                registry.register_user_item(
                    UserMenuItem(id='salir', label='Salir', kind='post', url_name='usuarios:cerrar_sesion')
                )

    def test_dos_modulos_comparten_una_seccion(self):
        seccion = MenuSection(id='organizacion', label='Organización', order=10)

        with registry.isolated():
            # Primer módulo.
            registry.register_section(seccion)
            registry.register_item(MenuItem(id='a', label='A', section='organizacion', url_name='main:index'))

            # Segundo módulo: declara la misma sección y otro ítem.
            registry.register_section(MenuSection(id='organizacion', label='Organización', order=10))
            registry.register_item(MenuItem(id='b', label='B', section='organizacion', url_name='main:index'))

            self.assertEqual(registry.sections(), (seccion,))
            self.assertEqual([item.id for item in registry.items()], ['a', 'b'])

    def test_isolated_sustituye_y_restaura_el_contenido(self):
        antes = (registry.sections(), registry.items(), registry.user_items())

        with registry.isolated():
            self.assertEqual(registry.items(), ())
            registry.register_item(MenuItem(id='temporal', label='Temporal', url_name='main:index'))

        self.assertEqual((registry.sections(), registry.items(), registry.user_items()), antes)

    def test_colecciones_de_solo_lectura(self):
        with registry.isolated():
            registry.register_item(MenuItem(id='inicio', label='Inicio', url_name='main:index'))

            self.assertIsInstance(registry.sections(), tuple)
            self.assertIsInstance(registry.items(), tuple)
            self.assertIsInstance(registry.user_items(), tuple)
