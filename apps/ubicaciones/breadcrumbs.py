from apps.common.utils import BASE_BREADCRUMBS, build_breadcrumbs

breadcrumbs = build_breadcrumbs(
    ('Ubicaciones', None),
)

ubicaciones_breadcrumbs = BASE_BREADCRUMBS + breadcrumbs