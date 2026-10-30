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
