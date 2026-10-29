from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse

from apps.common.tests.helpers import crear_usuario


class CerrarSesionTests(TestCase):
    """Cierre de sesión por POST con CSRF (spec FR-024, FR-024a, SC-004, Edge Cases)."""

    def setUp(self):
        self.url = reverse('usuarios:cerrar_sesion')

    def test_post_cierra_la_sesion_y_redirige_al_inicio_de_sesion(self):
        self.client.force_login(crear_usuario())

        response = self.client.post(self.url)

        self.assertRedirects(response, resolve_url(settings.LOGOUT_REDIRECT_URL), fetch_redirect_response=False)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_get_no_cierra_la_sesion(self):
        self.client.force_login(crear_usuario())

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)

    def test_post_con_sesion_expirada_redirige_sin_error(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, resolve_url(settings.LOGOUT_REDIRECT_URL), fetch_redirect_response=False)


class CerrarSesionCsrfTests(TestCase):
    """Cierre de sesión con verificación anti-falsificación inválida (spec Edge Cases)."""

    def test_post_sin_token_no_cierra_la_sesion_y_explica_en_espanol(self):
        from django.test import Client

        client = Client(enforce_csrf_checks=True)
        client.force_login(crear_usuario())

        response = client.post(reverse('usuarios:cerrar_sesion'))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, 'La solicitud no pudo verificarse', status_code=403)
        self.assertIn('_auth_user_id', client.session)
