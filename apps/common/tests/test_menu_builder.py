from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.common.components.menu import Badge, MenuItem, MenuSection, UserMenuItem, build_sidebar, registry
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


class BuildSidebarActivoTests(TestCase):
    """
    Estado activo calculado en el servidor (spec FR-020, SC-003;
    data-model §3 regla 6; research R4).
    """

    def setUp(self):
        self.usuario = crear_usuario()

    def construir(self, view_name):
        request = RequestFactory().get('/')
        if view_name is not None:
            request.resolver_match = SimpleNamespace(view_name=view_name)
        return build_sidebar(self.usuario, request)

    def registrar(self, *items):
        for item in items:
            registry.register_item(item)

    def hoja(self, item_id, order=100, **campos):
        campos.setdefault('url_name', 'main:index')
        return MenuItem(id=item_id, label=item_id, order=order, visible_to_authenticated=True, **campos)

    def activos(self, sidebar):
        """Ids de las hojas activas y de los contenedores marcados como padre activo."""
        hojas_activas, padres = [], []

        def recorrer(items):
            for item in items:
                if item.is_active:
                    hojas_activas.append(item.id)
                if item.is_active_parent:
                    padres.append(item.id)
                recorrer(item.children)

        for seccion in sidebar.sections:
            recorrer(seccion.items)
        return hojas_activas, padres

    def test_patron_vacio_equivale_a_su_url_name(self):
        with registry.isolated():
            self.registrar(self.hoja('inicio'))

            self.assertEqual(self.activos(self.construir('main:index')), (['inicio'], []))

    def test_coincidencia_exacta_gana_a_un_comodin(self):
        with registry.isolated():
            self.registrar(
                self.hoja('comodin', order=1, active_patterns=('organizacion:distrito_judicial_*',)),
                self.hoja('exacta', order=2, active_patterns=('organizacion:distrito_judicial_details',)),
            )

            hojas_activas, _ = self.activos(self.construir('organizacion:distrito_judicial_details'))

            self.assertEqual(hojas_activas, ['exacta'])

    def test_entre_comodines_gana_el_patron_mas_largo(self):
        with registry.isolated():
            self.registrar(
                self.hoja('amplio', order=1, active_patterns=('organizacion:*',)),
                self.hoja('especifico', order=2, active_patterns=('organizacion:distrito_*',)),
            )

            hojas_activas, _ = self.activos(self.construir('organizacion:distrito_judicial_update'))

            self.assertEqual(hojas_activas, ['especifico'])

    def test_empate_gana_el_primero_en_el_orden_del_menu(self):
        with registry.isolated():
            self.registrar(
                self.hoja('segundo', order=2, active_patterns=('personas:*',)),
                self.hoja('primero', order=1, active_patterns=('personas:*',)),
            )

            hojas_activas, _ = self.activos(self.construir('personas:list'))

            self.assertEqual(hojas_activas, ['primero'])

    def test_los_ancestros_quedan_como_padre_activo(self):
        with registry.isolated():
            self.registrar(MenuItem(
                id='nivel1', label='Nivel 1',
                children=(
                    MenuItem(id='nivel2', label='Nivel 2', children=(self.hoja('hoja'),)),
                    self.hoja('hermana', url_name='personas:list'),
                ),
            ))

            self.assertEqual(self.activos(self.construir('main:index')), (['hoja'], ['nivel1', 'nivel2']))

    def test_sin_coincidencia_nada_activo(self):
        with registry.isolated():
            self.registrar(self.hoja('inicio'))

            self.assertEqual(self.activos(self.construir('usuarios:list')), ([], []))

    def test_sin_resolver_match_nada_activo(self):
        with registry.isolated():
            self.registrar(self.hoja('inicio'))

            self.assertEqual(self.activos(self.construir(None)), ([], []))

    def test_las_hojas_ocultas_no_se_marcan(self):
        with registry.isolated():
            self.registrar(
                MenuItem(id='oculta', label='oculta', order=1, url_name='main:index',
                         permissions=('personas.view_persona',)),
                self.hoja('visible', order=2),
            )

            self.assertEqual(self.activos(self.construir('main:index')), (['visible'], []))


class BuildSidebarUserPanelTests(TestCase):
    """
    Área de usuario (spec FR-021, FR-025, Edge Cases; research R10;
    data-model §2 UserPanel).
    """

    def panel(self, usuario):
        return build_sidebar(usuario, RequestFactory().get('/')).user

    def test_nombre_completo(self):
        usuario = crear_usuario(first_name='Ana María', last_name='Pérez García')

        self.assertEqual(self.panel(usuario).full_name, 'Ana María Pérez García')

    def test_sin_nombre_usa_el_nombre_de_usuario(self):
        usuario = crear_usuario(numero_documento='45678912')

        self.assertEqual(self.panel(usuario).full_name, '45678912')

    def test_iniciales_de_nombre_y_apellido_paterno(self):
        usuario = crear_usuario(first_name='Ana María', last_name='Pérez García')

        self.assertEqual(self.panel(usuario).initials, 'AP')

    def test_iniciales_conservan_tildes_y_enie(self):
        usuario = crear_usuario(first_name='ángel', last_name='núñez')

        self.assertEqual(self.panel(usuario).initials, 'ÁN')

    def test_iniciales_con_un_solo_termino(self):
        usuario = crear_usuario(first_name='Ñuflo')

        self.assertEqual(self.panel(usuario).initials, 'ÑU')

    def test_iniciales_ignoran_caracteres_no_alfanumericos_iniciales(self):
        usuario = crear_usuario(first_name='(Luis)', last_name='-Rojas')

        self.assertEqual(self.panel(usuario).initials, 'LR')

    def test_iniciales_de_nombre_de_usuario_numerico(self):
        usuario = crear_usuario(numero_documento='45678912')

        self.assertEqual(self.panel(usuario).initials, '45')

    def test_dato_secundario_es_el_primer_grupo_alfabetico(self):
        usuario = crear_usuario(grupos=['Mesa de partes', 'Administradores'])

        self.assertEqual(self.panel(usuario).secondary, 'Administradores')

    def test_sin_grupos_no_hay_dato_secundario(self):
        usuario = crear_usuario(numero_documento='45678912')

        self.assertIsNone(self.panel(usuario).secondary)

    def test_opciones_de_usuario_filtradas_y_ordenadas(self):
        usuario = crear_usuario()

        with registry.isolated():
            registry.register_user_item(UserMenuItem(
                id='salir', label='Cerrar sesión', kind='post', url_name='usuarios:cerrar_sesion',
                visible_to_authenticated=True, order=1000,
            ))
            registry.register_user_item(UserMenuItem(
                id='perfil', label='Perfil', kind='link', url_name='main:index',
                visible_to_authenticated=True, order=10, divider_before=True,
            ))
            registry.register_user_item(UserMenuItem(
                id='restringida', label='Restringida', kind='link', url_name='main:index',
                permissions=('personas.view_persona',),
            ))

            opciones = self.panel(usuario).items

        self.assertEqual([opcion.id for opcion in opciones], ['perfil', 'salir'])
        self.assertEqual(opciones[1].kind, 'post')
        self.assertEqual(opciones[1].href, reverse('usuarios:cerrar_sesion'))
        self.assertTrue(opciones[0].divider_before)
