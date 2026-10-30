# Contrato: respuestas ante falta de sesión o de permiso

**Proveedores**:
- `apps/usuarios/middleware.py:LoginRequiredMiddleware` (sin sesión);
- `apps/usuarios/views/denegacion.py:permiso_denegado` (`handler403`, sin permiso);
- `templates/components/modals/modal_denegado.html`;
- `<meta name="htmx-config">` en `templates/base.html`.

## 1. Sin sesión en una vista protegida

| Petición | Respuesta |
|---|---|
| Normal | `302`, `Location: /usuarios/sesion/iniciar/?next=<ruta solicitada>` (nativo de Django) |
| `HX-Request: true` | `401`, cuerpo vacío, `HX-Redirect: /usuarios/sesion/iniciar/?next=<ruta>`, donde `<ruta>` = path y query de `HX-Current-URL` si es del mismo host (`url_has_allowed_host_and_scheme`); si no, la ruta de `LOGIN_REDIRECT_URL` |

HTMX procesa `HX-Redirect` antes de `responseHandling` y con cualquier código de estado, así que navega la página completa (verificado en `htmx_2.0.6.min.js`).

## 2. Con sesión y sin permiso

La vista lanza `PermissionDenied` (decorador `permission_required(raise_exception=True)`), que pasa por `process_exception` de los middleware (punto de enganche de la futura auditoría) y llega a `handler403`.

| Petición | Respuesta |
|---|---|
| Normal | `403`, `templates/403.html` (spec 001 FR-008b) |
| `HX-Request: true` y `HX-Target: modal_content` | `403`, `components/modals/modal_denegado.html`: título "Acceso denegado", texto "No tiene permiso para acceder a esta página. Si considera que necesita acceso, solicítelo al administrador del sistema.", un solo botón "Cerrar" (`data-bs-dismiss="modal"`), sin aside ni detalles técnicos |
| `HX-Request: true` y cualquier otro objetivo (tablas) | `403`, cuerpo vacío, `HX-Reswap: none`, `HX-Trigger: {"show_toast": {"type": "error", "message": "No tiene permiso para realizar esta operación."}}` |

## 2b. Fallo de verificación CSRF (spec §Edge Cases, CHK025)

Proveedor: `apps/usuarios/views/denegacion.py:fallo_csrf`, configurado como `CSRF_FAILURE_VIEW`.

| Petición | Respuesta |
|---|---|
| Normal | `403`, `templates/403_csrf.html` (sin cambios respecto de la feature 001) |
| `HX-Request: true` | `403`, cuerpo vacío, `HX-Refresh: true`: la página completa se recarga con un token válido o, si no hay sesión, el middleware la dirige al login |

Como HTMX procesa `HX-Refresh` antes de `responseHandling`, la regla del `403` (§3) no llega a insertar contenido. Así se evita incrustar la página completa de error CSRF en la ventana (spec FR-011).

## 3. Configuración de HTMX (`templates/base.html`)

```html
<meta name="htmx-config" content='{"responseHandling":[
  {"code":"204","swap":false},
  {"code":"[23]..","swap":true},
  {"code":"403","swap":true,"error":false},
  {"code":"[45]..","swap":false,"error":true},
  {"code":"...","swap":true}]}'>
```

Solo se añade la regla del `403`; las demás reproducen las de HTMX 2.0.6. En las tablas, `HX-Reswap: none` evita que se dibuje el cuerpo vacío.

## 4. Componente `modal_warning.html`

Se agregan los bloques `modal_footer` (por defecto: botón "Cerrar") y textos por defecto en español. Se elimina el botón de demostración "Eliminar 84 items". `modal_denegado.html` lo extiende.

## 5. Accesibilidad

- El modal conserva el `role="dialog"` del contenedor `#modal_htmx`. El cuerpo del aviso es una región `role="alert"` (título `<h3>` y mensaje), que se anuncia al insertarse. El botón "Cerrar" lleva `autofocus`: HTMX 2 enfoca el elemento con `autofocus` tras el intercambio (spec FR-011; constitución §Accesibilidad).
- El toast transversal ya usa `role="alert"` y `aria-live="assertive"` (`static/project/js/toast.js`).
