# Data Model: Navegación lateral dinámica

**Feature**: 001-aside-navegacion-dinamica | **Fecha**: 2026-10-28

> **No hay modelos de base de datos ni migraciones en esta feature.** Todas las estructuras de este documento viven en memoria. Las declarativas se crean una vez al arrancar el proceso (registro) y las resueltas se crean por request (árbol entregado a la plantilla). No se persiste información institucional, por lo que no aplican la inactivación ni la auditoría de datos (Principio III).

Ubicación: `apps/common/components/menu.py`.

---

## 1. Estructuras declarativas (inmutables, `@dataclass(frozen=True)`)

### Badge (Insignia)

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `text` | `str` | Sí | Texto en español, no vacío (el color nunca es el único significado, FR-017). |
| `variant` | `str` | No (def. `'light'`) | Uno del conjunto cerrado de spec FR-017: `'light'` (neutra), `'warning'` (advertencia), `'info'` (informativa); contraste en research R9. Un valor fuera del conjunto es un error del system check. |

### MenuSection (Sección)

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `id` | `str` | Sí | Slug único global entre secciones (`organizacion`, `personas`, `administracion`). |
| `label` | `str` | Sí | Título visible en español. |
| `order` | `int` | No (def. `100`) | Orden de la sección. |

- Una misma sección puede recibir ítems de varias apps (US5-2). Si dos apps declaran el mismo `id` de sección, deben usar el mismo `label` y el mismo `order`; si no, el registro falla al arrancar (`ImproperlyConfigured`, ver §MenuRegistry).
- Los ítems sin sección (`section=None`) forman el grupo inicial **sin título** (p. ej., "Inicio"), que se renderiza antes de cualquier sección.

### MenuItem (Opción de menú)

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `id` | `str` | Sí | Único global entre todos los ítems, a cualquier profundidad. |
| `label` | `str` | Sí | Etiqueta en español. |
| `section` | `str \| None` | Solo en primer nivel | Debe referenciar una `MenuSection` registrada. Los hijos lo heredan y no lo declaran. |
| `url_name` | `str \| None` | Excluyente con `url` | `namespace:name`, resoluble con `reverse()` **sin argumentos**. |
| `url` | `str \| None` | Excluyente con `url_name` | URL externa absoluta `https://…`; implica `target="_blank" rel="noopener"` y un aviso accesible (FR-019). |
| `icon` | `str \| None` | No | Nombre de parcial en `templates/components/icons/<icon>.html`; debe existir. |
| `badge` | `Badge \| None` | No | — |
| `permissions` | `tuple[str, ...]` | No (def. `()`) | Cada uno `app_label.codename`; se exigen **todos** (`user.has_perms`). |
| `visible_to_authenticated` | `bool` | No (def. `False`) | `True` = visible para todo autenticado aunque no declare permisos. |
| `order` | `int` | No (def. `100`) | Orden entre hermanos. Desempate por `label`. |
| `children` | `tuple[MenuItem, ...]` | No (def. `()`) | Submenú. |
| `columns` | `int` | No (def. `1`) | ≥ 1. Solo en ítems con hijos; reparte los hijos en `dropdown-menu-column`. |
| `active_patterns` | `tuple[str, ...]` | No (def. `(url_name,)`) | Patrones `namespace:name` con comodines `fnmatch`. Solo en ítems hoja internos. |

**Tipos de ítem (excluyentes)**:
- **Hoja**: tiene `url_name` o `url`, y `children == ()`.
- **Contenedor**: tiene `children`, sin `url_name` ni `url`. No declara permisos propios: es visible solo si algún hijo es visible.

**Profundidad**: el primer nivel (`nav-item`) puede ser hoja o contenedor (`dropdown`). El segundo nivel (`dropdown-item`) puede ser hoja o contenedor (`dropend`). El tercer nivel (`dropdown-item` dentro de `dropend`) solo puede ser hoja. Una profundidad mayor que 3 es error.

### UserMenuItem (Opción de menú de usuario)

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `id` | `str` | Sí | Único entre opciones de usuario. |
| `label` | `str` | Sí | Español. |
| `kind` | `'link' \| 'post'` | Sí | `'post'` se renderiza como formulario POST con CSRF; `'link'` como enlace. |
| `url_name` | `str` | Sí | Resoluble sin argumentos. |
| `icon` | `str \| None` | No | Igual que en `MenuItem`. |
| `permissions` | `tuple[str, ...]` | No | Igual que en `MenuItem`. |
| `visible_to_authenticated` | `bool` | No (def. `False`) | Igual que en `MenuItem`. |
| `order` | `int` | No (def. `100`) | — |
| `divider_before` | `bool` | No (def. `False`) | Dibuja un `dropdown-divider` antes de la opción. |

### MenuRegistry (Registro)

