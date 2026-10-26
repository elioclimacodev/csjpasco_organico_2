from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.personas.choices import EstadoCivil, Genero, TipoDocumento
from apps.personas.models import Persona
from apps.personas.validators import validar_numero_documento

Usuario = get_user_model()


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


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Número de documento")


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = [
            "tipo_documento",
            "numero_documento",
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "fecha_nacimiento",
            "genero",
            "estado_civil",
            "email",
            "activo",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["numero_documento"].help_text = _(
            "Si la persona tiene cuenta de usuario, este será su nombre de usuario."
        )

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.pk and self.instance.tiene_usuario:
            original = Persona.objects.get(pk=self.instance.pk)
            if (
                cleaned_data.get("tipo_documento")
                and cleaned_data.get("tipo_documento") != original.tipo_documento
            ):
                self.add_error(
                    "tipo_documento",
                    _("No se puede cambiar el tipo de documento porque la persona tiene cuenta de usuario."),
                )
            if (
                cleaned_data.get("numero_documento")
                and cleaned_data.get("numero_documento") != original.numero_documento
            ):
                self.add_error(
                    "numero_documento",
                    _("No se puede cambiar el número de documento porque la persona tiene cuenta de usuario."),
                )
        return cleaned_data


class PerfilForm(forms.Form):
    """Formulario para que el propio usuario edite sus datos personales."""

    nombres = forms.CharField(max_length=100, label="Nombres")
    apellido_paterno = forms.CharField(max_length=100, label="Apellido paterno")
    apellido_materno = forms.CharField(max_length=100, label="Apellido materno")
    fecha_nacimiento = forms.DateField(
        required=False,
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    genero = forms.ChoiceField(
        choices=[("", "--------")] + list(Genero.choices), required=False, label="Género"
    )
    estado_civil = forms.ChoiceField(
        choices=[("", "--------")] + list(EstadoCivil.choices),
        required=False,
        label="Estado civil",
    )
    email = forms.EmailField(label="Correo electrónico")

    def __init__(self, usuario, *args, **kwargs):
        self.usuario = usuario
        super().__init__(*args, **kwargs)
        persona = usuario.persona
        self.fields["nombres"].initial = persona.nombres
        self.fields["apellido_paterno"].initial = persona.apellido_paterno
        self.fields["apellido_materno"].initial = persona.apellido_materno
        self.fields["fecha_nacimiento"].initial = persona.fecha_nacimiento
        self.fields["genero"].initial = persona.genero
        self.fields["estado_civil"].initial = persona.estado_civil
        self.fields["email"].initial = persona.email

    def clean_email(self):
        email = self.cleaned_data["email"]
        qs = Persona.objects.filter(email__iexact=email).exclude(pk=self.usuario.persona.pk)
        if qs.exists():
            raise ValidationError(_("Ese correo electrónico ya lo usa otra persona."))
        return email

    def save(self):
        persona = self.usuario.persona
        persona.nombres = self.cleaned_data["nombres"]
        persona.apellido_paterno = self.cleaned_data["apellido_paterno"]
        persona.apellido_materno = self.cleaned_data["apellido_materno"]
        persona.fecha_nacimiento = self.cleaned_data["fecha_nacimiento"]
        persona.genero = self.cleaned_data["genero"]
        persona.estado_civil = self.cleaned_data["estado_civil"]
        persona.email = self.cleaned_data["email"]
        persona.save()
        self.usuario.email = persona.email
        self.usuario.save(update_fields=["email"])
        return self.usuario


class UsuarioAdminCreationForm(forms.ModelForm):
    tipo_documento = forms.ChoiceField(choices=TipoDocumento.choices, label="Tipo de documento")
    numero_documento = forms.CharField(
        max_length=20, label="Número de documento (nombre de usuario)"
    )
    email = forms.EmailField(label="Correo electrónico")
    nombres = forms.CharField(max_length=100, label="Nombres")
    apellido_paterno = forms.CharField(max_length=100, label="Apellido paterno")
    apellido_materno = forms.CharField(max_length=100, label="Apellido materno")
    fecha_nacimiento = forms.DateField(
        required=False,
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    genero = forms.ChoiceField(
        choices=[("", "--------")] + list(Genero.choices), required=False, label="Género"
    )
    estado_civil = forms.ChoiceField(
        choices=[("", "--------")] + list(EstadoCivil.choices),
        required=False,
        label="Estado civil",
    )
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ("is_staff", "is_active")

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
        password1 = cleaned_data.get("password1")
        if password1:
            validate_password(password1)
        if (
            password1
            and cleaned_data.get("password2")
            and password1 != cleaned_data.get("password2")
        ):
            self.add_error("password2", _("Las contraseñas no coinciden."))
        return cleaned_data

    def save(self, commit=True):
        data = self.cleaned_data
        try:
            user = Usuario.objects.create_user(
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
                is_staff=data.get("is_staff", False),
                is_active=data.get("is_active", True),
            )
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages)
        if commit:
            user.save()
        return user


class UsuarioAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Contraseña"))

    class Meta:
        model = Usuario
        fields = (
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )