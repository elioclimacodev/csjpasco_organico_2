from django.contrib.auth.models import Permission
from django.test import SimpleTestCase, TestCase

from apps.common.checks import check_menu
from apps.common.components.menu import Badge, MenuItem, MenuSection, UserMenuItem, registry


def codigos(*declaraciones, secciones=(), opciones_usuario=()):
    """Registra las declaraciones en un registro aislado y devuelve los ids de error."""
    with registry.isolated():
        for seccion in secciones:
            registry.register_section(seccion)
        for item in declaraciones:
            registry.register_item(item)
        for opcion in opciones_usuario:
            registry.register_user_item(opcion)
        return [error.id for error in check_menu(None)]


def hoja(**campos):
    """Hoja válida por defecto; los campos indicados la modifican."""
    campos.setdefault('id', 'hoja')
    campos.setdefault('label', 'Hoja')
    if 'url' not in campos:
        campos.setdefault('url_name', 'main:index')
    campos.setdefault('visible_to_authenticated', True)
    return MenuItem(**campos)


class CheckMenuTests(SimpleTestCase):
    """System check del menú (contracts/menu-declaration.md §Reglas; research R5)."""

    def test_declaracion_valida_no_produce_errores(self):
        self.assertEqual(codigos(hoja()), [])

    def test_e101_id_duplicado(self):
        contenedor = MenuItem(id='contenedor', label='Contenedor', children=(hoja(id='repetido'), hoja(id='repetido')))
        self.assertIn('common.E101', codigos(contenedor))

    def test_ids_de_opciones_de_usuario_independientes_de_los_items(self):
        # Los ids de opciones de usuario son independientes de los ítems: no colisionan.
        opcion = UserMenuItem(id='hoja', label='Opción', kind='link', url_name='main:index', visible_to_authenticated=True)
        self.assertNotIn('common.E101', codigos(hoja(), opciones_usuario=[opcion]))

    def test_e102_url_name_no_resoluble(self):
        self.assertIn('common.E102', codigos(hoja(url_name='noexiste:ruta')))

    def test_e102_url_name_con_argumentos_obligatorios(self):
        self.assertIn('common.E102', codigos(hoja(url_name='organizacion:distrito_judicial_details')))

    def test_e102_opcion_de_usuario_no_resoluble(self):
        opcion = UserMenuItem(id='rota', label='Rota', kind='link', url_name='noexiste:ruta', visible_to_authenticated=True)
        self.assertIn('common.E102', codigos(opciones_usuario=[opcion]))

    def test_e103_url_name_y_url_a_la_vez(self):
        self.assertIn('common.E103', codigos(hoja(url_name='main:index', url='https://www.pj.gob.pe/')))

    def test_e103_hoja_sin_destino(self):
        self.assertIn('common.E103', codigos(MenuItem(id='sin_destino', label='Sin destino', visible_to_authenticated=True)))

    def test_e104_contenedor_con_destino(self):
        contenedor = MenuItem(id='contenedor', label='Contenedor', url_name='main:index', children=(hoja(),))
        self.assertIn('common.E104', codigos(contenedor))

    def test_e104_contenedor_con_permisos(self):
        contenedor = MenuItem(
            id='contenedor', label='Contenedor', permissions=('personas.view_persona',), children=(hoja(),),
        )
        self.assertIn('common.E104', codigos(contenedor))

    def test_e105_hoja_sin_permisos_ni_visible_para_autenticados(self):
        self.assertIn('common.E105', codigos(hoja(visible_to_authenticated=False)))

    def test_e106_seccion_inexistente(self):
        self.assertIn('common.E106', codigos(hoja(section='no_registrada')))

    def test_e106_hijo_que_declara_seccion(self):
        seccion = MenuSection(id='organizacion', label='Organización')
        contenedor = MenuItem(
            id='contenedor', label='Contenedor', section='organizacion',
            children=(hoja(section='organizacion'),),
        )
        self.assertIn('common.E106', codigos(contenedor, secciones=[seccion]))

    def test_e107_profundidad_mayor_que_tres(self):
        nivel4 = hoja(id='n4')
        nivel3 = MenuItem(id='n3', label='N3', children=(nivel4,))
        nivel2 = MenuItem(id='n2', label='N2', children=(nivel3,))
        nivel1 = MenuItem(id='n1', label='N1', children=(nivel2,))
        self.assertIn('common.E107', codigos(nivel1))

    def test_e108_icono_inexistente(self):
        self.assertIn('common.E108', codigos(hoja(icon='icono-que-no-existe')))

    def test_e109_variante_de_insignia_no_permitida(self):
        self.assertIn('common.E109', codigos(hoja(badge=Badge(text='Nuevo', variant='danger'))))

    def test_e110_columnas_menor_que_uno(self):
        contenedor = MenuItem(id='contenedor', label='Contenedor', columns=0, children=(hoja(),))
        self.assertIn('common.E110', codigos(contenedor))

    def test_e110_columnas_en_una_hoja(self):
        self.assertIn('common.E110', codigos(hoja(columns=2)))

    def test_e111_url_externa_sin_https(self):
        self.assertIn('common.E111', codigos(hoja(url_name=None, url='http://www.pj.gob.pe/')))

    def test_e112_texto_de_insignia_vacio(self):
        for texto in ['', '   ']:
            with self.subTest(texto=repr(texto)):
                self.assertIn('common.E112', codigos(hoja(badge=Badge(text=texto))))

    def test_e112_texto_de_insignia_vacio_en_un_hijo(self):
        contenedor = MenuItem(id='contenedor', label='Contenedor', children=(hoja(badge=Badge(text='')),))
        self.assertIn('common.E112', codigos(contenedor))

    def test_e113_tipo_de_opcion_de_usuario_no_permitido(self):
        opcion = UserMenuItem(
            id='rara', label='Rara', kind='boton', url_name='main:index', visible_to_authenticated=True,
        )
        self.assertIn('common.E113', codigos(opciones_usuario=[opcion]))

    def test_tipos_de_opcion_de_usuario_permitidos(self):
        opciones = [
            UserMenuItem(id=kind, label=kind, kind=kind, url_name='main:index', visible_to_authenticated=True)
            for kind in ('link', 'post')
        ]
        self.assertNotIn('common.E113', codigos(opciones_usuario=opciones))

    def test_el_registro_real_del_proyecto_no_tiene_errores(self):
        self.assertEqual(check_menu(None), [])


