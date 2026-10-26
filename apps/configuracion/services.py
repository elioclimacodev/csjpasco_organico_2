from django.core.cache import cache

from .models import ConfiguracionInstitucional


def get_institutional_settings():
    '''
    Obtiene la configuración institucional.
    '''
    return (
        ConfiguracionInstitucional.objects
        .select_related(
            'distrito_judicial',
            'corte_superior_justicia',
        )
        .get(pk=1)
    )


# Versión con caché:
# def get_institucional_settings():
#     cache_key = 'institucional_settings'

#     settings = cache.get(cache_key)

#     if settings is None:
#         settings = (
#             ConfiguracionInstitucional.objects.select_related(
#                 'distrito_judicial',
#                 'corte_superior_justicia',
#             ).first()
#         )

#         cache.set(cache_key, settings, timeout=3600)

#     return settings