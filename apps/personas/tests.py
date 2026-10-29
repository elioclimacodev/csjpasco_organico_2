from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse

from apps.common.tests.helpers import crear_usuario


class PersonasListProteccionTests(TestCase):
    """La lista de Personas exige sesión y permiso de consulta (spec FR-008a)."""

    def test_anonimo_redirige_al_inicio_de_sesion(self):
        response = self.client.get(reverse('personas:list'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(resolve_url(settings.LOGIN_URL)))

    def test_autenticado_sin_permiso_recibe_403(self):
        self.client.force_login(crear_usuario())

        self.assertEqual(self.client.get(reverse('personas:list')).status_code, 403)

    def test_con_permiso_accede(self):
        self.client.force_login(crear_usuario(permisos=['personas.view_persona']))

        self.assertEqual(self.client.get(reverse('personas:list')).status_code, 200)
