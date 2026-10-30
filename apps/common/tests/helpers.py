from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission


_contador = 0


def crear_usuario(permisos=(), grupos=(), **campos):
    """
    Crea un usuario activo para pruebas.

    `CustomUserManager.create_user` crea los usuarios inactivos por defecto,
    y Django no concede permisos a usuarios inactivos; por eso aquí se
    fuerza `is_active=True`.

    :param permisos: Permisos con formato 'app_label.codename'.
    :param grupos: Nombres de grupos a los que se agrega el usuario (se
        crean si no existen).
    :param campos: Campos adicionales del usuario (p. ej., first_name).
    """
    global _contador
    _contador += 1

    campos.setdefault('numero_documento', f'{40000000 + _contador}')
    campos.setdefault('email', f'usuario{_contador}@prueba.pe')
    campos.setdefault('is_active', True)

    usuario = get_user_model().objects.create_user(
        tipo_documento='DNI',
        password='clave-de-prueba',
        **campos,
    )

    for permiso in permisos:
        app_label, codename = permiso.split('.')
        usuario.user_permissions.add(
            Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename,
            )
        )

    for nombre in grupos:
        grupo, _ = Group.objects.get_or_create(name=nombre)
        usuario.groups.add(grupo)

    return usuario


# ── Matriz de acceso (contracts/vistas-y-permisos.md) ───────────────────
# Única fuente de los tests de acceso de la feature 002: si una ruta cambia,
# se actualiza aquí y en el contrato.

KWARGS_PRUEBA = {
    'pk': 999999,
    'pais_id': 999999,
    'dpto_id': 999999,
    'prov_id': 999999,
    'dj_id': 999999,
    'uidb64': 'x',
    'token': 'y',
}

# Contrato §1: accesibles sin sesión.
RUTAS_PUBLICAS = [
    'usuarios:iniciar_sesion',
    'usuarios:cerrar_sesion',
    'usuarios:restablecer_contrasena',
    'usuarios:restablecer_contrasena_enviado',
    'usuarios:restablecer_contrasena_confirmar',
    'usuarios:restablecer_contrasena_completado',
    'usuarios:registro',
    'usuarios:activar_cuenta',
    'usuarios:registro_completo',
]

# Contrato §2: exigen sesión, pero no un permiso de entidad.
RUTAS_SOLO_SESION = [
    'main:index',
    'usuarios:cambiar_contrasena',
    'usuarios:cambiar_contrasena_completado',
]


def _filas_entidad(prefijo, permiso_base, list_, details, export, create, update, toggle):
    """Filas de la matriz para una entidad con sus seis operaciones."""
    app_label, modelo = permiso_base.split('.')
    return [
        (f'{prefijo}:{list_}', f'{app_label}.view_{modelo}', 'list'),
        (f'{prefijo}:{details}', f'{app_label}.view_{modelo}', 'details'),
        (f'{prefijo}:{export}', f'{app_label}.view_{modelo}', 'export'),
        (f'{prefijo}:{create}', f'{app_label}.add_{modelo}', 'create'),
        (f'{prefijo}:{update}', f'{app_label}.change_{modelo}', 'update'),
        (f'{prefijo}:{toggle}', f'{app_label}.change_{modelo}', 'toggle'),
    ]


# Contrato §2: (url_name, permiso, operación). 51 filas.
MATRIZ_PERMISOS = [
    *_filas_entidad(
        'organizacion', 'organizacion.distritojudicial',
        'distritos_judiciales_list', 'distrito_judicial_details', 'distritos_judiciales_export',
        'distrito_judicial_create', 'distrito_judicial_update', 'distrito_judicial_toggle',
    ),
    *_filas_entidad(
        'organizacion', 'organizacion.materiajurisdiccional',
        'materias_jurisdiccionales_list', 'materia_jurisdiccional_details', 'materias_jurisdiccionales_export',
        'materia_jurisdiccional_create', 'materia_jurisdiccional_update', 'materia_jurisdiccional_toggle',
    ),
    *_filas_entidad(
        'organizacion', 'organizacion.organojurisdiccional',
        'organos_jurisdiccionales_list', 'organo_jurisdiccional_details', 'organos_jurisdiccionales_export',
        'organo_jurisdiccional_create', 'organo_jurisdiccional_update', 'organo_jurisdiccional_toggle',
    ),
    *_filas_entidad(
        'organizacion', 'organizacion.sedejudicial',
        'sedes_list', 'sede_details', 'sedes_export',
        'sede_create', 'sede_update', 'sede_toggle',
    ),
    ('personas:list', 'personas.view_persona', 'list'),
    ('personas:create', 'personas.add_persona', 'create'),
    *_filas_entidad(
        'ubicaciones', 'ubicaciones.pais',
        'countries_list', 'country_details', 'countries_export',
        'country_create', 'country_update', 'country_toggle',
    ),
    *_filas_entidad(
        'ubicaciones', 'ubicaciones.departamento',
        'departamentos_list', 'departamento_details', 'departamentos_export',
        'departamento_create', 'departamento_update', 'departamento_toggle',
    ),
    *_filas_entidad(
        'ubicaciones', 'ubicaciones.provincia',
        'provincias_list', 'provincia_details', 'provincias_export',
        'provincia_create', 'provincia_update', 'provincia_toggle',
    ),
    *_filas_entidad(
        'ubicaciones', 'ubicaciones.distrito',
        'distritos_list', 'distrito_details', 'distritos_export',
        'distrito_create', 'distrito_update', 'distrito_toggle',
    ),
    ('usuarios:list', 'usuarios.view_usuario', 'list'),
]


