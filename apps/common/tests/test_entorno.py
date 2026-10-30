"""
Configuración sensible desde el entorno (feature 002, US4).

contracts/variables-entorno.md; data-model §3 (reglas E1–E4); research R6 y R8.
"""
import os
import re
import subprocess
import sys
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from apps.common.tests.helpers import crear_usuario


RAIZ = Path(settings.BASE_DIR)


class LecturaDelEntornoTests(SimpleTestCase):
    """Reglas E1–E4 de `config/entorno.py` (T035)."""

    def test_e1_cadena_vacia_equivale_a_no_definida(self):
        from config.entorno import env_bool, env_lista

        with mock.patch.dict(os.environ, {'PRUEBA': ''}):
            self.assertTrue(env_bool('PRUEBA', True))
            self.assertEqual(env_lista('PRUEBA', ('a',)), ['a'])

    def test_e2_booleanos_aceptados_sin_distinguir_mayusculas(self):
        from config.entorno import env_bool

        casos = {'true': True, 'TRUE': True, '1': True, 'sí': True, 'Si': True,
                 'false': False, 'False': False, '0': False, 'no': False, 'NO': False}
        for valor, esperado in casos.items():
            with self.subTest(valor=valor), mock.patch.dict(os.environ, {'PRUEBA': valor}):
                self.assertIs(env_bool('PRUEBA', not esperado), esperado)

    def test_e2_booleano_no_reconocido_falla_indicando_los_valores_aceptados(self):
        from config.entorno import env_bool

        with mock.patch.dict(os.environ, {'PRUEBA': 'quizas'}):
            with self.assertRaisesMessage(ImproperlyConfigured, 'PRUEBA'):
                env_bool('PRUEBA', False)
            with self.assertRaisesMessage(ImproperlyConfigured, 'true'):
                env_bool('PRUEBA', False)

    def test_e3_lista_separada_por_comas(self):
        from config.entorno import env_lista

        with mock.patch.dict(os.environ, {'PRUEBA': ' a, ,b '}):
            self.assertEqual(env_lista('PRUEBA'), ['a', 'b'])

    def test_e4_variable_obligatoria_ausente(self):
        from config.entorno import env_requerida

        with mock.patch.dict(os.environ, {'PRUEBA': ''}):
            with self.assertRaisesMessage(ImproperlyConfigured, 'PRUEBA'):
                env_requerida('PRUEBA')
            with self.assertRaisesMessage(ImproperlyConfigured, 'Revise el archivo .env (ver .env.example)'):
                env_requerida('PRUEBA')

    def test_entero(self):
        from config.entorno import env_entero

        with mock.patch.dict(os.environ, {'PRUEBA': '31536000'}):
            self.assertEqual(env_entero('PRUEBA', 0), 31536000)
        for invalido in ('-1', 'x'):
            with self.subTest(valor=invalido), mock.patch.dict(os.environ, {'PRUEBA': invalido}):
                with self.assertRaisesMessage(ImproperlyConfigured, 'PRUEBA'):
                    env_entero('PRUEBA', 0)


def arrancar(**variables):
    """
    Arranca Django en un subproceso con el entorno indicado y devuelve el
    resultado. `load_dotenv` no sobrescribe variables ya presentes, aunque
    estén vacías (research R8, CHK039), así que estas prevalecen sobre el .env.
    """
    entorno = {
        **os.environ,
        'DB_ENGINE': 'sqlite',
        'DJANGO_SETTINGS_MODULE': 'config.settings',
        # Mensajes con tildes legibles también en consolas de Windows.
        'PYTHONIOENCODING': 'utf-8',
        **variables,
    }
    codigo = 'import django; django.setup(); from django.conf import settings; print(settings.DEBUG)'
    return subprocess.run(
        [sys.executable, '-c', codigo],
        cwd=RAIZ, env=entorno, capture_output=True, text=True, encoding='utf-8', timeout=120,
    )


class ArranqueTests(SimpleTestCase):
    """Arranque con la configuración del entorno (T036; R8-d; FR-013, FR-014, SC-007)."""

    def test_sin_clave_secreta_no_arranca(self):
        resultado = arrancar(SECRET_KEY='')

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn('SECRET_KEY', resultado.stderr)

    def test_sin_modo_de_depuracion_queda_desactivado(self):
        resultado = arrancar(DEBUG='', ALLOWED_HOSTS='testserver')

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stdout.strip(), 'False')

    def test_modo_de_depuracion_no_reconocido_no_arranca(self):
        resultado = arrancar(DEBUG='quizas')

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn('DEBUG', resultado.stderr)
        self.assertIn('true', resultado.stderr)

    def test_sin_hosts_y_sin_depuracion_no_arranca(self):
        resultado = arrancar(DEBUG='false', ALLOWED_HOSTS='')

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn('ALLOWED_HOSTS', resultado.stderr)

    def test_origen_sin_esquema_no_arranca(self):
        resultado = arrancar(CSRF_TRUSTED_ORIGINS='erp.ejemplo.pe')

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn('CSRF_TRUSTED_ORIGINS', resultado.stderr)

    def test_cabecera_de_proxy_mal_formada_no_arranca(self):
        resultado = arrancar(SECURE_PROXY_SSL_HEADER='solo_uno')

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn('SECURE_PROXY_SSL_HEADER', resultado.stderr)


class TransporteSeguroTests(TestCase):
    """Transporte seguro simulado sin servidor HTTPS (T037; SC-006a; R8-h)."""

    def setUp(self):
        self.client.force_login(crear_usuario())
        self.url = reverse('main:index')

    @override_settings(SECURE_SSL_REDIRECT=True, SECURE_HSTS_SECONDS=31536000)
    def test_con_transporte_seguro_http_redirige_a_https(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 301)
        self.assertTrue(response.url.startswith('https://'))

    @override_settings(SECURE_SSL_REDIRECT=True, SECURE_HSTS_SECONDS=31536000)
    def test_con_transporte_seguro_https_incluye_hsts(self):
        response = self.client.get(self.url, secure=True)

        self.assertIn('max-age=31536000', response['Strict-Transport-Security'])

    def test_por_defecto_no_redirige(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class CodigoVersionadoTests(SimpleTestCase):
    """El código versionado no contiene secretos ni valores de un entorno (T038; SC-006, FR-015, FR-017)."""

    def test_settings_sin_clave_ni_valores_de_entorno(self):
        texto = (RAIZ / 'config' / 'settings.py').read_text(encoding='utf-8')

        self.assertNotIn('django-insecure', texto)
        self.assertNotIn('gethostbyname', texto)
        self.assertNotIn('github.dev', texto)
        self.assertIsNone(
            re.search(r"""['"][^'"\s]*:\d{2,5}['"]""", texto),
            'settings.py contiene un host u origen con puerto',
        )
