# Implementation Plan: Protección de operaciones y configuración segura

**Branch**: `002-seguridad-acceso-configuracion` | **Date**: 2026-10-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-seguridad-acceso-configuracion/spec.md`

## Summary

Aplicar **denegación por defecto** a todo el ERP:
- **Sesión**: un `LoginRequiredMiddleware` propio exige sesión en toda vista que no se declare pública con `login_not_required`.
- **Permisos**: cada vista protegida exige su permiso nativo (`view`, `add` o `change`) con `permission_required(raise_exception=True)`, según una matriz explícita de 9 entidades.
- **HTMX**: un fragmento sin sesión hace que la página completa vaya al login (cabecera `HX-Redirect`). Una denegación se muestra con los componentes transversales: modal de advertencia en ventanas y toast en tablas, mediante un `handler403` único y una configuración declarativa de HTMX.
- **Configuración**: la configuración sensible (clave secreta, depuración, hosts, orígenes, cookies y transporte seguro) pasa a leerse del entorno con un módulo de lectura que falla de forma explícita.
- **Otros**: se retira `main:signup`, se añade el aviso de cuenta sin permisos en Inicio y se actualiza el registro de brechas (II.4 cerrada, III.2b ampliada).

## Technical Context

**Language/Version**: Python 3.13 (constitución: ≥ 3.12)

**Primary Dependencies**: Django 6.0 (`LoginRequiredMiddleware` y `login_not_required`, nativos desde 5.1), HTMX 2.0.6 (cabeceras `HX-Redirect`, `HX-Trigger`, `HX-Reswap` y `htmx-config`), Tabler 1.7.1, python-dotenv (ya presente). Sin dependencias nuevas.

**Storage**: sin cambios de esquema. PostgreSQL o SQLite según `DB_ENGINE` (feature 001).

**Testing**: `python manage.py test` (Django TestCase), en SQLite y en PostgreSQL.

**Target Platform**: servidor Django detrás de un proxy HTTPS en producción; `runserver` en desarrollo.

**Project Type**: monolito web server-rendered (Django + Templates + HTMX).

**Performance Goals**: sin impacto apreciable. El middleware solo consulta `request.user.is_authenticated` y `permission_required` usa la caché de permisos por request.

**Constraints**: sin JavaScript del proyecto, sin HTML en Python, mensajes en español formal, componentes transversales de mensajes y WCAG 2.1 AA.

**Scale/Scope**:
- 9 entidades y 51 rutas protegidas con permiso (Organización 24, Personas 2, Ubicaciones 24, Usuarios 1), más `main:index` (solo sesión);
- 9 rutas públicas;
- 11 variables de entorno nuevas;
- 1 middleware, 1 `handler403`, 1 plantilla de modal y un módulo de entorno.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Evaluación inicial

| # | Regla | Cómo se cumple | Estado |
|---|---|---|---|
| I.1 | Lógica, validación y estado en el servidor | Autorización en el servidor; respuestas HTMX con cabeceras nativas | ✅ |
| I.2 | Sin JS del proyecto salvo último recurso | Solo `htmx-config` (configuración declarativa) y cabeceras; `toast.js` y `modal.js` ya existentes, sin cambios | ✅ |
| I.3 | Capacidades nativas de Django primero | `LoginRequiredMiddleware`, `login_not_required`, `permission_required`, `handler403` | ✅ |
| II.1 | Toda operación no pública bajo sesión | Denegación por defecto global (R1) | ✅ (cierra la brecha II.4) |
| II.2 | Autorización explícita; la autenticación no basta | Permiso nativo por vista según la matriz (R4) | ✅ |
| II.3 | Denegación por defecto | El middleware protege toda vista no exenta; un test exige permiso en toda vista no pública salvo `main:index` | ✅ |
| II.4 | Públicas expresamente identificadas por la spec | Lista cerrada en contracts/vistas-y-permisos.md §1 = spec FR-003 | ✅ |
| II.5 | Sin mecanismos paralelos; extensión en el módulo de autenticación | Middleware y `handler403` en `apps/usuarios` (R9) | ✅ |
| III.1 | Auditoría de denegaciones | `PermissionDenied` nativo, enganchable; brecha III.2b ampliada en `docs/decisiones` | ⚠️ Brecha preexistente registrada (constitución §Brechas preexistentes) |
| IV.1 | Capacidad transversal única | Un middleware y un `handler403` para todo el sistema; sin duplicar por módulo | ✅ |
| C.1 | Secretos y configuración desde el entorno; falla explícita | `config/entorno.py` + `settings.py` (R6) | ✅ |
| C.2 | `.env` no versionado; `.env.example` sin secretos | Se actualiza `.env.example` | ✅ |
| U.1 | Español formal y componentes transversales de mensajes | `modal_warning` (componente), toast transversal, `403.html` | ✅ |
| U.2 | WCAG 2.1 AA | Aviso del modal en región `role="alert"` y `autofocus` en «Cerrar»; toast con `role="alert"`; aviso FR-003a con `role="status"` | ✅ |
| T.1 | Tests proporcionales y en PostgreSQL | Estrategia R8 | ✅ |

**Resultado**: GATE superado. III.1 es una brecha preexistente que ya estaba registrada: esta feature solo la amplía a las nuevas denegaciones y cumple las 5 condiciones de §Gobernanza › Brechas preexistentes:
- **Origen**: la capacidad de auditoría no existe.
- **No ampliación**: ninguna operación queda sin protección.
- **Enganche**: `PermissionDenied`.
- **Registro**: en `docs/decisiones`.
- **Vigencia**: revisión el 2027-01-31.

### Re-evaluación tras Phase 1

- Los contratos fijan la lista cerrada de públicas (II.4), la matriz de permisos (II.2) y las respuestas HTMX (I.2, U.1).
- **`handler403` frente a middleware**: se eligió `handler403` y no un middleware que convierta `PermissionDenied`, para no cortar la cadena de `process_exception` (III, futura auditoría).
- **Hallazgos de diseño verificados en el código**:
  - `LogoutView` no está exenta y hay que marcarla.
  - HTMX 2 no dibuja los `4xx` por defecto, de ahí la regla del `403` en `htmx-config`.
  - `HX-Redirect` y `HX-Trigger` se procesan con cualquier estado.
  - `modal_warning.html` tenía un botón de demostración y ningún uso, así que se refactoriza.

**Resultado**: GATE superado sin nuevas desviaciones.

## Project Structure

### Documentation (this feature)

```text
specs/002-seguridad-acceso-configuracion/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── vistas-y-permisos.md
│   ├── respuestas-acceso.md
│   └── variables-entorno.md
├── checklists/requirements.md
├── tasks.md                # /speckit-tasks
├── despliegue-permisos-por-grupo.md   # T053: grupos y permisos para aprobación
└── evidencias/                        # T055–T056
```

### Source Code (repository root)

```text
config/
├── entorno.py                          # NUEVO: env_requerida (trasladada), env_bool, env_lista, env_entero
├── settings.py                         # MODIFICAR: SECRET_KEY/DEBUG/ALLOWED_HOSTS/CSRF/cookies/HSTS/SSL/proxy desde el entorno;
│                                       #            sin socket; MIDDLEWARE + LoginRequiredMiddleware del proyecto; CSRF_FAILURE_VIEW
└── urls.py                             # MODIFICAR: handler403 = 'apps.usuarios.views.denegacion.permiso_denegado'
.env.example                            # MODIFICAR: variables nuevas, sin secretos

