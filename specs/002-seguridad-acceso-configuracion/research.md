# Research: Protección de operaciones y configuración segura

**Feature**: 002-seguridad-acceso-configuracion | **Fecha**: 2026-10-29

Hechos verificados en el código instalado: Django 6.0 (`venv/Lib/site-packages/django`) y HTMX 2.0.6 (`static/libs/htmx/htmx_2.0.6.min.js`). Formato: Decisión / Justificación / Alternativas descartadas.

---

## R1. Denegación por defecto (FR-001, FR-002)

- **Decisión**: añadir a `MIDDLEWARE` un `LoginRequiredMiddleware` propio, subclase del nativo de Django (ver R2), justo después de `AuthenticationMiddleware`. Las vistas públicas se marcan explícitamente con `django.contrib.auth.decorators.login_not_required` (o con `method_decorator(login_not_required, name='dispatch')` en las clases).
- **Panel de administración** (CHK010): no se exentan sus vistas. Un anónimo pasa por el login del ERP y, ya autenticado, el admin aplica `is_staff`. Así lo recoge spec §Edge Cases.
- **Vistas ya exentas de forma nativa** (verificado):
  - `LoginView` y las cuatro `PasswordReset*View` (`contrib/auth/views.py:66, 210, 241, 248, 335`). Sus subclases del proyecto (`UsuarioLoginView`, `UsuarioPasswordReset*`) heredan la exención, porque `as_view()` copia los atributos de `dispatch`.
  - `AdminSite.login` (`contrib/admin/sites.py:414`).
- **Hay que marcar explícitamente**:
  - `UsuarioLogoutView`, porque `LogoutView` **no** está exenta (`contrib/auth/views.py:125`). Sin la marca, un cierre de sesión con la sesión expirada redirigiría a `login?next=…` y rompería `CerrarSesionTests.test_post_con_sesion_expirada_redirige_sin_error` (feature 001).
  - `registro`, `activar_cuenta` y `registro_completo` (`apps/usuarios/views/registro.py`).
- **Siguen requiriendo sesión** (correcto): `PasswordChangeView` y `PasswordChangeDoneView`, que además ya llevan `login_required` nativo, y el resto de las vistas del admin. Un anónimo que abre `/admin/` es dirigido al login del ERP y, tras autenticarse, el admin aplica su propio control (`is_staff`).
- **Fuera del alcance del middleware** (no pasan por `process_view`): los manejadores de error 404, 500 y CSRF (`views/defaults.py`, `views/csrf.py`). Los estáticos en desarrollo los sirve `StaticFilesHandler` de `runserver` antes del middleware; la ruta `static()` de `config/urls.py` usa `views.static.serve`, que **no** está exenta, pero no se usa en `runserver` y no existe con `DEBUG=False`. No se toca.
- **Justificación**: es denegación por defecto nativa (Principio II): una vista nueva queda protegida sin hacer nada, y lo público se declara junto a cada vista (FR-002). Evita depender de no olvidar un decorador en cada una de las más de 40 vistas.
- **Alternativas descartadas**: solo decoradores `@login_required` por vista (una vista nueva quedaría pública si se olvida, que es justo la brecha II.4); una lista blanca de URLs en settings (separa la declaración de la vista y es frágil ante renombres).

## R2. Fragmentos sin sesión (Q3, FR-012)

- **Hecho verificado**: HTMX sigue los `302` de forma transparente dentro del XHR, así que el login se insertaría dentro del modal. En cambio, `HX-Redirect` se procesa **antes** de `responseHandling`, con cualquier código de estado (`htmx_2.0.6.min.js`, función `jn`: `if(H(n,/HX-Redirect:/i)){…location.href=…;return}`).
- **Decisión**: `apps/usuarios/middleware.py:LoginRequiredMiddleware(django.contrib.auth.middleware.LoginRequiredMiddleware)` sobrescribe `handle_no_permission`:
  - Sin la cabecera `HX-Request`: comportamiento nativo (`302` a `LOGIN_URL?next=<ruta>`).
  - Con `HX-Request: true`: respuesta `401` vacía con `HX-Redirect: <LOGIN_URL>?next=<ruta>`. La `<ruta>` es la ruta y la consulta de la cabecera `HX-Current-URL` (la página donde está el usuario), validada con `url_has_allowed_host_and_scheme`. Si falta o no es válida, se usa `LOGIN_REDIRECT_URL`.
- **Justificación**: es la página completa la que va al login y luego vuelve donde estaba (Q3), sin JavaScript del proyecto (Principio I).
- **Alternativas descartadas**: `HX-Location` (hace una petición AJAX al login, no una navegación); `200` con un script (JavaScript del proyecto); `HX-Refresh` (recarga la página, que volvería a redirigir pero perdería el `next` explícito).

