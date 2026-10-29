from django.test import TestCase, override_settings
from django.urls import reverse

from apps.common.tests.helpers import crear_usuario


DEMO = ['Título de la página', 'Pre título', 'Nuevo registro']


@override_settings(DEBUG=False)
class PaginasDeErrorUS1Tests(TestCase):
    """Páginas 403 y 404 (spec FR-008b, Edge Cases "Páginas de error"; research R14)."""

    def test_403_en_espanol_sin_detalles_y_con_aside(self):
        self.client.force_login(crear_usuario())

        response = self.client.get(reverse('organizacion:distritos_judiciales_list'))

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')
        self.assertContains(response, 'No tiene permiso para acceder a esta página', status_code=403)
        self.assertNotContains(response, 'view_', status_code=403)
        self.assertNotContains(response, 'distritojudicial', status_code=403)
        self.assertContains(response, '<aside', status_code=403)
        self.assertContains(response, f'href="{reverse("main:index")}"', status_code=403)
        for texto in DEMO:
            with self.subTest(texto=texto):
                self.assertNotContains(response, texto, status_code=403)

    def test_404_autenticado_con_aside(self):
        self.client.force_login(crear_usuario())

        response = self.client.get('/ruta-que-no-existe/')

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        self.assertContains(response, 'La página solicitada no existe o ha sido movida', status_code=404)
        self.assertContains(response, '<aside', status_code=404)
        for texto in DEMO:
            with self.subTest(texto=texto):
                self.assertNotContains(response, texto, status_code=404)

    def test_404_anonimo_sin_aside(self):
        response = self.client.get('/ruta-que-no-existe/')

        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, '<aside', status_code=404)
