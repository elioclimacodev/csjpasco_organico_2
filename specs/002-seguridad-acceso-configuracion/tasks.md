---

description: "Lista de tareas de implementación: protección de operaciones y configuración segura"
---

# Tasks: Protección de operaciones y configuración segura

**Input**: Documentos de diseño de `specs/002-seguridad-acceso-configuracion/`

**Prerequisites**: plan.md, spec.md (con Clarifications), research.md (R1–R9), data-model.md, contracts/ (vistas-y-permisos, respuestas-acceso, variables-entorno), quickstart.md · constitución v1.1.0 · `docs/decisiones/2026-10-28-brechas-feature-001.md`

**Tests**: OBLIGATORIOS (constitución §Requisitos de testing; research R8). En cada historia, las tareas de test van antes que las de implementación y DEBEN fallar antes de implementar. Al cerrar cada historia, la suite completa (incluida la feature 001) DEBE seguir en verde.

**Organization**: Tareas agrupadas por historia de usuario (US1, US2, US4 y US3, en orden de prioridad de la spec) para que cada una sea implementable y verificable de forma independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: Historia de usuario a la que pertenece
- Cada tarea incluye la ruta exacta y la referencia (FR/SC, Rn o Contract §n) que implementa

## Restricciones que aplican a TODAS las tareas

- Sin JavaScript del proyecto: solo cabeceras HTMX nativas y `htmx-config` declarativo. Sin HTML en Python, sin `style=`, mensajes en español formal, componentes transversales de mensajes y WCAG 2.1 AA.
- Mecanismo de autenticación y autorización solo en `apps/usuarios` (Principio II, research R9): un único middleware y un único `handler403` (Principio IV). Las denegaciones usan `PermissionDenied` nativo (FR-008).
- Sin modelos, permisos ni migraciones nuevos.
- Fuera de alcance: módulo de auditoría, autorización por objeto, limpieza de apps heredadas (`apps/*_`, `apps/*__`, `apps/*___`, `apps/usuarios/views_.py`), paleta repetida, `mark_safe` en `datatable_tags.py` y `db.sqlite3`.
- Tests: `python manage.py test --noinput`; para SQLite, `DB_ENGINE=sqlite`.

---

## Phase 1: Setup (Infraestructura compartida)

- [x] T001 Convertir `apps/usuarios/tests.py` en el paquete `apps/usuarios/tests/`:
  - crear `apps/usuarios/tests/__init__.py`;
  - mover el contenido actual, sin cambios, a `apps/usuarios/tests/test_cerrar_sesion.py`;
  - eliminar `apps/usuarios/tests.py`;
  - comprobar con `python manage.py test apps.usuarios --noinput` que siguen pasando los mismos tests (plan §Project Structure).
- [x] T002 [P] Dejar `apps/ubicaciones/tests.py` preparado para los tests de US2: hoy es un stub. Reemplazar el comentario por un docstring de módulo en español y mantener el import de `TestCase` (plan §Project Structure).
- [x] T003 **BLOQUEANTE – tarea manual del Responsable Técnico, antes de T040**: generar una `SECRET_KEY` nueva con `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"` y añadirla al `.env` local, junto con `DEBUG=true` para desarrollo. No reutilizar la clave del historial de git (FR-017). Desde T040, `settings.py` la exige y la aplicación no arranca sin ella (contracts/variables-entorno.md).

---

## Phase 2: Foundational (prerrequisitos bloqueantes)

**⚠️ CRITICAL**: ninguna historia empieza sin esta fase.

- [x] T004 Añadir a `apps/common/tests/helpers.py` la matriz del contrato como **única fuente** de los tests de acceso (contracts/vistas-y-permisos.md §1–§2):
  - `KWARGS_PRUEBA = {'pk': 999999, 'pais_id': 999999, 'dpto_id': 999999, 'prov_id': 999999, 'dj_id': 999999, 'uidb64': 'x', 'token': 'y'}`.
  - `RUTAS_PUBLICAS` con las 9 rutas del contrato §1.
  - `RUTAS_SOLO_SESION = ['main:index', 'usuarios:cambiar_contrasena', 'usuarios:cambiar_contrasena_completado']`.
  - `MATRIZ_PERMISOS`: lista de tuplas `(url_name, permiso, operacion)` con las 51 rutas del contrato §2, donde `operacion` ∈ {`list`, `details`, `export`, `create`, `update`, `toggle`}.
  - `rutas_enrutadas()`: recorre `django.urls.get_resolver()` y devuelve `(url_name, kwargs)` para cada ruta con nombre, excluyendo el espacio de nombres `admin` y la ruta de `static()`.
  - `url_de_prueba(url_name, **overrides)`: construye la URL con `KWARGS_PRUEBA` filtrando los parámetros que la ruta realmente acepta.
