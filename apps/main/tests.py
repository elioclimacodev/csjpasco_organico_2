from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse

from apps.common.tests.helpers import crear_usuario


class IndexProteccionTests(TestCase):
    """Inicio exige sesión autenticada (spec FR-008a, US1-6)."""

    def test_anonimo_redirige_al_inicio_de_sesion(self):
        response = self.client.get(reverse('main:index'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(resolve_url(settings.LOGIN_URL)))

    def test_autenticado_accede(self):
        self.client.force_login(crear_usuario())

        response = self.client.get(reverse('main:index'))

        self.assertEqual(response.status_code, 200)
