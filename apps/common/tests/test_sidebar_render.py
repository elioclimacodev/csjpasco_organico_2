from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from apps.common.tests.helpers import crear_usuario


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