- [x] T005 [P] Crear `apps/common/tests/fabricas.py` con funciones que crean el mínimo registro válido de cada entidad: `crear_pais`, `crear_departamento(pais)`, `crear_provincia(departamento)`, `crear_distrito(provincia)`, `crear_distrito_judicial`, `crear_sede_judicial(distrito_judicial)`, `crear_materia_jurisdiccional`, `crear_organo_jurisdiccional`, `crear_persona`. Antes de escribirlas, leer los campos obligatorios en `apps/ubicaciones/models/*.py`, `apps/organizacion/models/*.py` y `apps/personas/models.py`. Sin migraciones (data-model, "sin modelos nuevos").
- [x] T006 Test de consistencia del helper en `apps/common/tests/test_matriz_acceso.py`:
  - el conjunto `RUTAS_PUBLICAS ∪ RUTAS_SOLO_SESION ∪ {rutas de MATRIZ_PERMISOS}` es igual al conjunto de `rutas_enrutadas()`, de modo que ninguna ruta queda sin clasificar (data-model §1 I1);
  - `MATRIZ_PERMISOS` tiene 51 filas;
  - cada permiso existe en `Permission`.

**Checkpoint**: matriz y fábricas listas; las historias pueden comenzar.

---

## Phase 3: User Story 1 - Nadie opera sin sesión (Priority: P1) 🎯 MVP

**Goal**: denegación por defecto. Toda vista no pública exige sesión; las públicas están declaradas explícitamente; un fragmento HTMX sin sesión lleva la página completa al login.

**Independent Test**: sin sesión, el recorrido de todas las rutas solo deja pasar las públicas (SC-001, SC-002).

### Tests for User Story 1 (escribir primero; deben fallar) ⚠️

- [x] T007 [P] [US1] En `apps/usuarios/tests/test_acceso_global.py`:
  - **(a)** para cada ruta de `rutas_enrutadas()` que no esté en `RUTAS_PUBLICAS`, un `GET` anónimo responde `302` con `Location` que empieza por `resolve_url(settings.LOGIN_URL)` y contiene `next=` (R8-a, contracts/vistas-y-permisos.md §3 C1, FR-001, FR-005, SC-001);
  - **(b)** SC-007b: con un usuario autenticado que tiene el permiso, la misma petición a una vista protegida hace las mismas consultas con el middleware y sin él, quitándolo con `modify_settings(MIDDLEWARE={'remove': ['apps.usuarios.middleware.LoginRequiredMiddleware']})`.
- [x] T008 [P] [US1] En `apps/usuarios/tests/test_acceso_global.py`, las rutas de `RUTAS_PUBLICAS` responden sin sesión y sin redirigir al login (FR-003, SC-002):
  - `GET` a login, recuperación y registro → código distinto de `302` hacia `LOGIN_URL`;
  - `activar_cuenta` y `restablecer_contrasena_confirmar` con `uidb64` y `token` de prueba → no redirigen al login;
  - `POST` anónimo a `cerrar_sesion` → redirige a `LOGOUT_REDIRECT_URL` **sin** `next`, que es la regresión de la feature 001;
  - un `POST` válido a `usuarios:iniciar_sesion` con `?next=/ubicaciones/paises/` redirige a `/ubicaciones/paises/` (FR-005, US1-4).
- [x] T009 [P] [US1] En `apps/usuarios/tests/test_respuestas_htmx.py`, bloque "sin sesión" (contracts/respuestas-acceso.md §1, FR-012):
  - `GET` anónimo con `HX-Request: true` y `HX-Current-URL: http://testserver/organizacion/distritos-judiciales/?page=2` a `organizacion:distrito_judicial_details` → `401`, cuerpo vacío, cabecera `HX-Redirect` igual a la URL de login con `next=/organizacion/distritos-judiciales/?page=2` codificado;
  - sin `HX-Current-URL`, o con un host externo (`https://evil.example/`) → `next` igual a la ruta de `LOGIN_REDIRECT_URL`.