class PermisosDeclaradosTests(TestCase):
    """Cada permiso declarado en el registro real existe en la BD (research R5)."""

    def test_permisos_declarados_existen(self):
        declarados = set()

        def recorrer(items):
            for item in items:
                declarados.update(item.permissions)
                recorrer(item.children)

        recorrer(registry.items())
        for opcion in registry.user_items():
            declarados.update(opcion.permissions)

        for permiso in sorted(declarados):
            app_label, codename = permiso.split('.')
            with self.subTest(permiso=permiso):
                self.assertTrue(
                    Permission.objects.filter(content_type__app_label=app_label, codename=codename).exists(),
                    f'El permiso declarado {permiso} no existe.',
                )


class PermisosDelMenuCoincidenConLaMatrizTests(SimpleTestCase):
    """
    El permiso de cada opción del menú es el que exige su vista destino
    (contrato C5, spec FR-010, SC-008).
    """

    def test_permisos_del_menu_coinciden_con_la_matriz(self):
        from apps.common.tests.helpers import MATRIZ_PERMISOS, RUTAS_SOLO_SESION

        permiso_de_ruta = {url_name: permiso for url_name, permiso, _ in MATRIZ_PERMISOS}

        def recorrer(items):
            for item in items:
                if item.url_name:
                    with self.subTest(item=item.id, url_name=item.url_name):
                        if item.url_name in RUTAS_SOLO_SESION:
                            self.assertEqual(item.permissions, ())
                        else:
                            self.assertIn(item.url_name, permiso_de_ruta, 'Destino fuera de la matriz')
                            self.assertEqual(item.permissions, (permiso_de_ruta[item.url_name],))
                recorrer(item.children)

        recorrer(registry.items())
