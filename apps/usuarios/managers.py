from django.contrib.auth.models import BaseUserManager

# from .choices import EstadoUsuario


class CustomUserManager(BaseUserManager):
    def create_user(self, tipo_documento, numero_documento, email, password=None, **extra_fields):
        if not tipo_documento:
            raise ValueError('El tipo de documento es obligatorio.')
        if not numero_documento:
            raise ValueError('El número de documento es obligatorio.')
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')

        email = self.normalize_email(email).strip().lower()
        # email = email.strip().lower()

        extra_fields.setdefault('is_active', False)
        # extra_fields.setdefault(
        #     'estado',
        #     EstadoUsuario.PENDIENTE_ACTIVACION,
        # )

        user = self.model(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            email=email,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, tipo_documento, numero_documento, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        # extra_fields.setdefault('estado', EstadoUsuario.ACTIVO)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('El superusuario debe tener is_active=True.')

        return self.create_user(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            email=email,
            password=password,
            **extra_fields,
        )