- [x] T010 [P] [US1] En `apps/main/tests.py`: `GET /signup/` → `404`; `reverse('main:signup')` lanza `NoReverseMatch` (FR-004).

### Implementation for User Story 1

- [x] T011 [US1] Crear `apps/usuarios/middleware.py` con `class LoginRequiredMiddleware(django.contrib.auth.middleware.LoginRequiredMiddleware)`. Sobrescribe `handle_no_permission(request, view_func)`:
  - sin `HX-Request`: comportamiento del padre;
  - con `HX-Request: true`: `HttpResponse(status=401)` con `HX-Redirect = f"{resolve_url(settings.LOGIN_URL)}?{urlencode({'next': ruta})}"`. `ruta` es el path y la query de `HX-Current-URL` si `url_has_allowed_host_and_scheme(..., allowed_hosts={request.get_host()}, require_https=request.is_secure())`; si no, `resolve_url(settings.LOGIN_REDIRECT_URL)`.
  - Docstrings en español (research R2, contracts/respuestas-acceso.md §1).
- [x] T012 [US1] Registrar `'apps.usuarios.middleware.LoginRequiredMiddleware'` en `MIDDLEWARE` de `config/settings.py`, inmediatamente después de `django.contrib.auth.middleware.AuthenticationMiddleware` (research R1).
- [x] T013 [P] [US1] En `apps/usuarios/views/acceso.py`, decorar `UsuarioLogoutView` con `@method_decorator(login_not_required, name='dispatch')`. `LogoutView` no está exenta de forma nativa (research R1, contracts/vistas-y-permisos.md §1).
- [x] T014 [P] [US1] En `apps/usuarios/views/registro.py`, decorar `registro`, `activar_cuenta` y `registro_completo` con `@login_not_required` de `django.contrib.auth.decorators` (FR-003, contrato §1).
- [x] T015 [P] [US1] Retirar `main:signup` (FR-004):
  - eliminar la función `signup` de `apps/main/views.py`;
  - eliminar la ruta de `apps/main/urls.py` y su import;
  - eliminar `apps/main/templates/main/signup.html`;
  - buscar referencias con `grep -rn "signup" apps templates config` (excluyendo las apps heredadas fuera de alcance).
- [x] T016 [US1] Retirar los `@login_required` que pasan a ser redundantes, porque el middleware ya exige sesión (research R4):
  - `apps/main/views.py:index`, `apps/organizacion/views/distrito_judicial.py:distritos_judiciales_list`, `materia_jurisdiccional.py:materias_jurisdiccionales_list`, `organo_jurisdiccional.py:organos_jurisdiccionales_list`, `apps/personas/views.py:personas_list` y `apps/usuarios/views/cuentas.py:usuarios_list`;
  - conservar `permission_required` y limpiar el import de `login_required` donde ya no se use.
- [x] T017 [US1] Ejecutar `python manage.py check` y la suite completa: T007–T010 y los tests de la feature 001 en verde.

**Checkpoint**: valida US1-1 a US1-4 y los escenarios 1–3 y 11 de quickstart.md.

---

## Phase 4: User Story 2 - Cada operación exige su permiso (Priority: P1) 🎯 MVP

**Goal**: cada una de las 51 rutas exige su permiso nativo (`view`, `add` o `change`). Las operaciones denegadas no tienen efectos. Inicio avisa a las cuentas sin permisos.

**Independent Test**: con perfiles de un solo permiso, cada operación se permite o se deniega según la matriz (SC-003, SC-004).

### Tests for User Story 2 (escribir primero; deben fallar) ⚠️

- [ ] T018 [P] [US2] En `apps/usuarios/tests/test_acceso_global.py`, cobertura de permisos (contracts/vistas-y-permisos.md §3 C2, research R4):
  - para cada fila de `MATRIZ_PERMISOS`, la vista resuelta conserva la marca del decorador `permission_required` con el permiso de la fila;
  - método recomendado: comprobar con un usuario autenticado sin permisos que la ruta responde `403` y, con solo ese permiso, que no responde `403`;
  - toda ruta enrutada fuera de `RUTAS_PUBLICAS` y `RUTAS_SOLO_SESION` está en la matriz;
  - FR-008: con un middleware de prueba añadido con `modify_settings` que registra las excepciones recibidas en `process_exception`, una denegación produce `PermissionDenied`, que es el punto de enganche de la futura auditoría (research R3).
