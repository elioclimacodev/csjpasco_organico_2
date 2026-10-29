from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from apps.common.components.menu import Badge, MenuItem, MenuSection, build_sidebar, registry
from apps.common.tests.helpers import crear_usuario


def hojas(sidebar):
    """Devuelve los ids de todos los ítems resueltos, en orden de recorrido."""
    ids = []

    def recorrer(items):
        for item in items:
            ids.append(item.id)
            recorrer(item.children)

    for seccion in sidebar.sections:
        recorrer(seccion.items)
    return ids


class BuildSidebarFiltradoTests(TestCase):
    """
    Construcción del árbol filtrado (data-model §2–§3, reglas 1–5 y 7;
    spec FR-005, FR-006, FR-007, FR-009, FR-015).
    """

    def setUp(self):
        self.request = RequestFactory().get('/')

    def construir(self, usuario):
        return build_sidebar(usuario, self.request)

    def test_anonimo_devuelve_none(self):
        with registry.isolated():
            registry.register_item(MenuItem(id='inicio', label='Inicio', url_name='main:index', visible_to_authenticated=True))

            self.assertIsNone(self.construir(AnonymousUser()))

    def test_filtrado_con_un_permiso(self):
        con_permiso = crear_usuario(permisos=['organizacion.view_distritojudicial'])
        sin_permiso = crear_usuario()

        with registry.isolated():
            registry.register_item(MenuItem(
                id='distritos', label='Distritos', url_name='main:index',
                permissions=('organizacion.view_distritojudicial',),
            ))

            self.assertEqual(hojas(self.construir(con_permiso)), ['distritos'])
            self.assertEqual(hojas(self.construir(sin_permiso)), [])

    def test_se_exigen_todos_los_permisos_declarados(self):
        uno = crear_usuario(permisos=['organizacion.view_distritojudicial'])
        ambos = crear_usuario(permisos=['organizacion.view_distritojudicial', 'personas.view_persona'])

        with registry.isolated():
            registry.register_item(MenuItem(
                id='doble', label='Doble', url_name='main:index',
                permissions=('organizacion.view_distritojudicial', 'personas.view_persona'),
            ))

            self.assertEqual(hojas(self.construir(uno)), [])
            self.assertEqual(hojas(self.construir(ambos)), ['doble'])

    def test_denegacion_por_defecto_sin_permisos_declarados(self):
        superusuario = crear_usuario(is_superuser=True)

        with registry.isolated():
            registry.register_item(MenuItem(id='sin_permisos', label='Sin permisos', url_name='main:index'))

            self.assertEqual(hojas(self.construir(superusuario)), [])

    def test_visible_para_todo_autenticado(self):
        usuario = crear_usuario()

        with registry.isolated():
            registry.register_item(MenuItem(
                id='inicio', label='Inicio', url_name='main:index', visible_to_authenticated=True,
            ))

            self.assertEqual(hojas(self.construir(usuario)), ['inicio'])

    def test_superusuario_ve_todo_lo_que_declara_permisos(self):
        superusuario = crear_usuario(is_superuser=True)

        with registry.isolated():
            registry.register_item(MenuItem(
                id='distritos', label='Distritos', url_name='main:index',
                permissions=('organizacion.view_distritojudicial',),
            ))

            self.assertEqual(hojas(self.construir(superusuario)), ['distritos'])

    def test_poda_de_contenedores_y_secciones_vacias(self):
        usuario = crear_usuario()

        with registry.isolated():
            registry.register_section(MenuSection(id='vacia', label='Vacía'))
            registry.register_item(MenuItem(
                id='contenedor', label='Contenedor', section='vacia',
                children=(
                    MenuItem(id='oculta', label='Oculta', url_name='main:index', permissions=('personas.view_persona',)),
                ),
            ))
            registry.register_item(MenuItem(
                id='inicio', label='Inicio', url_name='main:index', visible_to_authenticated=True,
            ))

            sidebar = self.construir(usuario)

            self.assertEqual(hojas(sidebar), ['inicio'])
            self.assertEqual([s.id for s in sidebar.sections], [None])

    def test_contenedor_visible_si_algun_hijo_es_visible(self):
        usuario = crear_usuario()

        with registry.isolated():
            registry.register_item(MenuItem(
                id='contenedor', label='Contenedor',
                children=(
                    MenuItem(id='visible', label='Visible', url_name='main:index', visible_to_authenticated=True),
                    MenuItem(id='oculta', label='Oculta', url_name='main:index', permissions=('personas.view_persona',)),
                ),
            ))

            sidebar = self.construir(usuario)

            self.assertEqual(hojas(sidebar), ['contenedor', 'visible'])
            self.assertIsNone(sidebar.sections[0].items[0].href)

    def test_orden_estable_y_grupo_sin_seccion_primero(self):
        usuario = crear_usuario()

        with registry.isolated():
            registry.register_section(MenuSection(id='b', label='Sección B', order=20))
            registry.register_section(MenuSection(id='a', label='Sección A', order=10))
            for item_id, label, section, order in [
                ('z', 'Zeta', 'a', 10),
                ('y', 'Alfa', 'a', 10),
                ('x', 'Primera', 'a', 5),
                ('w', 'En B', 'b', 1),
                ('inicio', 'Inicio', None, 50),
            ]:
                registry.register_item(MenuItem(
                    id=item_id, label=label, section=section, order=order,
                    url_name='main:index', visible_to_authenticated=True,
                ))

            sidebar = self.construir(usuario)

            self.assertEqual([s.id for s in sidebar.sections], [None, 'a', 'b'])
            self.assertEqual(hojas(sidebar), ['inicio', 'x', 'y', 'z', 'w'])

    def test_url_no_resoluble_se_omite_y_registra_advertencia(self):
        usuario = crear_usuario()

        with registry.isolated():
            registry.register_item(MenuItem(
                id='rota', label='Rota', url_name='noexiste:ruta', visible_to_authenticated=True,
            ))
            registry.register_item(MenuItem(
                id='inicio', label='Inicio', url_name='main:index', visible_to_authenticated=True,
            ))

            with self.assertLogs('apps.common.components.menu', 'WARNING'):
                sidebar = self.construir(usuario)

            self.assertEqual(hojas(sidebar), ['inicio'])

    def test_urls_resueltas_e_insignia(self):
        usuario = crear_usuario()

        with registry.isolated():
            registry.register_item(MenuItem(
                id='inicio', label='Inicio', url_name='main:index', visible_to_authenticated=True,
                badge=Badge(text='Nuevo'), order=1,
            ))
            registry.register_item(MenuItem(
                id='externo', label='Externo', url='https://www.pj.gob.pe/', visible_to_authenticated=True,
                order=2,
            ))

            inicio, externo = self.construir(usuario).sections[0].items

            self.assertEqual(inicio.href, '/')
            self.assertFalse(inicio.is_external)
            self.assertEqual(inicio.badge.text, 'Nuevo')
            self.assertEqual(externo.href, 'https://www.pj.gob.pe/')
            self.assertTrue(externo.is_external)

    def test_columnas_siete_hijos_en_tres_columnas(self):
        self.assert_columnas(hijos=7, columnas=3, esperado=[3, 3, 1])

    def test_columnas_cuatro_hijos_en_tres_columnas(self):
        self.assert_columnas(hijos=4, columnas=3, esperado=[2, 2])

    def assert_columnas(self, hijos, columnas, esperado):
        usuario = crear_usuario()

        with registry.isolated():
            registry.register_item(MenuItem(
                id='contenedor', label='Contenedor', columns=columnas,
                children=tuple(
                    MenuItem(id=f'h{i}', label=f'Hijo {i}', order=i, url_name='main:index', visible_to_authenticated=True)
                    for i in range(hijos)
                ),
            ))

            contenedor = self.construir(usuario).sections[0].items[0]

            self.assertEqual([len(columna) for columna in contenedor.columns], esperado)
            # El reparto respeta el orden: se llena cada columna antes de pasar a la siguiente.
            self.assertEqual(
                [hijo.id for columna in contenedor.columns for hijo in columna],
                [f'h{i}' for i in range(hijos)],
            )