## R3. Denegaciones en fragmentos (FR-008, FR-011)

- **Hechos verificados**:
  - Las ventanas se cargan con `hx-target="#modal_content"` (14 usos) y las tablas con `hx-target="#datatable"` (6 usos). HTMX envía `HX-Target: modal_content` o `datatable`.
  - Por defecto, HTMX 2 **no dibuja** las respuestas `4xx` (`responseHandling` por defecto: `204` → no; `[23]..` → sí; `[45]..` → no y error). `HX-Trigger` sí se procesa con cualquier estado.
  - Para `PermissionDenied`, Django usa `handler403` también con `DEBUG=True`; solo el 404 y el 500 tienen páginas técnicas.
- **Decisión**:
  1. **`handler403` propio**: en `config/urls.py`, `handler403 = 'apps.usuarios.views.denegacion.permiso_denegado'`.
     - Sin `HX-Request`: renderiza `templates/403.html` (como hoy).
     - Con `HX-Target: modal_content`: renderiza `components/modals/modal_denegado.html` (estado `403`). Extiende el componente transversal `modal_warning.html`, con título "Acceso denegado", el mensaje de FR-008b de la spec 001 y un único botón "Cerrar".
     - Cualquier otro objetivo HTMX (tablas): respuesta `403` vacía con `HX-Trigger: {"show_toast": {"type": "error", "message": "No tiene permiso para realizar esta operación."}}` y `HX-Reswap: none`. La tabla conserva su contenido.
  2. **Configuración declarativa de HTMX** en `templates/base.html`: `<meta name="htmx-config">` con `responseHandling` que **dibuja el `403`** (`{"code":"403","swap":true,"error":false}`, antes de la regla `[45]..`). El resto queda igual que por defecto. Es configuración, no JavaScript del proyecto.
  3. **`modal_warning.html`**: hoy no lo usa nadie y su pie trae un botón de demostración ("Eliminar 84 items") y textos de ejemplo en inglés. Se convierte en componente reutilizable con un `{% block modal_footer %}` y textos por defecto en español.
- **Justificación**: un único punto transversal (Principio IV) que reutiliza los componentes de mensajes existentes (constitución, UI/UX). La vista sigue lanzando `PermissionDenied` nativo, que atraviesa `process_exception` de cualquier middleware: el futuro módulo de auditoría podrá engancharse sin tocar las vistas (FR-008, brecha III.2b). El código `403` se conserva para pruebas y auditoría.
- **Fallo CSRF en HTMX** (CHK025): la regla global que dibuja los `403` haría que la página completa `403_csrf.html` se insertara en la ventana. **Decisión**: `CSRF_FAILURE_VIEW = 'apps.usuarios.views.denegacion.fallo_csrf'`, que delega en `django.views.csrf.csrf_failure` para peticiones normales y, con `HX-Request`, responde `403` vacío con `HX-Refresh: true`. HTMX procesa `HX-Refresh` antes de `responseHandling` (verificado en `htmx_2.0.6.min.js`: `if(l){…location.reload();return}`), así que no se dibuja nada.
- **Accesibilidad del aviso en ventana** (CHK028): `modal_denegado.html` envuelve título y mensaje en una región `role="alert"` y pone `autofocus` en "Cerrar". HTMX 2 enfoca el elemento con `autofocus` después del intercambio.
- **Alternativas descartadas**:
  - Middleware `process_exception` que convierta `PermissionDenied` en respuesta: cortaría la cadena para otros middleware, como la futura auditoría.
  - Responder `200` en el caso de la ventana: pierde la semántica del `403`.
  - Toast también en ventanas: lo descartó la clarificación Q2 de la spec.

## R4. Autorización por vista (FR-006, FR-007)

- **Decisión**: decorador `@permission_required('<app>.<acción>_<modelo>', raise_exception=True)` en cada vista protegida, siguiendo el precedente (`usuarios_list`, listas de la feature 001). Con el middleware de R1 ya no hace falta `@login_required`; se retira de las vistas de la feature 001 por coherencia, porque el middleware ya lo garantiza y un anónimo sigue siendo redirigido. La matriz completa está en [contracts/vistas-y-permisos.md](contracts/vistas-y-permisos.md).
- **Convención**: lista, detalle y exportación → `view`; registro → `add`; modificación, inactivación y reactivación → `change` (Q2).
- **Verificación**: un test recorre el resolver y comprueba que **toda** vista enrutada no pública tiene el atributo de `permission_required`, o figura en una lista explícita de excepciones (solo `main:index`, que exige sesión pero no permiso). Además, la matriz de pruebas (R8-b) contrasta cada vista con su permiso.
- **Justificación**: es legible junto a cada vista, coincide con el precedente y Django lo soporta de forma nativa (Principio II).
- **Alternativas descartadas**: una tabla declarativa central de permisos por nombre de ruta, aplicada por middleware. Separa la regla de la vista y duplica el sistema de autorización, lo que el Principio II desaconseja como mecanismo paralelo.

