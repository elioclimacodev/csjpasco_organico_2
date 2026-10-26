# usuarios/management/commands/createsuperuser.py

import re
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from getpass import getpass

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea un superusuario con selección interactiva del tipo de documento'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== CREACIÓN DE SUPERUSUARIO ===\n'))

        # 1. Obtener opciones del campo tipo_documento dinámicamente
        tipo_choices = User._meta.get_field('tipo_documento').choices
        tipo_dict = dict(tipo_choices)  # Para mostrar etiqueta por valor

        # 2. Selección del tipo de documento
        self.stdout.write('Tipos de documento disponibles:')
        for idx, (value, label) in enumerate(tipo_choices, start=1):
            self.stdout.write(f'  {idx}. {label} ({value})')

        tipo_value = None
        while True:
            try:
                selected = input('\nSelecciona el número del tipo de documento: ').strip()
                if not selected:
                    self.stderr.write(self.style.ERROR('Error: Debes ingresar un número.'))
                    continue
                idx = int(selected)
                if 1 <= idx <= len(tipo_choices):
                    tipo_value = tipo_choices[idx-1][0]
                    break
                else:
                    self.stderr.write(self.style.ERROR(f'Error: Número inválido. Elige entre 1 y {len(tipo_choices)}.'))
            except ValueError:
                self.stderr.write(self.style.ERROR('Error: Ingresa un número válido.'))

        # 3. Número de documento
        numero_documento = None
        while True:
            numero_documento = input('\nNúmero de documento: ').strip()
            if not numero_documento:
                self.stderr.write(self.style.ERROR('Error: El número de documento es obligatorio.'))
                continue
            # Validación según tipo (opcional, puedes adaptar)
            if tipo_value == 'DNI' and not re.match(r'^\d{8}$', numero_documento):
                self.stderr.write(self.style.ERROR('Error: DNI debe tener 8 dígitos.'))
                continue
            elif tipo_value == 'PAS' and not re.match(r'^[A-Z0-9]{9,12}$', numero_documento):
                self.stderr.write(self.style.ERROR('Error: Pasaporte debe tener 9 a 12 caracteres alfanuméricos.'))
                continue
            elif tipo_value == 'CEX' and not re.match(r'^[A-Z]\d{8}$', numero_documento):
                self.stderr.write(self.style.ERROR('Error: Carné de Extranjería debe ser una letra seguida de 8 dígitos.'))
                continue
            # Agrega validaciones para otros tipos si lo deseas
            break

        # 4. Correo electrónico
        email = None
        while True:
            email = input('\nCorreo electrónico: ').strip()
            if not email:
                self.stderr.write(self.style.ERROR('Error: El correo electrónico es obligatorio.'))
                continue
            try:
                validate_email(email)
                break
            except ValidationError:
                self.stderr.write(self.style.ERROR('Error: Ingresa un correo electrónico válido.'))

        # 5. Contraseña (con confirmación)
        password = None
        while True:
            password = getpass('\nContraseña: ')
            password2 = getpass('Confirmar contraseña: ')
            if password != password2:
                self.stderr.write(self.style.ERROR('Error: Las contraseñas no coinciden.'))
                continue
            if len(password) < 8:
                self.stderr.write(self.style.ERROR('Error: La contraseña debe tener al menos 8 caracteres.'))
                continue
            # Puedes agregar más validaciones (complejidad) según tus políticas
            break

        # 6. Crear el superusuario
        try:
            user = User.objects.create_superuser(
                numero_documento=numero_documento,
                tipo_documento=tipo_value,
                email=email,
                password=password
            )
            # Si hay campos adicionales como nombres, puedes pedirlos aquí
            # y asignarlos manualmente (si no son obligatorios para superuser)
            self.stdout.write(self.style.SUCCESS('\n✅ Superusuario creado correctamente.'))
            self.stdout.write(f'   Documento: {tipo_value} - {numero_documento}')
            self.stdout.write(f'   Email: {email}')
        except Exception as e:
            # Capturar errores del manager (como duplicados)
            self.stderr.write(self.style.ERROR(f'\n❌ Error al crear el superusuario: {e}'))
            raise CommandError(str(e))