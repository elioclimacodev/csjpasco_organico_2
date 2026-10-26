from django.contrib.auth.forms import (
    BaseUserCreationForm, 
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django import forms

from apps.personas.choices import (
    TipoDocumento,
    EstadoCivil,
    Genero,
)

from apps.personas.validators import validate_id_number
from apps.personas.models import Persona
from apps.personas.utils import normalize_id_number

from apps.usuarios.models import Usuario


GENERIC_REGISTRATION_ERROR = (
    'No fue posible completar el registro con los datos proporcionados. '
    'Si ya dispone de una cuenta, puede iniciar sesión, restablecer su '
    'contraseña o solicitar un nuevo enlace de activación.'
)


class RegistrationConflictError(Exception):
    '''
    Se utiliza cuando aparece un conflicto de unicidad durante
    el guardado, incluyendo condiciones de carrera.
    '''
    pass


class UsuarioRegistrationForm(BaseUserCreationForm):

    # ── Datos de persona ────────────

    tipo_documento = forms.ChoiceField(
        label="Tipo de documento",
        choices=TipoDocumento.choices,
        required=True,
        help_text='Seleccione su tipo de documento de identidad.',
        widget=forms.Select(
            attrs={
                'class': 'form-select',
            }
        ),
    )

    numero_documento = forms.CharField(
        label="Número de documento", 
        max_length=20,
        required=True,
        help_text="Este dato será su nombre de usuario para el acceso al sistema.",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'inputmode': 'email',
            }
        ),
    )

    nombres = forms.CharField(
        label="Nombres",
        max_length=100, 
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    apellido_paterno = forms.CharField(
        label="Apellido paterno",
        max_length=100, 
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    apellido_materno = forms.CharField(
        label="Apellido materno",
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    fecha_nacimiento = forms.DateField(
        label="Fecha de nacimiento",
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                "type": "date",
            }
        ),
    )

    genero = forms.ChoiceField(
        label="Género",
        choices=Genero.choices, 
        required=True, 
        widget=forms.Select(
            attrs={
                'class': 'form-select',
            }
        ),
    )

    estado_civil = forms.ChoiceField(
        label="Estado civil",
        choices=EstadoCivil.choices,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
            }
        ),
    )

    class Meta(BaseUserCreationForm.Meta):
        model = Usuario
        fields = (
            'tipo_documento',
            'numero_documento',
            'email',
        )

    # ── Normalización ──────────────────

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if any(character.isspace() for character in email):
            raise ValidationError(
                'El correo electrónico no debe contener espacios.'
            )
        return email

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data['numero_documento']
        return normalize_id_number(numero_documento)

    # ── Validaciones cruzadas ────────────

    def clean(self):
        cleaned_data = super().clean()

        tipo_documento = self.cleaned_data.get('tipo_documento')
        numero_documento = self.cleaned_data.get('numero_documento')
        email = self.cleaned_data.get('email')
        nombres = cleaned_data.get('nombres')
        apellido_paterno = cleaned_data.get('apellido_paterno')
        apellido_materno = cleaned_data.get('apellido_materno')
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        genero = cleaned_data.get('genero')
        estado_civil = cleaned_data.get('estado_civil')

        # Valida el tipo + número de documento

        if tipo_documento and numero_documento:
            try:
                numero_documento = validate_id_number(
                    tipo_documento,
                    numero_documento,
                )
                cleaned_data['numero_documento'] = numero_documento
            except ValidationError as error:
                self.add_error('numero_documento', error)

        # Valida los campos pertenecientes a Persona usando las
        # reglas del modelo.
        # Se han desactivado las validaciones únicas para manejarlo
        # con un mensaje genérico y evitar que el usuario sepa 
        # si un DNI o correo electrónico está registrado en el sistema.

        if all([
            tipo_documento,
            numero_documento,
            email,
            nombres,
            apellido_paterno,
            apellido_materno,
            fecha_nacimiento,
            genero,
            estado_civil,
        ]):
            persona = Persona(
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                email=email,
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                fecha_nacimiento=fecha_nacimiento,
                genero=genero,
                estado_civil=estado_civil
            )

            try:
                persona.full_clean(
                    validate_unique=False,
                    validate_constraints=False,
                )
            except ValidationError as error:
                for field, messages in error.message_dict.items():
                    if field in self.fields:
                        for message in messages:
                            self.add_error(field, message)
                    else:
                        for message in messages:
                            self.add_error(None, message)

        # Evita enumeración de usuarios:

        if email and numero_documento:
            conflict = (
                Usuario.objects.filter(email__iexact=email).exists() or
                Usuario.objects.filter(numero_documento=numero_documento).exists() or
                Persona.objects.filter(email__iexact=email).exists() or
                Persona.objects.filter(
                    tipo_documento=tipo_documento,
                    numero_documento=numero_documento,
                ).exists()
            )

            if conflict:
                raise ValidationError(
                    GENERIC_REGISTRATION_ERROR,
                    code='registration_conflict',
                )

        return cleaned_data

    # ───────────────────────────────────────────────── #
    # Evita que BaseUserCreationForm revele qué campo   #
    # único (unique) está repetido.                     #
    # Esto ya se controla en clean()                    #
    # ───────────────────────────────────────────────── #

    def validate_unique(self):
        pass

    # ── Guardado ────────────────────────

    def save(self, commit=True):
        if not commit:
            raise ValueError(
                'UsuarioRegistrationForm requiere de commit=True '
                'porque crea Usuario y Persona conjuntamente.'
            )

        data = self.cleaned_data

        try:
            with transaction.atomic():
                usuario = Usuario(
                    tipo_documento=data['tipo_documento'],
                    numero_documento=data['numero_documento'],
                    email=data['email'],

                    # La cuenta de usuario permanece inactiva hasta que
                    # el usuario confirma su correo electrónico.
                    is_active=False,
                    # estado=EstadoUsuario.PENDIENTE_ACTIVACION,
                )

                usuario.set_password(data['password1'])

                usuario.full_clean(validate_unique=False)

                usuario.save()

                persona = Persona(
                    usuario=usuario,
                    tipo_documento=data['tipo_documento'],
                    numero_documento=data['numero_documento'],
                    email=data['email'],
                    nombres=data['nombres'],
                    apellido_paterno=data['apellido_paterno'],
                    apellido_materno=data['apellido_materno'],
                    fecha_nacimiento=data['fecha_nacimiento'],
                    genero=data['genero'],
                    estado_civil=data['estado_civil'],
                )

                persona.full_clean(
                    validate_unique=False,
                    validate_constraints=False,
                )

                persona.save()

            return usuario
        
        except IntegrityError as error:
            raise RegistrationConflictError(
                GENERIC_REGISTRATION_ERROR
            ) from error

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'x-bind:type': "showPassword ? 'text': 'password'",
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'x-bind:type': "showPassword ? 'text': 'password'",
        })

        # Nombres y apellidos en mayúsculas.
        for field in (
            'nombres',
            'apellido_paterno',
            'apellido_materno',
        ):
            self.fields[field].widget.attrs.update({
                'x-on:input': '$el.value = $el.value.toUpperCase()',
            })

        # Correo electrónico en minúsculas.
        self.fields['email'].widget.attrs.update({
            'x-on:input': '$el.value = $el.value.toLowerCase()',
        })


