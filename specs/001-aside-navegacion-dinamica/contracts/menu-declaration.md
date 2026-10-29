# Contrato: declaración del menú por aplicación (API Python interna)

**Consumidores**: cada app de `apps/` que quiera aparecer en el menú lateral.
**Proveedor**: `apps/common/components/menu.py`.
**Estructuras**: ver [data-model.md](../data-model.md) §1.

## Ubicación y descubrimiento

- Cada app declara su menú en `apps/<app>/menu.py`. El archivo es opcional: una app sin menú no lo crea.
- `apps.common` lo descubre automáticamente al arrancar (`autodiscover_modules('menu')` en `CommonConfig.ready()`). No hay que registrarlo en ningún otro sitio.
- `menu.py` solo debe importar `apps.common.components.menu`. NO debe importar vistas, modelos ni consultar la BD. Los permisos se declaran como texto.

## API pública

```python
from apps.common.components.menu import (
    registry, Badge, MenuSection, MenuItem, UserMenuItem,
)

registry.register_section(MenuSection(...))
registry.register_item(MenuItem(...))           # solo ítems de primer nivel
registry.register_user_item(UserMenuItem(...))
```

Los ítems hijos no se registran por separado: van en `children` de su padre.

## Ejemplo normativo (contenido inicial, FR-035)

```python
# apps/main/menu.py
registry.register_item(MenuItem(
    id='inicio', label='Inicio', url_name='main:index',
    icon='home', visible_to_authenticated=True, order=0,
))

# apps/organizacion/menu.py
registry.register_section(MenuSection(id='organizacion', label='Organización', order=10))
# Ítems de primer nivel directamente bajo el título de sección (sin un
# desplegable "Organización" que repetiría el título). Los desplegables,
# columnas y dropend quedan disponibles para módulos futuros y se prueban
# con un registro aislado.
registry.register_item(MenuItem(
    id='distritos_judiciales', label='Distritos judiciales', section='organizacion',
    url_name='organizacion:distritos_judiciales_list', icon='map-pin',
    permissions=('organizacion.view_distritojudicial',),
    active_patterns=('organizacion:distritos_judiciales_*',
                     'organizacion:distrito_judicial_*'),
    order=10,
))
registry.register_item(MenuItem(
    id='materias_jurisdiccionales', label='Materias jurisdiccionales', section='organizacion',
    url_name='organizacion:materias_jurisdiccionales_list', icon='scale',
    permissions=('organizacion.view_materiajurisdiccional',),
    active_patterns=('organizacion:materias_jurisdiccionales_*',
                     'organizacion:materia_jurisdiccional_*'),
    order=20,
))
registry.register_item(MenuItem(
    id='organos_jurisdiccionales', label='Órganos jurisdiccionales', section='organizacion',
    url_name='organizacion:organos_jurisdiccionales_list', icon='building-bank',
    permissions=('organizacion.view_organojurisdiccional',),
    active_patterns=('organizacion:organos_jurisdiccionales_*',
                     'organizacion:organo_jurisdiccional_*'),
    order=30,
))

# apps/personas/menu.py
registry.register_section(MenuSection(id='personas', label='Personas', order=20))
registry.register_item(MenuItem(
    id='personas', label='Personas', section='personas',
    url_name='personas:list', icon='users',
    permissions=('personas.view_persona',),
    active_patterns=('personas:*',), order=10,
))

# apps/usuarios/menu.py
registry.register_section(MenuSection(id='administracion', label='Administración', order=90))
registry.register_item(MenuItem(
    id='usuarios', label='Usuarios', section='administracion',
    url_name='usuarios:list', icon='settings',
    permissions=('usuarios.view_usuario',), order=10,
))
registry.register_user_item(UserMenuItem(
    id='cerrar_sesion', label='Cerrar sesión', kind='post',
    url_name='usuarios:cerrar_sesion', icon='logout',
    visible_to_authenticated=True, order=1000,
))
```

> El contenido exacto (íconos, etiquetas y orden) puede ajustarse en la implementación siempre que respete FR-035 y las reglas siguientes.

## Reglas verificadas por el system check (`manage.py check`)

| Código | Regla |
|---|---|
| `common.E101` | `id` duplicado entre hijos, o de un hijo frente a un ítem de primer nivel. |
| `common.E102` | `url_name` no resoluble sin argumentos. |
| `common.E103` | Ítem con `url_name` y `url` a la vez, o hoja sin destino. |
| `common.E104` | Contenedor con destino propio o con `permissions`. |
| `common.E105` | Hoja sin `permissions` y con `visible_to_authenticated=False` (nunca sería visible). |
| `common.E106` | `section` inexistente, o hijo que declara `section`. |
| `common.E107` | Profundidad mayor que 3. |
| `common.E108` | Plantilla de ícono inexistente. |
| `common.E109` | Variante de `Badge` fuera del conjunto permitido. |
| `common.E110` | `columns < 1`, o `columns > 1` en una hoja. |
| `common.E111` | `url` externa sin esquema `https://`. |
| `common.E112` | Insignia sin texto (vacío o solo espacios): el color no puede ser el único significado (FR-017). |
| `common.E113` | Opción de usuario con `kind` fuera de `link` / `post`. |

Además, un test con BD verifica que cada `permissions` exista como `Permission`.

**Fallo al registrarse (antes del check)**: si un ítem de primer nivel, una sección o una opción de usuario se registran con un `id` ya usado y distinto contenido (por ejemplo, la misma sección con otro `label` u `order`), `MenuRegistry` lanza `ImproperlyConfigured` al importar los `menu.py`. La aplicación no llega a arrancar, por lo que esos casos no aparecen como errores `common.E1xx` del check.

## Obligaciones del consumidor (no verificables automáticamente)

- **Permisos sincronizados con la vista** (spec FR-005): los `permissions` de una opción DEBEN ser exactamente los que exige su vista destino (`permission_required`). Si difieren, el menú ofrecería una página que responde 403, o la ocultaría a quien sí puede verla. Se revisa en la revisión de código; para las opciones del menú inicial, además, lo cubren los tests de FR-008a (con permiso → 200).
- Agregar una opción solo modifica archivos del propio módulo (spec SC-008).

## Garantías del proveedor

- Si en ejecución `reverse` falla, el ítem se omite y se registra un warning: la página no se rompe.
- El orden es estable: `(order, label)`.
- Ocultar un ítem no autoriza ni desautoriza nada: la vista destino DEBE proteger su acceso por su cuenta (FR-008).