- [ ] T019 [P] [US2] En `apps/organizacion/tests.py`, matriz por entidad para distrito judicial, materia, órgano y sede (C3), usando `MATRIZ_PERMISOS` y `fabricas.py`:
  - sin permiso → `403`; con el permiso → no `403`;
  - **C4/FR-009**:
    - `POST` a `*_toggle` sin `change` → `activo` sin cambios;
    - `POST` a `*_create` sin `add` → el conteo no cambia;
    - `POST` a `*_update` sin `change` → los campos no cambian;
    - `GET` a `*_export` sin `view` → `403` y la respuesta no es `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`;
  - **C6** para `sedes_list`, `sede_create` y `sedes_export` con `dj_id` inexistente: sin `view_sedejudicial` → `403`; con el permiso → `404`.
- [ ] T020 [P] [US2] En `apps/personas/tests.py`: `personas:create` sin `add_persona` → `403` y el conteo no cambia con `POST`; con el permiso → no `403` (C3, C4).
- [ ] T021 [P] [US2] En `apps/ubicaciones/tests.py`, matriz para países, departamentos, provincias y distritos (C3), con C4 igual que T019 y C6:
  - `departamentos_*` con `pais_id` inexistente, `provincias_*` con `dpto_id` inexistente y `distritos_*` con `prov_id` inexistente;
  - sin el permiso de la entidad de la ruta → `403`; con el permiso → `404`;
  - **sin exigir el permiso de la entidad padre** (decisión CHK003).
- [ ] T022 [P] [US2] En `apps/common/tests/test_menu_checks.py`: para cada ítem del registro real con `url_name`, sus `permissions` coinciden con el permiso de `MATRIZ_PERMISOS` para esa ruta (C5, FR-010, SC-008).
- [ ] T023 [P] [US2] En `apps/main/tests.py`, aviso de cuenta sin permisos (FR-003a, SC-007a, SC-007b):
  - un usuario sin permisos ve "Su cuenta aún no tiene permisos asignados. Solicítelos al administrador del sistema." con `role="status"`, y la respuesta usa la plantilla `components/alerts/aviso_persistente.html` (`assertTemplateUsed`);
  - con un permiso directo, con un permiso por grupo o como superusuario, no lo ve;
  - SC-007b: para un usuario sin permisos, tras renderizar Inicio, `assertNumQueries(0)` al llamar a `user.get_all_permissions()`, porque el menú lateral ya cargó la caché. Además, Inicio hace las mismas consultas con y sin la variable `cuenta_sin_permisos`, comparando el mismo usuario con `mock.patch` sobre el cálculo.

### Implementation for User Story 2

Patrón común (research R4 y R5): `@permission_required('<app>.<acción>_<modelo>', raise_exception=True)` como **decorador más externo**, con los permisos de contracts/vistas-y-permisos.md §2.

- [ ] T024 [P] [US2] `apps/organizacion/views/distrito_judicial.py`: `distrito_judicial_create` (`add_distritojudicial`), `distrito_judicial_details` y `distritos_judiciales_export` (`view_distritojudicial`), `distrito_judicial_update` y `distrito_judicial_toggle` (`change_distritojudicial`).
- [ ] T025 [P] [US2] `apps/organizacion/views/materia_jurisdiccional.py`: create (`add_materiajurisdiccional`), details y export (`view_materiajurisdiccional`), update y toggle (`change_materiajurisdiccional`).
- [ ] T026 [P] [US2] `apps/organizacion/views/organo_jurisdiccional.py`: create (`add_organojurisdiccional`), details y export (`view_organojurisdiccional`), update y toggle (`change_organojurisdiccional`).
- [ ] T027 [P] [US2] `apps/organizacion/views/sede_judicial.py`: `sedes_list`, `sede_details` y `sedes_export` (`view_sedejudicial`), `sede_create` (`add_sedejudicial`), `sede_update` y `sede_toggle` (`change_sedejudicial`).
- [ ] T028 [P] [US2] `apps/personas/views.py`: `persona_create` (`personas.add_persona`).
- [ ] T029 [P] [US2] `apps/ubicaciones/views/paises.py`: `countries_list`, `country_details` y `countries_export` (`ubicaciones.view_pais`), `country_create` (`add_pais`), `country_update` y `country_toggle` (`change_pais`).
- [ ] T030 [P] [US2] `apps/ubicaciones/views/departamentos.py`: list, details y export (`view_departamento`), create (`add_departamento`), update y toggle (`change_departamento`).
- [ ] T031 [P] [US2] `apps/ubicaciones/views/provincias.py`: list, details y export (`view_provincia`), create (`add_provincia`), update y toggle (`change_provincia`).
- [ ] T032 [P] [US2] `apps/ubicaciones/views/distritos.py`: list, details y export (`view_distrito`), create (`add_distrito`), update y toggle (`change_distrito`).
- [ ] T033 [US2] Aviso FR-003a (research R7, constitución §Mensajes):
  - crear el componente transversal `templates/components/alerts/aviso_persistente.html` con los parámetros `tipo`, `rol` y `mensaje`, que renderiza `<div class="alert alert-{{ tipo }}" role="{{ rol|default:'status' }}">{{ mensaje }}</div>`, sin botón de cerrar y sin `style=`;
  - en `apps/main/views.py:index`, añadir al contexto `cuenta_sin_permisos = not request.user.is_superuser and not request.user.get_all_permissions()`;
  - en `apps/main/templates/main/index.html`, `{% if cuenta_sin_permisos %}{% include "components/alerts/aviso_persistente.html" with tipo="warning" mensaje="Su cuenta aún no tiene permisos asignados. Solicítelos al administrador del sistema." %}{% endif %}`.
