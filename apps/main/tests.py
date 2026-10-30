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


class AvisoCuentaSinPermisosTests(TestCase):
    """Aviso de Inicio para cuentas sin permisos (spec FR-003a, SC-007a, SC-007b; research R7)."""

    MENSAJE = 'Su cuenta aún no tiene permisos asignados. Solicítelos al administrador del sistema.'
    COMPONENTE = 'components/alerts/aviso_persistente.html'

    def test_usuario_sin_permisos_ve_el_aviso(self):
        self.client.force_login(crear_usuario())

        response = self.client.get(reverse('main:index'))

        self.assertContains(response, self.MENSAJE)
        self.assertContains(response, 'role="status"')
        self.assertTemplateUsed(response, self.COMPONENTE)

    def test_usuario_con_permiso_directo_no_lo_ve(self):
        self.client.force_login(crear_usuario(permisos=['ubicaciones.view_pais']))

        self.assertNotContains(self.client.get(reverse('main:index')), self.MENSAJE)

    def test_usuario_con_permiso_por_grupo_no_lo_ve(self):
        from django.contrib.auth.models import Group, Permission

        grupo = Group.objects.create(name='Consulta')
        grupo.permissions.add(Permission.objects.get(content_type__app_label='ubicaciones', codename='view_pais'))
        self.client.force_login(crear_usuario(grupos=['Consulta']))

        self.assertNotContains(self.client.get(reverse('main:index')), self.MENSAJE)

    def test_superusuario_no_lo_ve(self):
        self.client.force_login(crear_usuario(is_superuser=True))

        self.assertNotContains(self.client.get(reverse('main:index')), self.MENSAJE)

    def test_el_calculo_no_anade_consultas(self):
        """SC-007b: el menú lateral ya cargó la caché de permisos."""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        from unittest import mock

        usuario = crear_usuario()
        self.client.force_login(usuario)

        with CaptureQueriesContext(connection) as con_aviso:
            self.client.get(reverse('main:index'))
        with mock.patch('apps.main.views.cuenta_sin_permisos', return_value=False):
            with CaptureQueriesContext(connection) as sin_calculo:
                self.client.get(reverse('main:index'))

        self.assertEqual(len(con_aviso), len(sin_calculo))