apps/
├── usuarios/
│   ├── middleware.py                   # NUEVO: LoginRequiredMiddleware (respuesta HTMX con HX-Redirect)
│   ├── views/
│   │   ├── denegacion.py               # NUEVO: permiso_denegado (handler403: página, modal o toast) y fallo_csrf (CSRF_FAILURE_VIEW: HX-Refresh en HTMX)
│   │   ├── acceso.py                   # MODIFICAR: UsuarioLogoutView con login_not_required
│   │   └── registro.py                 # MODIFICAR: registro, activar_cuenta, registro_completo con @login_not_required
│   └── tests/                          # NUEVO paquete (tests.py actual → tests/test_cerrar_sesion.py)
│       ├── __init__.py
│       ├── test_cerrar_sesion.py       # MOVIDO desde tests.py (sin cambios de contenido)
│       ├── test_acceso_global.py       # NUEVO: recorrido de URLs y cobertura de permisos
│       └── test_respuestas_htmx.py     # NUEVO: 401 + HX-Redirect, modal 403, toast 403
├── main/
│   ├── views.py                        # MODIFICAR: index con cuenta_sin_permisos; se retira signup; sin @login_required
│   ├── urls.py                         # MODIFICAR: sin ruta signup
│   ├── templates/main/index.html       # MODIFICAR: aviso FR-003a
│   ├── templates/main/signup.html      # ELIMINAR
│   └── tests.py                        # MODIFICAR: FR-003a; signup → 404
├── organizacion/views/
│   ├── distrito_judicial.py            # MODIFICAR: permission_required en create/details/update/toggle/export
│   ├── materia_jurisdiccional.py       # MODIFICAR: idem
│   ├── organo_jurisdiccional.py        # MODIFICAR: idem
│   └── sede_judicial.py                # MODIFICAR: list/create/details/update/toggle/export
├── organizacion/tests.py               # MODIFICAR: matriz de permisos y sin efectos
├── personas/views.py                   # MODIFICAR: persona_create (add_persona)
├── personas/tests.py                   # MODIFICAR
├── ubicaciones/views/{paises,departamentos,provincias,distritos}.py   # MODIFICAR: 24 vistas
├── ubicaciones/tests.py                # MODIFICAR: matriz de permisos
└── common/tests/
    ├── helpers.py                      # MODIFICAR: matriz única del contrato (T004)
    ├── fabricas.py                     # NUEVO: registros mínimos por entidad
    ├── test_matriz_acceso.py           # NUEVO: clasificación completa de rutas
    ├── test_htmx_config.py             # NUEVO: htmx-config y modal_warning
    └── test_entorno.py                 # NUEVO: config/entorno.py y arranque en subproceso