- [ ] T034 [US2] Ejecutar `python manage.py check` y la suite completa: T018–T023 y la regresión de la feature 001 en verde.

**Checkpoint**: valida US2-1 a US2-4 y los escenarios 4–6, 8, 10 y 17 de quickstart.md.

---

## Phase 5: User Story 4 - Configuración sensible fuera del código (Priority: P1)

**Goal**: la clave secreta, la depuración, los hosts, los orígenes, las cookies y el transporte seguro se leen del entorno, con fallo explícito.

**Independent Test**: sin `SECRET_KEY` la aplicación no arranca; sin `DEBUG`, la depuración queda desactivada (SC-007, SC-006, SC-006a).

**Dependencia**: T003 (`SECRET_KEY` en el `.env` local).

### Tests for User Story 4 (escribir primero; deben fallar) ⚠️

- [ ] T035 [P] [US4] `apps/common/tests/test_entorno.py`, pruebas unitarias de `config/entorno.py` con `mock.patch.dict(os.environ, …)` (data-model §3):
  - **E1**: `''` equivale a no definida;
  - **E2**: `env_bool` acepta `true`, `false`, `1`, `0`, `sí`, `si` y `no` sin distinguir mayúsculas, y `'quizas'` → `ImproperlyConfigured` con los valores aceptados;
  - **E3**: `env_lista(' a, ,b ')` → `['a', 'b']`;
  - **E4**: `env_requerida` sin valor → `ImproperlyConfigured` cuyo mensaje contiene el nombre de la variable y "Revise el archivo .env (ver .env.example)";
  - `env_entero('-1')` y `env_entero('x')` → error.
- [ ] T036 [P] [US4] `apps/common/tests/test_entorno.py`, arranque en subproceso (`subprocess.run([sys.executable, '-c', 'import django, os; os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings"); django.setup(); from django.conf import settings; print(settings.DEBUG)'], env=…)`) con el entorno copiado y modificado (research R8-d; `load_dotenv` no sobrescribe variables presentes, research R8, CHK039):
  - `SECRET_KEY=''` → código ≠ 0 y salida con "SECRET_KEY";
  - `DEBUG=''` y `ALLOWED_HOSTS='testserver'` → imprime `False`;
  - `DEBUG='quizas'` → error con los valores aceptados;
  - `DEBUG='false'` y `ALLOWED_HOSTS=''` → error que nombra `ALLOWED_HOSTS`;
  - `SECURE_PROXY_SSL_HEADER='solo_uno'` → error.
- [ ] T037 [P] [US4] `apps/common/tests/test_entorno.py`, transporte seguro simulado (SC-006a, research R8-h), con `override_settings(SECURE_SSL_REDIRECT=True, SECURE_HSTS_SECONDS=31536000)` y un usuario autenticado:
  - `client.get(url)` → `301` a `https://`;
  - `client.get(url, secure=True)` → cabecera `Strict-Transport-Security` con `max-age=31536000`;
  - sin `override_settings` → sin redirección (desarrollo).
- [ ] T038 [P] [US4] Test de código versionado (SC-006, FR-015, FR-017): `config/settings.py` no contiene `django-insecure`, `socket.gethostbyname` ni literales de IP o puerto en `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`. Puede ir en `apps/common/tests/test_entorno.py` leyendo el archivo.

