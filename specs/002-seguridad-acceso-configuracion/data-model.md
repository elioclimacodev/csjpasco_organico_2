# Data Model: Protección de operaciones y configuración segura

**Feature**: 002-seguridad-acceso-configuracion | **Fecha**: 2026-10-29

> **No hay modelos de datos, permisos ni migraciones nuevos.** Se usan los permisos nativos `view`, `add` y `change` que Django ya crea para cada modelo existente. Este documento describe las "estructuras" de la feature, que son de configuración y de comportamiento, no de base de datos.

## 1. Clasificación de vistas

| Estructura | Definición | Regla |
|---|---|---|
| **Vista pública** | Vista accesible sin sesión. | Solo las de [contracts/vistas-y-permisos.md](contracts/vistas-y-permisos.md) §1. Se declara con `login_not_required` junto a la vista (o la hereda de la vista nativa de Django). |
| **Vista protegida** | Toda otra vista enrutada. | Exige sesión (middleware) y, salvo `main:index`, un permiso nativo con `permission_required(..., raise_exception=True)`. |

**Invariantes**:
- I1. Toda vista enrutada es pública o protegida; no hay una tercera categoría.
- I2. Toda vista protegida, salvo `main:index`, declara exactamente un permiso de su propia entidad.
- I3. El permiso de una opción del menú lateral coincide con el de su vista destino (spec 001 FR-005).

## 2. Permiso por operación

| Operación (sufijo de la vista) | Acción del permiso |
|---|---|
| `list`, `details`, `export` | `view` |
| `create` | `add` |
| `update`, `toggle` (inactivar y reactivar) | `change` |

Permiso = `<app_label>.<acción>_<modelo>`, con `<modelo>` en minúsculas (p. ej., `ubicaciones.change_provincia`). La matriz completa está en el contrato §2.

## 3. Variables de entorno

Ver la tabla de [research.md](research.md) R6 y [contracts/variables-entorno.md](contracts/variables-entorno.md).

**Reglas de lectura**:
- E1. Una cadena vacía equivale a "no definida".
- E2. Un booleano acepta `true`, `false`, `1`, `0`, `sí`, `si` y `no` sin distinguir mayúsculas; cualquier otro valor → `ImproperlyConfigured`.
- E3. Una lista se separa por comas y se recortan los espacios; los elementos vacíos se ignoran.
- E4. Las variables obligatorias ausentes → `ImproperlyConfigured` con el nombre de la variable y la referencia a `.env.example`.

## 4. Estados de respuesta ante acceso

| Condición | Petición normal | Petición HTMX (`HX-Request: true`) |
|---|---|---|
| Sin sesión, vista protegida | `302` → `LOGIN_URL?next=<ruta>` | `401` + `HX-Redirect: LOGIN_URL?next=<ruta de HX-Current-URL>` |
| Sesión sin permiso | `403` + `templates/403.html` | `HX-Target: modal_content` → `403` + `modal_denegado.html`; otro objetivo → `403` vacío + `HX-Trigger` (`show_toast` error) + `HX-Reswap: none` |
| Con permiso | respuesta de la vista | respuesta de la vista |

Detalle en [contracts/respuestas-acceso.md](contracts/respuestas-acceso.md).

## 5. Usuario sin permisos (FR-003a)

`cuenta_sin_permisos = not user.is_superuser and not user.get_all_permissions()`. Se calcula en `main:index`: si es verdadero, Inicio muestra el aviso; si es falso, no lo muestra.