templates/
├── base.html                           # MODIFICAR: <meta name="htmx-config"> con la regla del 403
└── components/
    ├── alerts/aviso_persistente.html   # NUEVO: aviso persistente transversal (FR-003a)
    └── modals/
        ├── modal_warning.html          # MODIFICAR: bloque modal_footer, textos en español, sin demo
        └── modal_denegado.html         # NUEVO: "Acceso denegado" + botón "Cerrar"

docs/decisiones/2026-10-28-brechas-feature-001.md   # MODIFICAR: II.4 cerrada (002); III.2b ampliada
```

**Structure Decision**:
- **Mecanismo de autenticación y autorización** en `apps/usuarios`, el módulo designado (Principio II, research R9).
- **Lectura del entorno** en `config/`.
- **Componentes de presentación** en `templates/components/`.
- **Vistas protegidas**: cada vista recibe su decorador de permiso en su propio módulo.

## Estrategia de tests

Ver research R8. Resumen:
- **(a)** recorrido de todas las rutas (anónimo → login, salvo las públicas) y cobertura de `permission_required`;
- **(b)** matriz de permisos por entidad, más la comprobación de que las operaciones denegadas no tienen efectos;
- **(c)** respuestas HTMX;
- **(d)** módulo de entorno y arranque en subproceso;
- **(e)** aviso FR-003a;
- **(f)** rutas anidadas, **(g)** CSRF en HTMX, **(h)** transporte seguro simulado (SC-006a) e **(i)** conteo de consultas (SC-007b);
- regresión completa de la feature 001.

Todo se ejecuta en SQLite y en PostgreSQL.

## Orden sugerido (insumo para /speckit-tasks)

1. `config/entorno.py`, `settings.py` y `.env.example` con sus tests. Hay que actualizar el `.env` local con una `SECRET_KEY` nueva antes de ejecutar nada más.
2. Middleware, exenciones de las vistas públicas, retirada de `signup` y test de recorrido.
3. Permisos en las vistas de Organización y Personas con su matriz de tests (P1).
4. Permisos en Ubicaciones con su matriz de tests.
5. `handler403`, `modal_denegado`, `modal_warning`, `htmx-config` y tests de respuestas HTMX (P2).
6. Aviso FR-003a.
7. Registro de brechas, quickstart manual y suite en PostgreSQL.

Nota: tasks.md reordena por historias (US1, US2, US4, US3); la clave nueva queda asegurada con T003 antes de modificar `settings.py`.

## Impacto en despliegue

- **Variables obligatorias nuevas** en `.env`:
  - `SECRET_KEY`, **nueva por entorno** (FR-017), porque la del historial de git se da por comprometida;
  - `ALLOWED_HOSTS`, cuando `DEBUG` no esté activo.
- **Producción detrás de HTTPS**: activar `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS` y `SECURE_PROXY_SSL_HEADER` según contracts/variables-entorno.md.
- **Permisos en el Admin**: asignar a los grupos de usuarios los permisos `view`, `add` y `change` de cada entidad, según la lista aprobada por el Responsable Técnico (spec §Assumptions, "Preparación del despliegue"). Sin ellos, los usuarios actuales perderán acceso a las operaciones que hoy usan sin control.
- **Rotación de la clave** (FR-017): avisar a los usuarios de que deberán iniciar sesión de nuevo y de que los enlaces pendientes de activación o restablecimiento dejarán de valer.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| III.1 – Las nuevas denegaciones (403) no se auditan aún (ampliación de la brecha III.2b) | El módulo de auditoría no existe. Las denegaciones se producen con `PermissionDenied` nativo, que el futuro módulo interceptará en `process_exception` sin tocar las vistas. | Auditar aquí exigiría crear el módulo de auditoría (otra feature, Principio IV). No proteger las vistas para no generar denegaciones mantendría la brecha II.4, que es más grave. Queda registrada conforme a §Gobernanza › Brechas preexistentes. |