### Implementation for User Story 4

- [ ] T039 [US4] Crear `config/entorno.py`:
  - trasladar `env_requerida` desde `config/settings.py`, conservando su mensaje;
  - añadir `env_bool(nombre, por_defecto)`, `env_lista(nombre, por_defecto=())` y `env_entero(nombre, por_defecto, minimo=0)`, con las reglas E1–E4 de data-model §3: booleanos `true/false/1/0/sí/si/no`; listas separadas por comas, con espacios recortados y vacíos ignorados; mensajes en español con el nombre de la variable y "Revise el archivo .env (ver .env.example)".
- [ ] T040 [US4] Modificar `config/settings.py` según contracts/variables-entorno.md:
  - `SECRET_KEY = env_requerida('SECRET_KEY')` y `DEBUG = env_bool('DEBUG', False)`;
  - `ALLOWED_HOSTS = env_lista('ALLOWED_HOSTS')`, o `['localhost', '127.0.0.1']` si `DEBUG` y está vacía; error si está vacía sin `DEBUG`;
  - `CSRF_TRUSTED_ORIGINS = env_lista(...)`, con error si un elemento no empieza por `http://` o `https://`;
  - `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` (`True` por defecto); `SECURE_SSL_REDIRECT` (`False`); `SECURE_HSTS_SECONDS` (`0`); `SECURE_HSTS_INCLUDE_SUBDOMAINS` y `SECURE_HSTS_PRELOAD` (`False`);
  - `SECURE_PROXY_SSL_HEADER = tuple(lista)` si tiene 2 elementos, `None` si está vacía y error en otro caso;
  - retirar `import socket`, `hostname` y `local_ip`, e importar los helpers desde `config.entorno`.
- [ ] T041 [US4] Actualizar `.env.example` con todas las variables nuevas, con valores vacíos o ficticios y comentarios en español:
  - las reglas de coherencia de contracts/variables-entorno.md: orígenes HTTPS detrás de un proxy y `SECURE_SSL_REDIRECT` que exige `SECURE_PROXY_SSL_HEADER` (FR-016, FR-016a, FR-015);
  - la nota de cookies seguras para acceder por IP local en HTTP (research R6);
  - el comando para generar `SECRET_KEY`.
- [ ] T042 [US4] Ejecutar `python manage.py check` y la suite completa: T035–T038 y la regresión en verde.

**Checkpoint**: valida US4-1 a US4-4 y los escenarios 12–16 de quickstart.md.

---

## Phase 6: User Story 3 - Denegaciones claras dentro de ventanas y fragmentos (Priority: P2)

**Goal**: sin permiso, un modal muestra "Acceso denegado" con "Cerrar", accesible; una actualización de tabla muestra un toast sin alterar la tabla; un fallo CSRF en HTMX recarga la página.

**Independent Test**: con un usuario sin permiso, abrir un detalle (modal) y filtrar una tabla (toast) (SC-005).

### Tests for User Story 3 (escribir primero; deben fallar) ⚠️

- [ ] T043 [P] [US3] En `apps/usuarios/tests/test_respuestas_htmx.py`, bloque "sin permiso" (contracts/respuestas-acceso.md §2, FR-011, SC-005):
  - **modal**: `GET` con `HX-Request: true` y `HX-Target: modal_content` a `organizacion:distrito_judicial_details` sin permiso → `403` con la plantilla `components/modals/modal_denegado.html`. Contiene "Acceso denegado", el texto de spec 001 FR-008b, `role="alert"` y un único botón "Cerrar" con `autofocus` y `data-bs-dismiss="modal"`. No contiene `<aside`, el nombre del permiso ni "Eliminar".
  - **tabla**: `GET` con `HX-Target: datatable` a `organizacion:distritos_judiciales_list` sin permiso → `403`, cuerpo vacío, `HX-Reswap: none` y `HX-Trigger` JSON con `show_toast.type == 'error'` y el mensaje "No tiene permiso para realizar esta operación.".
  - **normal**: `GET` sin `HX-Request` → `403` con `403.html`, que es la regresión de la feature 001.
- [ ] T044 [P] [US3] En `apps/usuarios/tests/test_respuestas_htmx.py`, CSRF (contracts/respuestas-acceso.md §2b, CHK025): `Client(enforce_csrf_checks=True)` autenticado:
  - `POST` con `HX-Request: true` y sin token a `organizacion:distrito_judicial_toggle` → `403`, cuerpo vacío y `HX-Refresh: true`;
  - sin `HX-Request` → `403` con `403_csrf.html`.
