"""Configuración declarativa de HTMX y componente de advertencia (contracts/respuestas-acceso.md §3–§4)."""
import json
import re

from django.conf import settings
from django.test import SimpleTestCase


def leer(ruta):
    return (settings.BASE_DIR / 'templates' / ruta).read_text(encoding='utf-8')


class HtmxConfigTests(SimpleTestCase):

    def test_base_declara_la_regla_del_403_antes_de_la_de_errores(self):
        coincidencia = re.search(r"""<meta name="htmx-config" content='(.*?)'\s*/?>""", leer('base.html'), re.S)
        self.assertIsNotNone(coincidencia, 'base.html no declara <meta name="htmx-config">')

        reglas = json.loads(coincidencia.group(1))['responseHandling']
        codigos = [regla['code'] for regla in reglas]
        self.assertIn({'code': '403', 'swap': True, 'error': False}, reglas)
        self.assertLess(codigos.index('403'), codigos.index('[45]..'))


class ModalWarningTests(SimpleTestCase):

    def test_sin_demostracion_ni_textos_en_ingles(self):
        texto = leer('components/modals/modal_warning.html')

        for prohibido in ('Eliminar 84 items', 'Do you really', 'aria-label="Close"'):
            self.assertNotIn(prohibido, texto)
        self.assertIn('{% block modal_footer %}', texto)
