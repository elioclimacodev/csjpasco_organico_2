"""Consistencia de la matriz de acceso con el enrutador (data-model §1 I1; contrato §1–§2)."""
from unittest import expectedFailure

from django.contrib.auth.models import Permission
from django.test import TestCase

from apps.common.tests import fabricas
from apps.common.tests.helpers import (
    MATRIZ_PERMISOS,
    RUTAS_PUBLICAS,
    RUTAS_SOLO_SESION,
    rutas_enrutadas,
)


class MatrizAccesoTests(TestCase):

    def test_la_matriz_tiene_las_51_rutas_del_contrato(self):
        self.assertEqual(len(MATRIZ_PERMISOS), 51)
        self.assertEqual(len({fila[0] for fila in MATRIZ_PERMISOS}), 51)

    # Falla hasta que T015 retire `main:signup`; T015 quita este marcador.
    @expectedFailure
    def test_toda_ruta_enrutada_esta_clasificada(self):
        clasificadas = set(RUTAS_PUBLICAS) | set(RUTAS_SOLO_SESION) | {fila[0] for fila in MATRIZ_PERMISOS}
        enrutadas = {nombre for nombre, _ in rutas_enrutadas()}

        self.assertEqual(enrutadas, clasificadas)

    def test_cada_permiso_de_la_matriz_existe(self):
        for url_name, permiso, _ in MATRIZ_PERMISOS:
            app_label, codename = permiso.split('.')
            with self.subTest(url_name=url_name):
                self.assertTrue(
                    Permission.objects.filter(content_type__app_label=app_label, codename=codename).exists(),
                    f'No existe el permiso {permiso}',
                )


class FabricasTests(TestCase):
    """Las fábricas crean registros válidos con sus relaciones."""

    def test_las_fabricas_crean_registros(self):
        distrito = fabricas.crear_distrito()
        sede = fabricas.crear_sede_judicial()

        self.assertIsNotNone(distrito.provincia.departamento.pais.pk)
        self.assertIsNotNone(sede.distrito_judicial.pk)
        self.assertIsNotNone(fabricas.crear_materia_jurisdiccional().pk)
        self.assertIsNotNone(fabricas.crear_organo_jurisdiccional().pk)
        self.assertIsNotNone(fabricas.crear_persona().pk)
