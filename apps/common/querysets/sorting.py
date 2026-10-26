def sort_queryset(
    queryset,
    order_by,
    direction,
    order_fields,
    default_field,
):
    '''
    Ordena el queryset solo en los campos permitidos.
    '''
    field = order_fields.get(order_by, default_field)

    prefix = '-' if direction == 'desc' else ''

    return queryset.order_by(f'{prefix}{field}')