- [ ] T045 [P] [US3] En `apps/common/tests/test_htmx_config.py` (nuevo):
  - `templates/base.html` contiene `<meta name="htmx-config"` y su `content` es JSON válido con `responseHandling` que incluye `{"code":"403","swap":true,"error":false}` antes de la regla `[45]..`;
  - `templates/components/modals/modal_warning.html` no contiene "Eliminar 84 items" ni textos en inglés y define `{% block modal_footer %}` (contracts/respuestas-acceso.md §3–§4).

### Implementation for User Story 3

- [ ] T046 [P] [US3] Refactorizar `templates/components/modals/modal_warning.html` (contracts/respuestas-acceso.md §4):
  - añadir `{% block modal_footer %}` con un único botón "Cerrar" por defecto;
  - poner textos por defecto en español en `modal_title` y `modal_content`;
  - eliminar el botón de demostración y el `aria-label="Close"` en inglés (→ "Cerrar").
  - El componente no tiene usos actuales.
- [ ] T047 [US3] Crear `templates/components/modals/modal_denegado.html`, que extiende `modal_warning.html`:
  - título "Acceso denegado" y el texto de spec 001 FR-008b, dentro de una región `role="alert"`;
  - `modal_footer` con `<button type="button" class="btn w-100" data-bs-dismiss="modal" autofocus>Cerrar</button>`;
  - sin `style=` (contracts/respuestas-acceso.md §2, §5; FR-011; CHK028).
- [ ] T048 [US3] Crear `apps/usuarios/views/denegacion.py` (research R3, contracts/respuestas-acceso.md §2 y §2b):
  - `permiso_denegado(request, exception=None)`: sin `HX-Request` → `django.views.defaults.permission_denied(request, exception)`, que renderiza `403.html`; con `HX-Request` y `HX-Target == 'modal_content'` → `render(request, 'components/modals/modal_denegado.html', status=403)`; con otro objetivo → `HttpResponse(status=403)` con `HX-Reswap: none` y `HX-Trigger` JSON `{"show_toast": {"type": "error", "message": "No tiene permiso para realizar esta operación."}}`.
  - `fallo_csrf(request, reason='')`: sin `HX-Request` → `django.views.csrf.csrf_failure(request, reason)`, que usa `403_csrf.html`; con `HX-Request` → `HttpResponse(status=403)` con `HX-Refresh: true`.
- [ ] T049 [US3] Configurar los manejadores:
  - en `config/urls.py`, `handler403 = 'apps.usuarios.views.denegacion.permiso_denegado'`;
  - en `config/settings.py`, `CSRF_FAILURE_VIEW = 'apps.usuarios.views.denegacion.fallo_csrf'`.
- [ ] T050 [US3] En `templates/base.html`, dentro de `<head>` y antes de cargar HTMX, añadir `<meta name="htmx-config" content='…'>` con el `responseHandling` de contracts/respuestas-acceso.md §3: solo se añade la regla del `403`.
- [ ] T051 [US3] Ejecutar `python manage.py check` y la suite completa: T043–T045 y la regresión en verde.

**Checkpoint**: valida US3-1 a US3-3 y los escenarios 7, 9, 11, 18 y 19 de quickstart.md.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T052 Actualizar `docs/decisiones/2026-10-28-brechas-feature-001.md` (FR-018, constitución §Gobernanza › Brechas preexistentes):
  - marcar **II.4 como cerrada** por la feature 002, con fecha y commit;
  - **ampliar III.2b** a las denegaciones de las 51 rutas y de las páginas en modal y tabla, con la tabla de cumplimiento de las 5 condiciones: origen (no hay módulo de auditoría), no ampliación (ninguna operación queda sin protección), punto de enganche (`PermissionDenied` y `process_exception`), registro (este documento y plan §Complexity Tracking) y vigencia (revisión 2027-01-31).
- [ ] T053 [P] Crear `specs/002-seguridad-acceso-configuracion/despliegue-permisos-por-grupo.md` (spec §Assumptions "Preparación del despliegue", FR-017):
  - plantilla con la lista de grupos existentes, que se obtiene con `Group.objects.values_list('name', flat=True)`, y una columna por entidad con los permisos `view`, `add` y `change` propuestos;
  - un espacio para la aprobación del Responsable Técnico, con nombre y fecha;
  - el texto del aviso a usuarios por la rotación de la clave: cierre de sesiones e invalidación de los enlaces de activación y recuperación.
