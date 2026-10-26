from django.db import models


class EstadoUsuario(models.TextChoices):
    PENDIENTE_ACTIVACION    = ('PENDIENTE', 'Pendiente de activación')
    ACTIVO                  = ('ACTIVO', 'Activo')
    BLOQUEADO               = ('BLOQUEADO', 'Bloqueado')
    SUSPENDIDO              = ('SUSPENDIDO', 'Suspendido')