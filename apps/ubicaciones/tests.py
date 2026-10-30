"""Pruebas de acceso de Ubicaciones: permisos por operación (feature 002, US2)."""
from django.test import TestCase

from apps.common.tests import fabricas
from apps.common.tests.helpers import comprobar_sin_efectos, crear_usuario, url_de_prueba


class SinEfectosUbicacionesTests(TestCase):
    """Las operaciones denegadas no producen efectos (contrato C4, FR-009, SC-004)."""

    def test_pais(self):
        obj = fabricas.crear_pais()
        comprobar_sin_efectos(
            self, obj=obj,
            rutas={
                'toggle': 'ubicaciones:country_toggle',
                'update': 'ubicaciones:country_update',
                'create': 'ubicaciones:country_create',
                'export': 'ubicaciones:countries_export',
            },
            kwargs_registro={'pk': obj.pk}, kwargs_padre={},
            permiso_consulta='ubicaciones.view_pais',
        )

    def test_departamento(self):
        obj = fabricas.crear_departamento()
        comprobar_sin_efectos(
            self, obj=obj,
            rutas={
                'toggle': 'ubicaciones:departamento_toggle',
                'update': 'ubicaciones:departamento_update',
                'create': 'ubicaciones:departamento_create',
                'export': 'ubicaciones:departamentos_export',
            },
            kwargs_registro={'pais_id': obj.pais_id, 'pk': obj.pk},
            kwargs_padre={'pais_id': obj.pais_id},
            permiso_consulta='ubicaciones.view_departamento',
        )

    def test_provincia(self):
        obj = fabricas.crear_provincia()
        comprobar_sin_efectos(
            self, obj=obj,
            rutas={
                'toggle': 'ubicaciones:provincia_toggle',
                'update': 'ubicaciones:provincia_update',
                'create': 'ubicaciones:provincia_create',
                'export': 'ubicaciones:provincias_export',
            },
            kwargs_registro={'dpto_id': obj.departamento_id, 'pk': obj.pk},
            kwargs_padre={'dpto_id': obj.departamento_id},
            permiso_consulta='ubicaciones.view_provincia',
        )

    def test_distrito(self):
        obj = fabricas.crear_distrito()
        comprobar_sin_efectos(
            self, obj=obj,
            rutas={
                'toggle': 'ubicaciones:distrito_toggle',
                'update': 'ubicaciones:distrito_update',
                'create': 'ubicaciones:distrito_create',
                'export': 'ubicaciones:distritos_export',
            },
            kwargs_registro={'prov_id': obj.provincia_id, 'pk': obj.pk},
            kwargs_padre={'prov_id': obj.provincia_id},
            permiso_consulta='ubicaciones.view_distrito',
        )


class RutasAnidadasUbicacionesTests(TestCase):
    """
    Contrato C6: se exige solo el permiso de la entidad de la ruta, y se
    comprueba antes que el registro padre (decisión CHK003).
    """

    RUTAS = [
        ('ubicaciones:departamentos_list', 'pais_id', 'ubicaciones.view_departamento'),
        ('ubicaciones:departamento_create', 'pais_id', 'ubicaciones.add_departamento'),
        ('ubicaciones:departamentos_export', 'pais_id', 'ubicaciones.view_departamento'),
        ('ubicaciones:provincias_list', 'dpto_id', 'ubicaciones.view_provincia'),
        ('ubicaciones:provincia_create', 'dpto_id', 'ubicaciones.add_provincia'),
        ('ubicaciones:provincias_export', 'dpto_id', 'ubicaciones.view_provincia'),
        ('ubicaciones:distritos_list', 'prov_id', 'ubicaciones.view_distrito'),
        ('ubicaciones:distrito_create', 'prov_id', 'ubicaciones.add_distrito'),
        ('ubicaciones:distritos_export', 'prov_id', 'ubicaciones.view_distrito'),
    ]

    def test_padre_inexistente(self):
        for url_name, parametro, permiso in self.RUTAS:
            with self.subTest(url_name=url_name):
                url = url_de_prueba(url_name, **{parametro: 999999})

                self.client.force_login(crear_usuario())
                self.assertEqual(self.client.get(url).status_code, 403)

                self.client.force_login(crear_usuario(permisos=[permiso]))
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_no_exige_el_permiso_de_la_entidad_padre(self):
        provincia = fabricas.crear_provincia()
        self.client.force_login(crear_usuario(permisos=['ubicaciones.view_provincia']))

        response = self.client.get(url_de_prueba('ubicaciones:provincias_list', dpto_id=provincia.departamento_id))

        self.assertEqual(response.status_code, 200)