- [ ] T054 [P] Auditoría con búsquedas, registrando el resultado:
  - `grep -rn "style=" templates/components/modals/modal_denegado.html templates/components/modals/modal_warning.html` → vacío;
  - `git diff --stat master -- static/project/js` → sin cambios;
  - `git grep -n "django-insecure\|socket" config/` → vacío;
  - `apps/usuarios/middleware.py` y `apps/usuarios/views/denegacion.py` no construyen HTML en Python.
- [ ] T055 Recorrer los escenarios 1–19 de `quickstart.md` con los perfiles de su §2 y registrar la evidencia en `specs/002-seguridad-acceso-configuracion/evidencias/`: `quickstart.md` con resultado por escenario, y capturas del modal de denegación, el toast y el aviso de FR-003a. Los escenarios que requieran servidor HTTPS o NVDA los ejecuta el Responsable Técnico.
- [ ] T056 Ejecutar `python manage.py check` y la suite completa en SQLite (`DB_ENGINE=sqlite`) y en PostgreSQL (con el `.env`), y registrar los totales en `specs/002-seguridad-acceso-configuracion/evidencias/suite.md` (constitución §Requisitos de testing).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sin dependencias. **T003 es manual y bloquea T040**.
- **Foundational (Fase 2)**: depende de T001. Bloquea todas las historias. T004 → T006; T005 en paralelo con T004.
- **US1 (Fase 3)**: depende de la Fase 2. T011 → T012. T013–T015 en paralelo. T016 después de T012.
- **US2 (Fase 4)**: depende de la Fase 2 y, para que los tests de anónimo no interfieran, de US1. T024–T032 en paralelo (archivos distintos).
- **US4 (Fase 5)**: depende de T003. Es independiente de US1 y US2 en código: solo toca `config/` y `.env.example`. T039 → T040.
- **US3 (Fase 6)**: depende de US2, porque las denegaciones existen gracias a `permission_required`. T046 → T047. T048 → T049. T050 es independiente.
- **Polish (Fase 7)**: depende de las historias. T052 y T053 pueden adelantarse.

### Parallel Opportunities

- Fase 2: T004 ∥ T005.
- US1: tests T007 ∥ T008 ∥ T009 ∥ T010; implementación T013 ∥ T014 ∥ T015.
- US2: tests T018–T023 en paralelo; implementación T024–T032 (9 archivos) en paralelo.
- US4: tests T035–T038 en el mismo archivo, así que se hacen en serie o en bloques; T039 → T040 → T041.
- US3: tests T043 ∥ T045 (T044 comparte archivo con T043); implementación T046 ∥ T048 ∥ T050.
- US4 puede avanzar en paralelo con US1 o US2, porque toca archivos distintos.

## Parallel Example: User Story 2

```bash
Task: "T024 permisos en apps/organizacion/views/distrito_judicial.py"
Task: "T025 permisos en apps/organizacion/views/materia_jurisdiccional.py"
Task: "T027 permisos en apps/organizacion/views/sede_judicial.py"
Task: "T029 permisos en apps/ubicaciones/views/paises.py"
Task: "T032 permisos en apps/ubicaciones/views/distritos.py"
```

## Implementation Strategy

### MVP (Fases 1–2 + US1 + US2)

1. Setup y Fundamentos, incluida la matriz única del contrato.
2. US1: denegación por defecto (cierra la exposición sin sesión).
3. US2: permisos por operación (cierra la brecha II.4).
4. **Detenerse y validar**: quickstart 1–6, 8, 10 y 17; suite en verde.

### Incremental Delivery

5. US4: configuración desde el entorno. Requiere T003.
6. US3: UX de denegaciones en modal y tabla, y CSRF en HTMX.
7. Pulido: brechas, preparación del despliegue, quickstart manual y PostgreSQL.

---

## Notes

- La matriz de `apps/common/tests/helpers.py` (T004) es la única fuente de los tests de acceso: si una ruta cambia, se actualiza ahí y en contracts/vistas-y-permisos.md.
- Antes de desplegar: aplicar la asignación de permisos aprobada (T053) y comunicar la rotación de la clave (FR-017).
- Hacer commit por fase. Detenerse en cada checkpoint.
