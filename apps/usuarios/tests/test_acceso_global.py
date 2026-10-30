"""
Denegación por defecto y vistas públicas (feature 002, US1).

Recorre todas las rutas enrutadas con la matriz única de
`apps/common/tests/helpers.py` (contracts/vistas-y-permisos.md §1–§3).
"""
from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase, modify_settings
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.urls import reverse

from apps.common.tests.helpers import (
    RUTAS_PUBLICAS,
    crear_usuario,
    rutas_enrutadas,
    url_de_prueba,
)


def redirige_al_login(response):
    """Indica si la respuesta es una redirección al inicio de sesión."""
    return response.status_code == 302 and response.url.startswith(resolve_url(settings.LOGIN_URL))


class DenegacionPorDefectoTests(TestCase):
    """R8-a, C1, FR-001, FR-005, SC-001."""

    def test_toda_ruta_no_publica_redirige_al_anonimo_al_login_con_retorno(self):
        for url_name, _ in rutas_enrutadas():
            if url_name in RUTAS_PUBLICAS:
                continue
            with self.subTest(url_name=url_name):
                response = self.client.get(url_de_prueba(url_name))

                self.assertTrue(
                    redirige_al_login(response),
                    f'{url_name} respondió {response.status_code} a un anónimo',
                )
                self.assertIn('next=', response.url)

    def test_la_exigencia_de_sesion_no_anade_consultas(self):
        """SC-007b: misma petición con y sin el middleware, mismo número de consultas."""
        self.client.force_login(crear_usuario(permisos=['organizacion.view_distritojudicial']))
        url = reverse('organizacion:distritos_judiciales_list')

        with CaptureQueriesContext(connection) as con_middleware:
            self.client.get(url)

        with modify_settings(MIDDLEWARE={'remove': ['apps.usuarios.middleware.LoginRequiredMiddleware']}):
            with CaptureQueriesContext(connection) as sin_middleware:
                self.client.get(url)

        self.assertEqual(len(con_middleware), len(sin_middleware))


class VistasPublicasTests(TestCase):
    """FR-003, SC-002 y regresión de la feature 001."""

    def test_las_paginas_publicas_responden_sin_sesion(self):
        for url_name in RUTAS_PUBLICAS:
            if url_name == 'usuarios:cerrar_sesion':
                continue  # Solo acepta POST (prueba siguiente).
            with self.subTest(url_name=url_name):
                response = self.client.get(url_de_prueba(url_name))

                self.assertFalse(redirige_al_login(response), f'{url_name} exige sesión')
                self.assertLess(response.status_code, 500)

    def test_cerrar_sesion_anonimo_redirige_sin_next(self):
        response = self.client.post(reverse('usuarios:cerrar_sesion'))

        self.assertRedirects(
            response, resolve_url(settings.LOGOUT_REDIRECT_URL), fetch_redirect_response=False
        )

    def test_tras_iniciar_sesion_vuelve_a_la_pagina_pedida(self):
        """FR-005, US1-4."""
        crear_usuario(numero_documento='45678912')
        destino = reverse('ubicaciones:countries_list')

        response = self.client.post(
            f"{reverse('usuarios:iniciar_sesion')}?next={destino}",
            {'username': '45678912', 'password': 'clave-de-prueba', 'next': destino},
        )

        self.assertRedirects(response, destino, fetch_redirect_response=False)
