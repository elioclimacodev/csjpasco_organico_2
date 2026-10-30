"""Respuestas a solicitudes HTMX sin sesión o sin permiso (contracts/respuestas-acceso.md)."""
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse


class FragmentoSinSesionTests(TestCase):
    """Contrato §1, FR-012: la página completa va al login con retorno."""

    def setUp(self):
        self.url = reverse('organizacion:distrito_judicial_details', kwargs={'pk': 999999})
        self.login = resolve_url(settings.LOGIN_URL)

    def esperado(self, ruta):
        return f"{self.login}?{urlencode({'next': ruta})}"

    def test_con_url_actual_redirige_a_esa_pagina(self):
        ruta = f"{reverse('organizacion:distritos_judiciales_list')}?page=2"

        response = self.client.get(
            self.url, headers={'HX-Request': 'true', 'HX-Current-URL': f'http://testserver{ruta}'}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, b'')
        self.assertEqual(response['HX-Redirect'], self.esperado(ruta))

    def test_sin_url_actual_retorna_a_inicio(self):
        response = self.client.get(self.url, headers={'HX-Request': 'true'})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['HX-Redirect'], self.esperado(resolve_url(settings.LOGIN_REDIRECT_URL)))

    def test_url_actual_de_otro_host_no_se_usa(self):
        response = self.client.get(
            self.url, headers={'HX-Request': 'true', 'HX-Current-URL': 'https://evil.example/robar/'}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['HX-Redirect'], self.esperado(resolve_url(settings.LOGIN_REDIRECT_URL)))


class FragmentoSinPermisoTests(TestCase):
    """Contrato §2, FR-011, SC-005: denegaciones en ventanas, tablas y páginas."""

    def setUp(self):
        from apps.common.tests.helpers import crear_usuario

        self.client.force_login(crear_usuario())

    def test_en_ventana_muestra_el_aviso_con_cerrar(self):
        response = self.client.get(
            reverse('organizacion:distrito_judicial_details', kwargs={'pk': 999999}),
            headers={'HX-Request': 'true', 'HX-Target': 'modal_content'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'components/modals/modal_denegado.html')
        contenido = response.content.decode()
        self.assertIn('Acceso denegado', contenido)
        self.assertIn('No tiene permiso para acceder a esta página.', contenido)
        self.assertIn('role="alert"', contenido)
        self.assertEqual(contenido.count('autofocus'), 1)
        self.assertEqual(contenido.count('>Cerrar</button>'), 1)
        self.assertIn('data-bs-dismiss="modal"', contenido)
        for prohibido in ('<aside', 'distritojudicial', 'Eliminar', 'Close'):
            self.assertNotIn(prohibido, contenido)

    def test_en_tabla_muestra_un_toast_sin_alterar_la_tabla(self):
        import json

        response = self.client.get(
            reverse('organizacion:distritos_judiciales_list'),
            headers={'HX-Request': 'true', 'HX-Target': 'datatable'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b'')
        self.assertEqual(response['HX-Reswap'], 'none')
        evento = json.loads(response['HX-Trigger'])['show_toast']
        self.assertEqual(evento, {'type': 'error', 'message': 'No tiene permiso para realizar esta operación.'})

    def test_en_pagina_normal_muestra_la_pagina_de_denegacion(self):
        response = self.client.get(reverse('organizacion:distritos_judiciales_list'))

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')


class FalloCsrfTests(TestCase):
    """Contrato §2b (decisión CHK025): fallo CSRF en HTMX recarga la página."""

    def setUp(self):
        from django.test import Client

        from apps.common.tests.helpers import crear_usuario

        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(crear_usuario())
        self.url = reverse('organizacion:distrito_judicial_toggle', kwargs={'pk': 999999})

    def test_en_htmx_responde_con_recarga(self):
        response = self.client.post(self.url, headers={'HX-Request': 'true'})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b'')
        self.assertEqual(response['HX-Refresh'], 'true')

    def test_en_peticion_normal_muestra_la_pagina_de_verificacion_fallida(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403_csrf.html')
