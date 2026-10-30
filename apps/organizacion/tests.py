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


from apps.common.tests import fabricas
from apps.common.tests.helpers import comprobar_sin_efectos, url_de_prueba


class SinEfectosOrganizacionTests(TestCase):
    """Las operaciones denegadas no producen efectos (contrato C4, FR-009, SC-004)."""

    def test_distrito_judicial(self):
        obj = fabricas.crear_distrito_judicial()
        comprobar_sin_efectos(
            self, obj=obj,
            rutas={
                'toggle': 'organizacion:distrito_judicial_toggle',
                'update': 'organizacion:distrito_judicial_update',
                'create': 'organizacion:distrito_judicial_create',
                'export': 'organizacion:distritos_judiciales_export',
            },
            kwargs_registro={'pk': obj.pk}, kwargs_padre={},
            permiso_consulta='organizacion.view_distritojudicial',
        )

    def test_materia_jurisdiccional(self):
        obj = fabricas.crear_materia_jurisdiccional()
        comprobar_sin_efectos(
            self, obj=obj,
            rutas={
                'toggle': 'organizacion:materia_jurisdiccional_toggle',
                'update': 'organizacion:materia_jurisdiccional_update',
                'create': 'organizacion:materia_jurisdiccional_create',
                'export': 'organizacion:materias_jurisdiccionales_export',
            },
            kwargs_registro={'pk': obj.pk}, kwargs_padre={},
            permiso_consulta='organizacion.view_materiajurisdiccional',
        )

    def test_organo_jurisdiccional(self):
        obj = fabricas.crear_organo_jurisdiccional()
        comprobar_sin_efectos(
            self, obj=obj,
            rutas={
                'toggle': 'organizacion:organo_jurisdiccional_toggle',
                'update': 'organizacion:organo_jurisdiccional_update',
                'create': 'organizacion:organo_jurisdiccional_create',
                'export': 'organizacion:organos_jurisdiccionales_export',
            },
            kwargs_registro={'pk': obj.pk}, kwargs_padre={},
            permiso_consulta='organizacion.view_organojurisdiccional',
        )

    def test_sede_judicial(self):
        obj = fabricas.crear_sede_judicial()
        comprobar_sin_efectos(
            self, obj=obj,
            rutas={
                'toggle': 'organizacion:sede_toggle',
                'update': 'organizacion:sede_update',
                'create': 'organizacion:sede_create',
                'export': 'organizacion:sedes_export',
            },
            kwargs_registro={'pk': obj.pk}, kwargs_padre={'dj_id': obj.distrito_judicial_id},
            permiso_consulta='organizacion.view_sedejudicial',
        )


class RutasAnidadasSedesTests(TestCase):
    """Contrato C6: el permiso se comprueba antes que el registro padre (decisión CHK003)."""

    RUTAS = [
        ('organizacion:sedes_list', 'organizacion.view_sedejudicial'),
        ('organizacion:sede_create', 'organizacion.add_sedejudicial'),
        ('organizacion:sedes_export', 'organizacion.view_sedejudicial'),
    ]

    def test_padre_inexistente(self):
        for url_name, permiso in self.RUTAS:
            with self.subTest(url_name=url_name):
                url = url_de_prueba(url_name, dj_id=999999)

                self.client.force_login(crear_usuario())
                self.assertEqual(self.client.get(url).status_code, 403)

                self.client.force_login(crear_usuario(permisos=[permiso]))
                self.assertEqual(self.client.get(url).status_code, 404)
