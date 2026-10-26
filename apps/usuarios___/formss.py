from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class RegistroUsuarioForm(UserCreationForm):
    


class RegistroUsuarioForm(forms.Form):
    """Formulario público de auto-registro de usuarios."""

    tipo_documento = forms.ChoiceField(
        label="Tipo de documento",
        choices=TipoDocumento.choices,
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
        help_text="Este dato será su nombre de usuario para el acceso al sistema.",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    password1 = forms.CharField(
        label="Contraseña", 
        widget=forms.PasswordInput(
            render_value=False,
            attrs={
                'class': 'form-control',
                'x-bind:type': "showPassword ? 'text': 'password'",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña", 
        widget=forms.PasswordInput(
            render_value=False,
            attrs={
                'class': 'form-control',
                'x-bind:type': "showPassword ? 'text': 'password'",
            }
        ),
    )
    nombres = forms.CharField(
        label="Nombres",
        max_length=100, 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    apellido_paterno = forms.CharField(
        label="Apellido paterno",
        max_length=100, 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    apellido_materno = forms.CharField(
        label="Apellido materno",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    fecha_nacimiento = forms.DateField(
        label="Fecha de nacimiento",
        required=False,
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
        required=False, 
        widget=forms.Select(
            attrs={
                'class': 'form-select',
            }
        ),
    )
    estado_civil = forms.ChoiceField(
        label="Estado civil",
        choices=EstadoCivil.choices,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo_documento")
        numero = cleaned_data.get("numero_documento")
        email = cleaned_data.get("email")

        if tipo and numero:
            try:
                validar_numero_documento(tipo, numero)
            except ValidationError as exc:
                self.add_error("numero_documento", exc)
            if Usuario.objects.filter(username=numero).exists():
                self.add_error(
                    "numero_documento",
                    _("Ese número de documento ya está asociado a una cuenta de usuario."),
                )

        if email:
            if Persona.objects.filter(email__iexact=email).exists() and not (
                numero and Persona.objects.filter(numero_documento=numero).exists()
            ):
                self.add_error(
                    "email", _("Ese correo electrónico ya está registrado por otra persona.")
                )
        return cleaned_data

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1:
            validate_password(password1)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Las contraseñas no coinciden."))
        return password2

    def save(self):
        data = self.cleaned_data
        try:
            return Usuario.objects.create_user(
                tipo_documento=data["tipo_documento"],
                numero_documento=data["numero_documento"],
                email=data["email"],
                password=data["password1"],
                nombres=data["nombres"],
                apellido_paterno=data["apellido_paterno"],
                apellido_materno=data["apellido_materno"],
                fecha_nacimiento=data.get("fecha_nacimiento"),
                genero=data.get("genero") or None,
                estado_civil=data.get("estado_civil") or None,
            )
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages)