## R5. Sin efectos en operaciones denegadas (FR-009)

- **Decisión**: el decorador se coloca como el más externo de la vista, así que se evalúa antes de cualquier código de la vista, incluido `get_object_or_404` y la generación del archivo de exportación. Verificado en `distrito_judicial_toggle`: `GET` muestra la confirmación y `POST` escribe; ambos exigen `change`.
- **Prueba**: para cada vista que escribe (create, update, toggle) y para la exportación, un `POST` o `GET` sin permiso no cambia la base (conteo y estado `activo` iguales) y no devuelve el contenido del archivo.

## R6. Configuración desde el entorno (FR-013–FR-017, FR-016a)

- **Decisión**: nuevo módulo `config/entorno.py` con funciones puras de lectura del entorno: `env_requerida`, trasladada desde `settings.py`, más `env_bool`, `env_lista` y `env_entero`. Una cadena vacía cuenta como "no definida", lo que también permite probar los valores por defecto aunque `.env` los defina (ver R8-d). Ante un valor inválido lanzan `ImproperlyConfigured` con un mensaje en español. `settings.py` los usa así:

| Variable | Tipo | Por defecto | Regla |
|---|---|---|---|
| `SECRET_KEY` | texto | — (obligatoria) | `env_requerida` |
| `DEBUG` | booleano | `False` | acepta `true/false/1/0/sí/no` (sin distinguir mayúsculas); otro valor → error |
| `ALLOWED_HOSTS` | lista (comas) | con `DEBUG`: `localhost,127.0.0.1`; sin `DEBUG`: obligatoria | vacía sin `DEBUG` → error |
| `CSRF_TRUSTED_ORIGINS` | lista (comas) | vacía | cada valor con esquema (`http://` o `https://`) |
| `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` | booleano | `True` | — |
| `SECURE_SSL_REDIRECT` | booleano | `False` | — |
| `SECURE_HSTS_SECONDS` | entero ≥ 0 | `0` | — |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD` | booleano | `False` | — |
| `SECURE_PROXY_SSL_HEADER` | lista de 2 (`CABECERA,valor`) | vacía (`None`) | p. ej., `HTTP_X_FORWARDED_PROTO,https`; otro número de elementos → error |

  Se retiran `import socket` y el cálculo de la IP local. `.env.example` documenta todas las variables.
- **Justificación**: la constitución (§Configuración de entorno) exige secretos fuera del código y fallo explícito. Un módulo propio mantiene `settings.py` declarativo y permite probar el parseo por separado.
- **Alternativas descartadas**: `django-environ` (dependencia nueva); dejar los helpers en `settings.py` (no se pueden importar en tests sin cargar todo el settings).
- **Nota sobre cookies seguras en desarrollo**: Chrome y Firefox tratan `localhost` como contexto seguro, así que con los valores por defecto (`True`) el login funciona en `http://localhost`. Para acceder por la IP de la red local en HTTP hay que poner `SESSION_COOKIE_SECURE=false` y `CSRF_COOKIE_SECURE=false` en el `.env` de desarrollo.

## R7. Aviso de cuenta sin permisos (FR-003a)

- **Decisión**: la vista `main:index` añade al contexto `cuenta_sin_permisos = not user.is_superuser and not user.get_all_permissions()`. `main/index.html` incluye el componente transversal `components/alerts/aviso_persistente.html` con `tipo="warning"`, `rol="status"` y el texto de FR-003a. El componente se crea en esta feature (análisis H1, constitución §Mensajes): un aviso Tabler `alert alert-{{ tipo }}` sin botón de cerrar, para avisos que duran mientras se cumpla una condición. `components/alerts/alert.html` sigue reservado a los mensajes de un solo uso de `django.contrib.messages`.
- **Costo**: `get_all_permissions` usa la caché de permisos del usuario que ya llenó el aside (`has_perms`), así que no añade consultas en el mismo request.
- **Alternativas descartadas**: un mensaje de `messages` al iniciar sesión (desaparece y no refleja el estado); una página dedicada (descartada en la clarificación).

## R8. Estrategia de pruebas

