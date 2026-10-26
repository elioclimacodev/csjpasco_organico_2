from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.personas.validators import validar_numero_documento


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _validar_y_crear_persona(
        self, tipo_documento, numero_documento, email, nombres, apellido_paterno,
        apellido_materno, fecha_nacimiento, genero, estado_civil,
    ):
        from apps.personas.models import Persona

        numero_documento = validar_numero_documento(tipo_documento, numero_documento)

        try:
            persona = Persona.objects.get(numero_documento=numero_documento)
            if persona.tipo_documento != tipo_documento:
                raise ValidationError(
                    _(
                        "Ya existe una persona registrada con el número %(numero)s "
                        "pero con otro tipo de documento (%(tipo)s)."
                    ),
                    params={"numero": numero_documento, "tipo": persona.tipo_documento},
                )
            if persona.email.lower() != (email or "").lower():
                raise ValidationError(
                    _(
                        "Ya existe una persona registrada con el número %(numero)s "
                        "y el correo no coincide con el registrado."
                    ),
                    params={"numero": numero_documento},
                )
            return persona

        except Persona.DoesNotExist:
            if Persona.objects.filter(email__iexact=email).exists():
                raise ValidationError(
                    _("Ya existe una persona registrada con ese correo electrónico.")
                )
            persona = Persona(
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                email=email,
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                fecha_nacimiento=fecha_nacimiento,
                genero=genero,
                estado_civil=estado_civil,
            )
            persona.full_clean()
            persona.save()
            return persona

    def _create_user(
        self,
        tipo_documento,
        numero_documento,
        email,
        password,
        is_staff=False,
        is_superuser=False,
        **extra_fields,
    ):
        if not email:
            raise ValueError(_("El correo electrónico es obligatorio."))
        email = self.normalize_email(email)

        persona = self._validar_y_crear_persona(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            email=email,
            nombres=extra_fields.pop("nombres"),
            apellido_paterno=extra_fields.pop("apellido_paterno"),
            apellido_materno=extra_fields.pop("apellido_materno"),
            fecha_nacimiento=extra_fields.pop("fecha_nacimiento", None),
            genero=extra_fields.pop("genero", None),
            estado_civil=extra_fields.pop("estado_civil", None),
        )

        extra_fields.setdefault("is_active", True)
        if self.model.objects.filter(username=persona.numero_documento).exists():
            raise ValidationError(
                _(
                    "Ese número de documento ya está asociado a una cuenta de usuario."
                )
            )
        usuario = self.model(
            username=persona.numero_documento,
            email=persona.email,
            persona=persona,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields,
        )
        usuario.set_password(password)
        usuario.full_clean(exclude=["username", "password"])
        usuario.save(using=self._db)
        return usuario

    def create_user(self, tipo_documento, numero_documento, email, password, **extra_fields):
        return self._create_user(
            tipo_documento,
            numero_documento,
            email,
            password,
            **extra_fields,
        )

    def create_superuser(self, tipo_documento, numero_documento, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("El superusuario debe tener is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("El superusuario debe tener is_superuser=True."))
        return self._create_user(
            tipo_documento,
            numero_documento,
            email,
            password,
            **extra_fields,
        )