Instancia única en el módulo (`registry`), con:
- `register_section(section)`, `register_item(item)` y `register_user_item(item)`, idempotentes ante el mismo objeto. Un `id` duplicado con distinto contenido lanza `ImproperlyConfigured`.
- `sections()`, `items()` y `user_items()`: colecciones de solo lectura.
- `isolated()`: context manager para tests que sustituye temporalmente el contenido.

---

## 2. Estructuras resueltas por request (entregadas a la plantilla)

Las produce `build_sidebar(user, request) -> Sidebar | None`. Es una función pura respecto del registro: no lo modifica.

### ResolvedItem

| Campo | Tipo | Descripción |
|---|---|---|
| `id`, `label`, `icon`, `badge` | — | Copiados de la declaración. |
| `href` | `str \| None` | URL resuelta (`reverse`) o externa; `None` en contenedores. |
| `is_external` | `bool` | `True` si proviene de `url`. |
| `is_active` | `bool` | Hoja que coincide con la página actual (como máximo una en todo el árbol). |
| `is_active_parent` | `bool` | Contenedor con algún descendiente activo (se renderiza abierto). |
| `children` | `list[ResolvedItem]` | Hijos ya filtrados y ordenados. |
| `columns` | `list[list[ResolvedItem]]` | Hijos repartidos en `columns` columnas (relleno por columnas, en orden). |
| `level` | `int` | 1, 2 o 3. |

### ResolvedSection

| Campo | Tipo | Descripción |
|---|---|---|
| `id`, `label` | `str \| None` | `None` para el grupo inicial sin título. |
| `items` | `list[ResolvedItem]` | Nunca vacía (las secciones vacías se podan). |

### UserPanel

| Campo | Tipo | Descripción |
|---|---|---|
| `full_name` | `str` | `get_full_name()` o, si está vacío, `get_username()`. |
| `secondary` | `str \| None` | Nombre del primer grupo del usuario en orden alfabético; `None` sin grupos. Nunca el username (número de documento). |
| `initials` | `str` | 1–2 letras en mayúsculas (ver regla en research R10). |
| `items` | `list[ResolvedUserItem]` | `{id, label, icon, kind, href, divider_before}` filtrados y ordenados. |

### Sidebar

| Campo | Tipo | Descripción |
|---|---|---|
| `sections` | `list[ResolvedSection]` | Grupo sin título primero y después las secciones por `(order, label)`. |
| `user` | `UserPanel` | — |

`build_sidebar` devuelve `None` si `not user.is_authenticated`. La plantilla no renderiza el `<aside>` en ese caso (FR-001).

---

## 3. Reglas de resolución (orden de aplicación)

> **Importante**: estas reglas solo deciden qué se **muestra**. No autorizan ni desautorizan nada: cada vista destino DEBE verificar su propia autorización (spec FR-008), y una opción DEBE declarar los mismos permisos que exige su vista (spec FR-005).

1. **Visibilidad de una hoja**: `visible_to_authenticated` **o** (`permissions != ()` **y** `user.has_perms(permissions)`). Cualquier otro caso → oculta (denegación por defecto, FR-006).
2. **Resolución de URL**: `reverse(url_name)`. Ante `NoReverseMatch` → la hoja se oculta y se registra `logger.warning('Menú: no se pudo resolver %s', url_name)` (FR-009).
3. **Visibilidad de un contenedor**: visible si y solo si tiene ≥ 1 hijo visible tras aplicar 1–3 recursivamente (FR-007).
4. **Sección**: visible si y solo si tiene ≥ 1 ítem visible (FR-007).
5. **Orden**: `(order, label)` entre hermanos y entre secciones. Es estable.
6. **Estado activo**: se compara `request.resolver_match.view_name` contra los `active_patterns` de las hojas visibles. Gana la coincidencia exacta; entre comodines, el patrón más largo; si sigue empatado, el primero en orden de recorrido. Se marca `is_active` en la hoja ganadora e `is_active_parent` en sus ancestros. Sin `resolver_match` o sin coincidencia → nada activo (US2-4).
7. **Columnas** (spec FR-015): con n = hijos visibles y c = `min(columns, n)`, se calcula k = ⌈n / c⌉. Los hijos, en su orden, se asignan llenando la columna 1 con los primeros k, la columna 2 con los siguientes k, y así sucesivamente; la última columna recibe el resto. Las columnas vacías se descartan (p. ej., n = 7, c = 3 → 3 / 3 / 1; n = 4, c = 3 → k = 2 → 2 / 2, sin tercera columna).

## 4. Relación con entidades existentes

- **Usuario** (`usuarios.Usuario`): solo se lee (`is_authenticated`, `has_perms`, `get_full_name`, `get_username`). No se modifica.
- **Permission** (`django.contrib.auth`): los códigos declarados deben existir (se verifica en un test con BD, research R5).