| Bloque | Qué se prueba | Archivo |
|---|---|---|
| (a) Recorrido de URLs | Todas las rutas del resolver salvo admin, estáticos y públicas (contrato). Las rutas con parámetros se prueban con valores de prueba (`pk`, `pais_id`, `dpto_id`, `prov_id` y `dj_id` = `999999`; `uidb64='x'`, `token='y'`). Son todos los parámetros enrutados, verificados con el resolver el 2026-10-29. Anónimo con `GET` → `302` a `LOGIN_URL`. Las públicas → no redirigen al login. | `apps/usuarios/tests/test_acceso_global.py` |
| (a') Cobertura de permisos | Toda vista no pública salvo `main:index` lleva `permission_required` | ídem |
| (b) Matriz de permisos | Para cada fila del contrato: sin permiso → `403`; con el permiso → distinto de `403` (con un registro creado en `setUp` cuando hace falta pk); sin efectos en escrituras y exportaciones | `apps/organizacion/tests.py`, `apps/personas/tests.py`, `apps/ubicaciones/tests.py` |
| (c) HTMX | Sin sesión con `HX-Request` → `401` + `HX-Redirect` con `next` igual a la ruta de `HX-Current-URL`; sin permiso con `HX-Target: modal_content` → `403` con `modal_denegado.html` y sin aside; con `HX-Target: datatable` → `403`, cuerpo vacío, `HX-Trigger` con `show_toast` de tipo `error` y `HX-Reswap: none` | `apps/usuarios/tests/test_respuestas_htmx.py` |
| (d) Configuración | Funciones de `config/entorno.py` (unitarias); subproceso `python -c "import django; django.setup()"` con `SECRET_KEY=''` → error; con `DEBUG=''` → `settings.DEBUG is False`. La variable se fija vacía porque `load_dotenv()` no sobrescribe las ya definidas. | `apps/common/tests/test_entorno.py` |
| (e) FR-003a | El aviso aparece con un usuario sin permisos, no aparece con un permiso ni con superusuario, y no añade consultas | `apps/main/tests.py` |
| Regresión 001 | La suite de la feature 001 sigue en verde; el menú sigue coherente con los permisos | existentes |

Bloques adicionales tras la revisión de requisitos:
- **(f) Rutas anidadas (C6)**: sin permiso → `403` aunque el padre no exista; con permiso y padre inexistente → `404`.
- **(g) CSRF en HTMX**: `Client(enforce_csrf_checks=True)` con `HX-Request` y sin token → `403` + `HX-Refresh: true`; sin `HX-Request` → `403_csrf.html`.
- **(h) Transporte seguro (SC-006a)**: con `override_settings(SECURE_SSL_REDIRECT=True, SECURE_HSTS_SECONDS=31536000)`, `client.get(url)` → `301` a `https://`; `client.get(url, secure=True)` → cabecera `Strict-Transport-Security`.
- **(i) Consultas (SC-007b)**: `assertNumQueries` sobre una vista protegida con y sin el middleware (misma cantidad), y sobre Inicio con y sin el aviso de FR-003a.

Supuesto verificado (CHK039): `load_dotenv()` no sobrescribe las variables ya presentes en el entorno, aunque estén vacías (`dotenv/main.py:105`: `if k in os.environ and not self.override: continue`; `load_dotenv` usa `override=False`). Las pruebas de arranque fijan `SECRET_KEY=''` y `DEBUG=''` en el subproceso.

Se ejecutan en SQLite y en PostgreSQL. Los tests convierten `apps/usuarios/tests.py` en paquete `apps/usuarios/tests/`, conservando los tests actuales.

## R9. Ubicación del mecanismo (Principio IV y Principio II)

- **Decisión**: el middleware (`apps/usuarios/middleware.py`) y el `handler403` (`apps/usuarios/views/denegacion.py`) viven en `apps/usuarios`, que es el módulo de autenticación y autorización del proyecto. Lo exige el Principio II: "extensión compartida y documentada, ubicada en el módulo de autenticación y autorización". La plantilla `modal_denegado.html` va en `templates/components/modals/`, junto a los componentes transversales. Los helpers de entorno van en `config/`, porque pertenecen a la configuración del proyecto.
- **Alternativa descartada**: `apps/common`. La constitución lo reserva para componentes técnicos que no pertenecen a una capacidad transversal concreta, y la autorización sí la tiene.

## Hallazgos fuera de alcance

- `django.views.static.serve` (ruta `static()`) no está exenta; no afecta a `runserver` ni a producción, pero si en el futuro se sirve `MEDIA` con `static()` habrá que marcarla.
- El panel de administración envía a los anónimos al login del ERP en lugar de al del admin. Es aceptable y queda documentado.
- La navegación HTMX hacia `#page_wrapper` solo existía en la barra superior de demostración, que la feature 001 retiró de los layouts.
