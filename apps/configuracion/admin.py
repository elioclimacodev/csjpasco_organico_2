from django.contrib import admin

from .models import ConfiguracionInstitucional


@admin.register(ConfiguracionInstitucional)
class ConfiguracionInstitucionalAdmin(admin.ModelAdmin):
    """
    Administración de la configuración institucional.
    """

    list_display = (
        'distrito_judicial',
        'corte_superior_justicia',
    )

    search_fields = (
        'distrito_judicial__nombre',
        'corte_superior_justicia__nombre',
    )

    autocomplete_fields = (
        'distrito_judicial',
        'corte_superior_justicia',
    )

    def has_add_permission(self, request):
        """
        Permite crear una única configuración institucional.
        """
        return not ConfiguracionInstitucional.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """
        Impide eliminar la configuración institucional.
        """
        return False