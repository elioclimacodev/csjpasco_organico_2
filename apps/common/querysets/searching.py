from django.db.models import Q

from apps.common.utils.text import normalize_alphanumeric


def search_queryset(
    queryset,
    search,
    search_fields=None,
    normalized_fields=None,
):
    '''
    Busca en los campos definidos y en un campo normalizado.
    search: Criterio de búsqueda.
    '''    
    search_fields = search_fields or []
    normalized_fields = normalized_fields or []

    search = (search or '').strip()

    if not search:
        return queryset

    qs = Q()
    normalized_search = normalize_alphanumeric(search.lower())

    for field in search_fields:
        qs |= Q(**{f'{field}__icontains': search})

    for field in normalized_fields:
        qs |= Q(**{f'{field}__icontains': normalized_search})

    return queryset.filter(qs)