from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse

from apps.common.tests.helpers import crear_usuario


class PersonasListProteccionTests(TestCase):
    """La lista de Personas exige sesión y permiso de consulta (spec FR-008a)."""

    def test_anonimo_redirige_al_inicio_de_sesion(self):
        response = self.client.get(reverse('personas:list'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(resolve_url(settings.LOGIN_URL)))

    def test_autenticado_sin_permiso_recibe_403(self):
        self.client.force_login(crear_usuario())

        self.assertEqual(self.client.get(reverse('personas:list')).status_code, 403)

    def test_con_permiso_accede(self):
        self.client.force_login(crear_usuario(permisos=['personas.view_persona']))

        self.assertEqual(self.client.get(reverse('personas:list')).status_code, 200)


class PersonaCreateProteccionTests(TestCase):
    """El registro de personas exige el permiso de alta (contrato C3–C4, FR-009)."""

    def test_sin_permiso_recibe_403_y_no_registra(self):
        from apps.personas.models import Persona

        self.client.force_login(crear_usuario(permisos=['personas.view_persona']))
        total = Persona.objects.count()

        response = self.client.post(reverse('personas:create'), {'nombres': 'Nueva'})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Persona.objects.count(), total)

    def test_con_permiso_accede(self):
        self.client.force_login(crear_usuario(permisos=['personas.add_persona']))

        response = self.client.get(reverse('personas:create'))

        self.assertNotEqual(response.status_code, 403)
