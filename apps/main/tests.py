from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from apps.common.tests.helpers import crear_usuario


class SignupRetiradaTests(TestCase):
    """La página de demostración `signup` se retiró (spec FR-004)."""

    def test_la_direccion_responde_pagina_no_encontrada(self):
        self.client.force_login(crear_usuario())

        response = self.client.get('/signup/')

        self.assertEqual(response.status_code, 404)

    def test_la_ruta_ya_no_existe(self):
        with self.assertRaises(NoReverseMatch):
            reverse('main:signup')


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
