from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse

from apps.common.tests.helpers import crear_usuario


# Listas enlazadas por el menú inicial y el permiso que exige cada una.
LISTAS = [
    ('organizacion:distritos_judiciales_list', 'organizacion.view_distritojudicial'),
    ('organizacion:materias_jurisdiccionales_list', 'organizacion.view_materiajurisdiccional'),
    ('organizacion:organos_jurisdiccionales_list', 'organizacion.view_organojurisdiccional'),
]


class ListasProteccionTests(TestCase):
    """Las listas de Organización exigen sesión y permiso de consulta (spec FR-008a, US1-5)."""

    def test_anonimo_redirige_al_inicio_de_sesion(self):
        for url_name, _ in LISTAS:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))

                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(resolve_url(settings.LOGIN_URL)))

    def test_autenticado_sin_permiso_recibe_403(self):
        self.client.force_login(crear_usuario())

        for url_name, _ in LISTAS:
            with self.subTest(url_name=url_name):
                self.assertEqual(self.client.get(reverse(url_name)).status_code, 403)

    def test_con_permiso_accede(self):
        for url_name, permiso in LISTAS:
            with self.subTest(url_name=url_name):
                self.client.force_login(crear_usuario(permisos=[permiso]))

                self.assertEqual(self.client.get(reverse(url_name)).status_code, 200)
