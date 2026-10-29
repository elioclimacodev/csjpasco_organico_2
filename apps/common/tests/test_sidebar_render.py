from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse

from apps.common.components.menu import MenuItem, registry
from apps.common.tests.helpers import crear_usuario
from apps.organizacion.models import DistritoJudicial


ASIDE_DIR = Path(settings.BASE_DIR) / 'templates' / 'components' / 'navigation' / 'aside'
ICONS_DIR = Path(settings.BASE_DIR) / 'templates' / 'components' / 'icons'


def aside_html(response):
    """
    Devuelve solo el bloque <aside>…</aside> de la respuesta, o '' si no hay.

    Se aísla el aside porque la página también contiene otros componentes
    (p. ej., la barra superior) cuyo contenido no debe afectar las pruebas.
    """
    html = response.content.decode()
    inicio = html.find('<aside')
    if inicio == -1:
        return ''
    return html[inicio:html.find('</aside>', inicio) + len('</aside>')]


class SidebarRenderUS1Tests(TestCase):
    """
    Render del aside para US1 (spec FR-001, FR-010, FR-011, FR-028, FR-031,
    SC-002, SC-007; contracts/sidebar-template.md §4).
    """

    def test_anonimo_no_ve_el_aside(self):
        response = self.client.get(reverse('usuarios:iniciar_sesion'))

        self.assertNotContains(response, '<aside')
        self.assertNotContains(response, 'id="sidebar-menu"')

    def test_autenticado_ve_la_region_de_navegacion_y_el_boton(self):
        self.client.force_login(crear_usuario())

        aside = aside_html(self.client.get(reverse('main:index')))

        self.assertIn('id="sidebar-menu"', aside)
        self.assertIn('aria-label="Menú principal"', aside)
        self.assertIn('aria-label="Mostrar u ocultar el menú de navegación"', aside)

    def test_logo_institucional(self):
        self.client.force_login(crear_usuario())

        aside = aside_html(self.client.get(reverse('main:index')))

        self.assertIn('project/img/logo-csjpasco.svg', aside)
        self.assertIn('alt="Corte Superior de Justicia de Pasco"', aside)

    def test_sin_permisos_solo_ve_inicio(self):
        self.client.force_login(crear_usuario())

        aside = aside_html(self.client.get(reverse('main:index')))

        self.assertIn('Inicio', aside)
        self.assertNotIn('nav-section-title', aside)

    def test_perfil_organizacion_ve_solo_sus_opciones(self):
        self.client.force_login(crear_usuario(permisos=[
            'organizacion.view_distritojudicial',
            'organizacion.view_materiajurisdiccional',
        ]))

        aside = aside_html(self.client.get(reverse('main:index')))

        self.assertIn('Organización', aside)
        self.assertIn('Distritos judiciales', aside)
        self.assertIn('Materias jurisdiccionales', aside)
        for ausente in ['Órganos jurisdiccionales', 'Personas', 'Administración', 'Usuarios']:
            with self.subTest(ausente=ausente):
                self.assertNotIn(ausente, aside)

    def test_peticion_htmx_no_incluye_el_aside(self):
        self.client.force_login(crear_usuario(permisos=['organizacion.view_distritojudicial']))

        response = self.client.get(
            reverse('organizacion:distritos_judiciales_list'),
            HTTP_HX_REQUEST='true',
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<aside')

    def test_plantillas_del_componente_sin_estilos_inline(self):
        archivos = list(ASIDE_DIR.glob('*.html')) + list(ICONS_DIR.glob('*.html'))
        self.assertTrue(archivos)

        for archivo in archivos:
            with self.subTest(archivo=archivo.name):
                self.assertNotIn('style=', archivo.read_text(encoding='utf-8'))


def render_aside(usuario, path):
    """
    Renderiza el componente aside para una ruta, con su `resolver_match`
    real, sin pasar por la vista.

    Se usa para páginas secundarias (detalle, edición) que en este proyecto
    son fragmentos de modal y no renderizan el aside por sí mismas.
    """
    request = RequestFactory().get(path)
    request.user = usuario
    request.resolver_match = resolve(path)
    return render_to_string('components/navigation/aside/base.html', request=request)


class SidebarRenderUS2Tests(TestCase):
    """Estado activo en el marcado (spec US2-1 a US2-4, FR-020, SC-003)."""

    def setUp(self):
        self.usuario = crear_usuario(permisos=[
            'organizacion.view_distritojudicial',
            'organizacion.view_materiajurisdiccional',
        ])

    def test_lista_de_distritos_una_sola_opcion_actual(self):
        self.client.force_login(self.usuario)

        aside = aside_html(self.client.get(reverse('organizacion:distritos_judiciales_list')))

        self.assertEqual(aside.count('aria-current="page"'), 1)
        self.assertRegex(
            aside,
            r'href="' + reverse('organizacion:distritos_judiciales_list') + r'"\s*aria-current="page"',
        )

    def test_pagina_secundaria_marca_la_opcion_del_mantenimiento(self):
        distrito = DistritoJudicial.objects.create(nombre='Pasco', corte='Corte Superior de Justicia de Pasco')
        detalle = reverse('organizacion:distrito_judicial_details', kwargs={'pk': distrito.pk})

        aside = render_aside(self.usuario, detalle)

        self.assertEqual(aside.count('aria-current="page"'), 1)
        self.assertRegex(
            aside,
            r'href="' + reverse('organizacion:distritos_judiciales_list') + r'"\s*aria-current="page"',
        )

    def test_pagina_sin_opcion_asociada_sin_opcion_actual(self):
        aside = render_aside(self.usuario, reverse('usuarios:list'))

        self.assertIn('<aside', aside)
        self.assertEqual(aside.count('aria-current="page"'), 0)

    def test_contenedor_de_la_opcion_actual_abierto(self):
        with registry.isolated():
            registry.register_item(MenuItem(
                id='grupo', label='Grupo',
                children=(
                    MenuItem(id='inicio', label='Inicio', url_name='main:index', visible_to_authenticated=True),
                ),
            ))

            aside = render_aside(self.usuario, reverse('main:index'))

        self.assertIn('class="nav-item dropdown active"', aside)
        self.assertRegex(aside, r'class="nav-link dropdown-toggle show"[^>]*aria-expanded="true"')
        self.assertIn('class="dropdown-menu show"', aside)
        self.assertRegex(aside, r'class="dropdown-item active"\s*href="/"\s*aria-current="page"')


class SidebarRenderUS3Tests(TestCase):
    """
    Área de usuario y cierre de sesión en el marcado (spec FR-021, FR-023,
    FR-024, FR-028; contracts/sidebar-template.md §3–§4).
    """

    def aside(self, usuario):
        self.client.force_login(usuario)
        return aside_html(self.client.get(reverse('main:index')))

    def area_de_usuario(self, aside):
        return aside[aside.index('class="navbar-footer"'):]

    def test_area_de_usuario_despues_de_la_navegacion(self):
        aside = self.aside(crear_usuario())

        self.assertIn('class="navbar-footer"', aside)
        self.assertGreater(aside.index('class="navbar-footer"'), aside.index('</nav>'))

    def test_cerrar_sesion_es_un_formulario_post_con_csrf(self):
        area = self.area_de_usuario(self.aside(crear_usuario()))

        self.assertRegex(area, r'<form method="post" action="' + reverse('usuarios:cerrar_sesion') + '">')
        self.assertIn('name="csrfmiddlewaretoken"', area)
        self.assertRegex(area, r'<button type="submit" class="dropdown-item">[\s\S]*Cerrar sesión')

    def test_menu_de_usuario_con_una_sola_opcion(self):
        area = self.area_de_usuario(self.aside(crear_usuario()))

        self.assertEqual(area.count('class="dropdown-item"'), 1)

    def test_disparador_con_nombre_accesible(self):
        aside = self.aside(crear_usuario(first_name='Ana', last_name='Pérez'))

        self.assertIn('aria-label="Menú de usuario de Ana Pérez"', aside)

    def test_dato_secundario_es_el_grupo_y_no_el_documento(self):
        usuario = crear_usuario(
            numero_documento='45678912', first_name='Ana', last_name='Pérez', grupos=['Administradores'],
        )

        area = self.area_de_usuario(self.aside(usuario))

        self.assertIn('Administradores', area)
        self.assertNotIn('45678912', area)

    def test_sin_grupos_no_hay_dato_secundario(self):
        area = self.area_de_usuario(self.aside(crear_usuario(first_name='Ana', last_name='Pérez')))

        self.assertNotIn('class="small', area)


SIDEBAR_CSS = Path(settings.BASE_DIR) / 'static' / 'project' / 'css' / 'sidebar.css'
PALETA = ['#a42622', '#eae4d2', '#7a7562']


class SidebarRenderUS4Tests(TestCase):
    """Restricciones de presentación (spec FR-029, FR-030; constitución §Identidad visual)."""

    def test_sidebar_css_no_repite_valores_de_la_paleta(self):
        css = SIDEBAR_CSS.read_text(encoding='utf-8').lower()

        for color in PALETA:
            with self.subTest(color=color):
                self.assertNotIn(color, css)

    def test_selectores_con_especificidad_suficiente_frente_a_tabler(self):
        """
        Regresión de T055: con `.sidebar-institucional` (0,1,0) ganaban las
        reglas de Tabler `.navbar[data-bs-theme=dark]` (0,2,0) y
        `.navbar-vertical[class*=navbar-expand] .navbar-nav .nav-section-title`
        (0,4,0), y el texto quedaba al 70 % o al 49 % de blanco (4.28:1 y
        2.81:1).
        """
        css = SIDEBAR_CSS.read_text(encoding='utf-8')

        self.assertIn('.navbar-vertical.sidebar-institucional[data-bs-theme="dark"] {', css)
        self.assertIn('.navbar-vertical.sidebar-institucional .navbar-nav .nav-section-title {', css)
        self.assertIn('.navbar-vertical.sidebar-institucional .navbar-nav .nav-link-title,', css)

    def test_aside_responsive_con_esquema_local_y_sin_fondos_en_conflicto(self):
        self.client.force_login(crear_usuario())

        aside = aside_html(self.client.get(reverse('main:index')))
        apertura = aside[:aside.index('>') + 1]

        self.assertIn('navbar-expand-lg', apertura)
        self.assertIn('data-bs-theme="dark"', apertura)
        self.assertNotIn('bg-primary', aside)
        self.assertNotIn('sidebar-custom', aside)

    def test_iconos_decorativos(self):
        for archivo in ICONS_DIR.glob('*.html'):
            with self.subTest(archivo=archivo.name):
                self.assertIn('aria-hidden="true"', archivo.read_text(encoding='utf-8'))
