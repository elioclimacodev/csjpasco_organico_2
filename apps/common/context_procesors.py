def htmx_base_template(request):
    '''
    Define dinámicamente el layout base según el tipo de solicitud.
    - Si es HTMX: Usa un layout vacío/parcial.
    - Si es recarga directa (F5): Usa el layout completo con CSS/JS.
    '''

    if request.headers.get('HX-Request'):
        return {'base_template': ''}

    if request.htmx:
        return {'base_template': 'layouts/partial_base.html'}
    return {'base_template': 'layouts/base_page.html'}