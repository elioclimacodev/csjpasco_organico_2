def build_breadcrumbs(*items):
    '''
    Constrye una estructura estándar para breadcrumbs.
    * Ejemplo:
        build_breadcrumbs(
            ('Inicio', reverse('core:home')),
            ('Distritos Judiciales', reverse('organizacion:distritos_judiciales_list'),
            ('Pasco', None),
        )
    '''
    return [
        {
            'label': label,
            'url': url,
        }
        for label, url in items
    ]


BASE_BREADCRUMBS = build_breadcrumbs(
    ('Inicio', '/'),
)