def rutas_enrutadas():
    """
    Recorre el enrutador del proyecto y devuelve `(url_name, parámetros)`
    de cada ruta, excluyendo el panel de administración (tiene su propio
    control) y la ruta de archivos estáticos de `static()`.

    Una ruta sin nombre que no sea la de estáticos se devuelve con
    `url_name=None` para que la verificación de clasificación la detecte.
    """
    from django.urls import URLResolver, get_resolver
    from django.views.static import serve

    def recorrer(patrones, espacio=None, parametros=()):
        for patron in patrones:
            params = parametros + tuple(getattr(patron.pattern, 'converters', {}).keys())
            if isinstance(patron, URLResolver):
                if patron.namespace == 'admin':
                    continue
                nuevo = espacio
                if patron.namespace:
                    nuevo = f'{espacio}:{patron.namespace}' if espacio else patron.namespace
                yield from recorrer(patron.url_patterns, nuevo, params)
            elif patron.callback is serve:
                continue
            else:
                nombre = None
                if patron.name:
                    nombre = f'{espacio}:{patron.name}' if espacio else patron.name
                yield nombre, params

    return list(recorrer(get_resolver().url_patterns))


def url_de_prueba(url_name, **overrides):
    """Construye la URL de `url_name` con los valores de prueba de los parámetros que acepta."""
    from django.urls import reverse

    parametros = dict(rutas_enrutadas())[url_name]
    kwargs = {p: overrides.get(p, KWARGS_PRUEBA[p]) for p in parametros}
    return reverse(url_name, kwargs=kwargs)


XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def comprobar_sin_efectos(test, *, obj, rutas, kwargs_registro, kwargs_padre, permiso_consulta):
    """
    Comprueba que las operaciones denegadas no producen efectos (contrato
    C4, spec FR-009, SC-004).

    :param test: El `TestCase` que ejecuta las aserciones.
    :param obj: Registro existente de la entidad (con campos `activo` y `nombre`).
    :param rutas: Diccionario con los `url_name` de 'toggle', 'update',
        'create' y 'export'.
    :param kwargs_registro: Parámetros de las rutas del registro (toggle, update).
    :param kwargs_padre: Parámetros de las rutas de la colección (create, export).
    :param permiso_consulta: Permiso `view` de la entidad.
    """
    from django.urls import reverse

    modelo = type(obj)
    test.client.force_login(crear_usuario(permisos=[permiso_consulta]))

    estado = obj.activo
    response = test.client.post(reverse(rutas['toggle'], kwargs=kwargs_registro))
    test.assertEqual(response.status_code, 403)
    obj.refresh_from_db()
    test.assertEqual(obj.activo, estado, 'La inactivación denegada cambió el estado')

    nombre = obj.nombre
    response = test.client.post(reverse(rutas['update'], kwargs=kwargs_registro), {'nombre': 'Nombre cambiado'})
    test.assertEqual(response.status_code, 403)
    obj.refresh_from_db()
    test.assertEqual(obj.nombre, nombre, 'La modificación denegada cambió el registro')

    total = modelo.objects.count()
    response = test.client.post(reverse(rutas['create'], kwargs=kwargs_padre), {'nombre': 'Registro nuevo'})
    test.assertEqual(response.status_code, 403)
    test.assertEqual(modelo.objects.count(), total, 'El registro denegado creó un registro')

    test.client.force_login(crear_usuario())
    response = test.client.get(reverse(rutas['export'], kwargs=kwargs_padre))
    test.assertEqual(response.status_code, 403)
    test.assertNotEqual(response.get('Content-Type'), XLSX, 'La exportación denegada generó un archivo')
