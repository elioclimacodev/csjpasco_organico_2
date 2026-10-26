from django.db.models import Q


def filter_by_status(
    queryset,
    status,
    status_field='activo',
):
    '''
    Filtra el queryset por estado (activo/inactivo).
    '''
    if status == '1':
        return queryset.filter(**{status_field: True})
    elif status == '0':
        return queryset.filter(**{status_field: False})
    
    return queryset