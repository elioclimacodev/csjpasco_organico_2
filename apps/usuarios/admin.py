from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.personas.models import Persona
from .models import Usuario


class UsuarioAdmin(UserAdmin):
    # Campos que se muestran en el listado.
    list_display = ('tipo_documento', 'numero_documento', 'email', 'is_staff')

    # Los campos que se usan para buscar.
    search_fields = ('numero_documento', 'email')

    # Orden por defecto.
    ordering = ('numero_documento', )

    # Los campos que aparecen al editar/crear (agrupados).
    fieldsets = (
        (None, {'fields': ('tipo_documento', 'numero_documento', 'email', 'password')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Auditoría', {'fields': ('last_login', 'date_joined')}),
    )
    add_fields = (
        (
            None, {
                'classess': ('wide', ),
                'fields': ('tipo_documento', 'numero_documento', 'email', 'password1', 'password2'),
            }
        ),
    )

admin.site.register(Usuario, UsuarioAdmin)