# Implementation Plan: Navegación lateral dinámica filtrada por permisos (aside Tabler 1.7.1)

**Branch**: `001-aside-navegacion-dinamica` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-aside-navegacion-dinamica/spec.md`

## Summary

Reemplazar el aside de demostración por un componente transversal único con el patrón "navbar vertical" de Tabler 1.7.1, cuyo contenido se declara en código Python por cada app (`apps/<app>/menu.py`). Un registro compartido en `apps/common` reúne esas declaraciones al arrancar y las valida con un system check. Por cada request, una función pura construye el árbol filtrado con los permisos nativos de Django (con denegación por defecto y poda de grupos vacíos) y calcula en el servidor el ítem activo. Un simple tag entrega el árbol a las plantillas del aside, que no tienen estilos inline ni JavaScript propio.

La feature incluye además:
- área de usuario con iniciales y "Cerrar sesión" por POST + CSRF;
- logo como imagen estática;
- fondo institucional con contraste AA verificado;
- retiro de la barra superior en los layouts con aside;
- protección (login + permiso de consulta) de las páginas que enlaza el menú inicial.

## Technical Context

**Language/Version**: Python 3.13 (requisito constitucional ≥ 3.12)

**Primary Dependencies**: Django 6.0; Tabler.io 1.7.1 (CSS/JS en `static/tabler/dist/`); HTMX presente en el stack y no usado por el componente; Alpine.js usado solo para cerrar con Esc el menú desplegado en pantallas pequeñas (research R15). No hay dependencias de UI nuevas. **Cambio de dependencia**: `psycopg==3` (versión 3.0, incompatible con Django 6.0, que exige ≥ 3.1.12, y sin `libpq` en Windows) se reemplaza por `psycopg[binary]==3.3.6`, que trae su propia `libpq`. Fue necesario para ejecutar la suite contra PostgreSQL (T070; research R17).

**Storage**: N/A para la feature: sin modelos ni migraciones. El motor se elige con la variable de entorno `DB_ENGINE`: `sqlite` (por defecto, solo desarrollo local) o `postgresql` (producción y validación previa al despliegue), con `DB_NAME`, `DB_USER` y `DB_PASSWORD` obligatorias (research R17).

**Testing**: `django.test.TestCase` vía `python manage.py test`. Suite obligatoria contra PostgreSQL antes de desplegar.

**Target Platform**: Servidor Linux con Django; navegadores modernos de escritorio, tablet y móvil.

**Project Type**: Aplicación web monolítica server-rendered (Django + Templates).

**Performance Goals**:
- La construcción del árbol es O(n), con n = número de ítems declarados (decenas).
- `has_perms` usa la caché de permisos por usuario de Django: 2 consultas la primera vez por request (permisos del usuario y de sus grupos), más 1 para el grupo principal.
- SC-009: como máximo 3 consultas extra (permisos del usuario, permisos de sus grupos y grupo principal), independientemente del número de ítems y verificadas con `assertNumQueries` en `test_sidebar_render.py`, y como máximo 20 ms de diferencia en el tiempo medio de respuesta (20 solicitudes con y sin aside, procedimiento en quickstart.md).

**Constraints**:
- Sin `style=` ni HTML/CSS construido en Python.
- Sin JavaScript del proyecto.
- Textos en español.
- WCAG 2.1 AA (solo tema claro).
- Valores de la paleta solo en `static/project/css/custom_color.css`.

**Scale/Scope**:
- 6 entradas iniciales (Inicio + 5) y 1 opción de usuario.
- 6 layouts afectados y 5 vistas protegidas.
- ~8 plantillas de componente y ~8 parciales de ícono.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Evaluación inicial (antes de Phase 0)

| # | Regla constitucional | Cómo se cumple | Estado |
|---|---|---|---|
| I.1 | Lógica, validación y estado en el servidor | Filtrado y estado activo calculados en `build_sidebar` a partir de `request.resolver_match` y `user.has_perms` | ✅ |
| I.2 | Sin JS del proyecto; JS de Tabler permitido | Solo `collapse`/`dropdown` de `tabler.min.js`; ningún archivo en `static/project/js/` | ✅ |
| I.3 | Preferir capacidades nativas de Django | `autodiscover_modules`, system checks, `simple_tag`, `login_required`/`permission_required`, `LogoutView` | ✅ |
| II.1 | Permisos y grupos nativos; sin mecanismos paralelos | `user.has_perms` sobre `Permission` de Django | ✅ |
| II.2 | Denegación por defecto | Hoja sin permisos y sin `visible_to_authenticated` → oculta; además lo detecta el check `common.E105` | ✅ |
| II.3 | La autenticación no basta como autorización | Las listas exigen `view_<modelo>` (FR-008a); el menú no autoriza (FR-008) | ✅ |
| II.4 | Operaciones no públicas bajo sesión | `login_required` en `index` y en las 4 listas; aside solo con sesión | ✅ (parcial: el resto de vistas es una brecha preexistente registrada en `docs/decisiones/2026-10-28-brechas-feature-001.md`) |
| II.6 | Información sensible identificada | El número de documento (username) no se muestra como dato secundario; se muestra el grupo principal (spec §Seguridad, FR-021) | ✅ |
| II.5 | Cierre de sesión seguro | POST + CSRF hacia `LogoutView` nativa | ✅ |
| III.1 | Sin borrado físico / inactivación única | No hay datos persistidos | ✅ N/A |
| III.2 | Auditoría de eventos de autenticación y de denegaciones de autorización | El cierre de sesión emite `user_logged_out` y las denegaciones se producen como `PermissionDenied` nativo, pero aún no hay módulo de auditoría | ⚠️ Brecha preexistente registrada en `docs/decisiones/2026-10-28-brechas-feature-001.md` (Complexity Tracking III.2 y III.2b) |
| IV.1 | Capacidad transversal implementada una sola vez | Registro único en `apps/common/components/menu.py`; el aside es el único menú lateral | ✅ |
| IV.2 | `apps/common` solo técnico, sin depender de módulos de negocio | `autodiscover_modules('menu')`: la dependencia va de negocio → common | ✅ |
| IV.3 | Alta cohesión: cada módulo declara lo suyo | `apps/<app>/menu.py` por app | ✅ |
| E.1 | Componentes reutilizables en `templates/components/` | `templates/components/navigation/aside/`, `templates/components/icons/` | ✅ |
| E.2 | CSS en `static/project/css/`, imágenes en `static/project/img/` | `sidebar.css`; `logo-csjpasco.svg` | ✅ |
| E.3 | Sin HTML en strings de Python | El tag devuelve datos; el marcado está en las plantillas | ✅ |
| E.4 | Sin estilos inline ni CSS desde backend | Iniciales como texto; colores en `sidebar.css`; test que busca `style=` | ✅ |
| E.5 | Terceros desde static propio con versión fija | Tabler 1.7.1 ya local; íconos copiados como parciales SVG (MIT) | ✅ |
| U.1 | Español formal | Etiquetas, `aria-label` y textos en español | ✅ |
| U.2 | WCAG 2.1 AA, teclado, foco lógico | `<nav aria-label>`, `aria-current`, íconos `aria-hidden`, foco visible, contraste calculado (research R9) | ✅ |
| U.3 | El color no es el único medio | Activo = fondo + marca lateral + negrita; insignias con texto | ✅ |
| U.4 | Paleta solo en el archivo de tokens | `sidebar.css` usa `var(--institutional-primary)`; se elimina `#f9fafb !important` de `.sidebar-custom` | ✅ |
| U.5 | Mobile first / responsive | `navbar-expand-lg` + toggler | ✅ |
| T.1 | Tests proporcionales; PostgreSQL antes de producción | Estrategia de tests abajo | ✅ |

**Resultado**: GATE superado. Hay una desviación temporal (III.2) y un alcance parcial (II.4), justificados en Complexity Tracking. Ninguna toca reglas no exceptuables sin justificación: la brecha III.2 no es una omisión de diseño sino una dependencia de una capacidad transversal que aún no existe, y la feature deja preparado el punto de enganche.

### Re-evaluación tras Phase 1 (diseño)

Se revisaron [data-model.md](data-model.md) y [contracts/](contracts/):

- El diseño no introduce modelos, APIs externas ni JS (I, III sin cambios).
- El contrato de declaración prohíbe que `menu.py` importe vistas o modelos, lo que protege IV.2.
- El check `common.E105` hace cumplir la denegación por defecto ya en la declaración (II.2).
- El contrato de plantilla prohíbe `style=` y textos en inglés y fija el marcado accesible (E.4, U.1, U.2).
- Hallazgo de diseño: el color atenuado por defecto de Tabler sobre el fondo institucional da 4.30:1 y falla AA. El diseño fija el texto en blanco 100 % (7.30:1). Queda resuelto en research R9.

**Resultado**: GATE superado sin nuevas desviaciones.

## Project Structure

### Documentation (this feature)

```text
specs/001-aside-navegacion-dinamica/
├── plan.md              # Este archivo
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── menu-declaration.md   # API Python interna de declaración por app
│   └── sidebar-template.md   # Template tag + marcado obligatorio del aside
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks; no lo crea este comando)
```

### Source Code (repository root)

```text
config/
└── settings.py                       # MODIFICAR: DATABASES según DB_ENGINE + env_requerida() (research R17)
.env.example                          # NUEVO: nombres de las variables de entorno, sin secretos
requirements.txt                      # MODIFICAR: psycopg[binary]==3.3.6

apps/
├── __init__.py                         # NUEVO: apps/ como paquete regular (descubrimiento de tests; research R16)
├── common/
│   ├── apps.py                         # MODIFICAR: ready() → autodiscover_modules('menu') + registrar checks
│   ├── checks.py                       # NUEVO: system check common.E101–E113
│   ├── components/
│   │   ├── breadcrumb.py               # (precedente, sin cambios)
│   │   └── menu.py                     # NUEVO: Badge, MenuSection, MenuItem, UserMenuItem,
│   │                                   #        MenuRegistry/registry, build_sidebar, estructuras resueltas
│   ├── templatetags/
│   │   └── navigation_tags.py          # NUEVO: {% get_sidebar as sidebar %}
│   └── tests/                          # NUEVO paquete
│       ├── __init__.py
│       ├── helpers.py                  # NUEVO: crear_usuario() con usuarios activos (research R16)
│       ├── test_menu_registry.py
│       ├── test_menu_builder.py
│       ├── test_menu_checks.py
│       ├── test_sidebar_render.py
│       └── test_error_pages.py
├── main/
│   ├── menu.py                         # NUEVO: "Inicio"
│   ├── views.py                        # MODIFICAR: @login_required en index
│   └── tests.py                        # MODIFICAR: protección de index
├── organizacion/
│   ├── menu.py                         # NUEVO: sección Organización (3 ítems)
│   ├── urls.py                         # MODIFICAR: name de la lista de órganos → organos_jurisdiccionales_list
│   ├── views/distrito_judicial.py      # MODIFICAR: protección de distritos_judiciales_list
│   ├── views/materia_jurisdiccional.py # MODIFICAR: protección de materias_jurisdiccionales_list
│   ├── views/organo_jurisdiccional.py  # MODIFICAR: protección de organos_jurisdiccionales_list
│   └── tests.py                        # MODIFICAR: 302 anónimo / 403 sin permiso / 200 con permiso
├── personas/
│   ├── menu.py                         # NUEVO: sección Personas
│   ├── views.py                        # MODIFICAR: protección de personas_list
│   └── tests.py                        # MODIFICAR
└── usuarios/
    ├── menu.py                         # NUEVO: sección Administración + opción de usuario "Cerrar sesión"
    └── tests.py                        # MODIFICAR: logout POST ok / GET no cierra

templates/
├── base.html                           # MODIFICAR: cargar project/css/sidebar.css tras custom_color.css
├── 403.html                            # NUEVO: acceso denegado (extiende layouts/base_page.html; FR-008b)
├── 404.html                            # NUEVO: página no encontrada (extiende layouts/base_page.html)
├── 500.html                            # NUEVO: autocontenido, sin aside (research R14)
├── 403_csrf.html                       # NUEVO: fallo de verificación CSRF, autocontenido (research R14)
├── components/
│   ├── icons/                          # NUEVO: home, map-pin, scale, building-bank, users, settings,
│   │                                   #        logout, external-link (.html con SVG)
│   └── navigation/aside/
│       ├── base.html                   # REESCRIBIR: aside + toggler + includes, {% get_sidebar %}
│       ├── _logo.html                  # REESCRIBIR: <img> estático
│       ├── _user.html                  # NUEVO: navbar-footer + dropup (va DESPUÉS del <nav>: orden de foco, FR-028)
│       ├── _menu.html                  # REESCRIBIR: <nav> + secciones
│       ├── _menu_item.html             # NUEVO: nivel 1
│       ├── _dropdown_item.html         # NUEVO: niveles 2–3
│       ├── _badge.html                 # NUEVO: insignia compartida por niveles (research R16)
│       ├── _external.html              # NUEVO: aviso de enlace externo compartido (research R16)
│       └── _user_options.html          # ELIMINADO en US1 (T063 adelantada; research R16)
└── layouts/
    ├── base_page.html                  # MODIFICAR: quitar include de navbar/base.html
    ├── base_list.html                  # MODIFICAR: idem
    ├── htmx_base_page.html             # MODIFICAR: idem
    ├── htmx/base_page.html             # MODIFICAR: idem
    ├── htmx/page_wrapper.html          # MODIFICAR: idem
    ├── dashboards/base_list.html       # MODIFICAR: idem
    ├── base_form copy.html             # ELIMINAR (tras verificar que no se referencia)
    └── base_page copy.html             # ELIMINAR (idem)

static/project/
├── css/
│   ├── custom_color.css                # MODIFICAR: retirar bloque .sidebar-custom (fondo #f9fafb !important)
│   └── sidebar.css                     # NUEVO: reglas del componente (consume tokens)
└── img/
    └── logo-csjpasco.svg               # NUEVO: SVG extraído de _logo.html
```

**Structure Decision**: Monolito Django existente.
- El mecanismo técnico compartido va en `apps/common/` (components, templatetags, checks), siguiendo el precedente de breadcrumbs.
- Las declaraciones de contenido van en cada módulo de negocio (`apps/<app>/menu.py`).
- La presentación va en `templates/components/` y los estilos e imágenes en `static/project/`.
- `templates/components/navigation/navbar/` se conserva sin uso en los layouts con aside.

## Estrategia de tests

| Archivo | Casos | Requisitos |
|---|---|---|
| `apps/common/tests/test_menu_registry.py` | Registro idempotente; `id` duplicado → `ImproperlyConfigured`; secciones compartidas por dos apps; `isolated()` | FR-003, US5 |
| `apps/common/tests/test_menu_builder.py` | Filtrado con 1 y con varios permisos (todos exigidos); denegación por defecto; `visible_to_authenticated`; poda de contenedores y secciones vacíos; orden `(order, label)`; `NoReverseMatch` → ítem omitido + warning (`assertLogs`); activo exacto, con comodín y más específico; un solo activo; padre abierto; sin coincidencia → nada activo; columnas; iniciales y `full_name` con fallback; anónimo → `None` | FR-005–FR-009, FR-020, FR-021, SC-002, SC-003 |
| `apps/common/tests/test_menu_checks.py` | Cada código `common.E101`–`E113` con un registro aislado; el registro real del proyecto pasa sin errores; cada permiso declarado existe en `Permission` | FR-009, SC-008 |
| `apps/common/tests/test_sidebar_render.py` | Anónimo sin `<aside`; autenticado con `<nav … aria-label="Menú principal">`; un único `aria-current="page"`; formulario de logout POST con CSRF; enlace externo con `rel="noopener"` y texto oculto; sin `style=` en los archivos de `aside/` e `icons/`; las páginas de los 6 layouts sin `<header class="navbar`; petición con `HX-Request` a una lista sin `<aside` | FR-001, FR-019, FR-024, FR-026, FR-028, FR-031, SC-007 |
| `apps/usuarios/tests.py` | POST a `cerrar_sesion` cierra la sesión y redirige a iniciar sesión; GET responde 405 y la sesión sigue; POST anónimo (sesión expirada) redirige al inicio de sesión sin error; POST sin token CSRF (`Client(enforce_csrf_checks=True)`) responde 403 con la plantilla `403_csrf.html` y la sesión sigue | FR-024, SC-004, Edge Cases |
| `apps/common/tests/test_error_pages.py` | 403 de una lista sin permiso: plantilla `403.html`, texto en español, sin nombre de permiso y con aside; 404 autenticado con aside y anónimo sin aside; `500.html` se renderiza sin contexto ni aside | FR-008b, Edge Cases |
| `apps/common/tests/test_menu_builder.py` (añadidos) | Reparto en columnas (7/3 → 3,3,1; 4/3 → 2,2); iniciales con tildes y Ñ, y username numérico; secundario = primer grupo alfabético o ausente | FR-015, FR-021 |
| `apps/main/tests.py`, `apps/organizacion/tests.py`, `apps/personas/tests.py` | Anónimo → 302 a `LOGIN_URL`; autenticado sin permiso → 403; con permiso → 200 | FR-008a |

Ejecución: `python manage.py test` (SQLite en desarrollo). Antes de desplegar, la misma suite contra PostgreSQL.

## Orden sugerido de implementación (insumo para /speckit-tasks)

1. Protección de vistas y corrección del `name` de ruta de órganos (FR-008a), con sus tests.
2. `menu.py` del registro, estructuras, `build_sidebar` y tests unitarios.
3. System check, `CommonConfig.ready()` y tests del check.
4. Declaraciones `apps/<app>/menu.py` (contenido inicial).
5. Parciales de íconos, logo SVG, `sidebar.css` y limpieza de `custom_color.css`.
6. Plantillas del aside, template tag y retiro de `_user_options.html`.
7. Layouts: quitar la barra superior y eliminar las copias sobrantes.
8. Tests de render, quickstart manual (teclado, móvil, contraste) y suite completa contra PostgreSQL.

## Complexity Tracking

> Las tres filas son **brechas preexistentes** (no introducidas por esta feature), registradas y aprobadas por el Responsable Técnico en `docs/decisiones/2026-10-28-brechas-feature-001.md`, con fecha de revisión y cierre comprometido, conforme a constitución v1.1.0 §Gobernanza › Brechas preexistentes (las 5 condiciones están justificadas en ese documento).

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| **III.2 – El cierre de sesión aún no genera registro de auditoría** (brecha temporal, FR-024a) | La auditoría es una capacidad transversal que, según el Principio IV, debe implementarse una sola vez en su propio módulo, y ese módulo aún no existe. Esta feature usa `LogoutView` nativa, que emite `user_logged_out`, el punto de enganche del futuro módulo. | Crear aquí un registro de auditoría mínimo produciría una implementación parcial y duplicable que habría que rehacer, y contradice IV. Un log de aplicación no cumple la inmutabilidad ni la consulta que exige III. **Cierre previsto**: feature del módulo de auditoría (receptor de `user_logged_in/out/login_failed`). |
| **III.2b – Las denegaciones de autorización (403) aún no se auditan** (constitución §III Auditoría: "las denegaciones de autorización sobre información protegida"; spec §Seguridad, auditoría y protección de datos) | FR-008a hace que las 4 listas del menú inicial respondan 403 a usuarios sin permiso. Hoy esas páginas están abiertas, así que no existe ninguna denegación que auditar; la feature crea el evento, pero la capacidad de auditoría no existe. Las denegaciones se producen con el mecanismo nativo (`permission_required(raise_exception=True)` → `PermissionDenied` → respuesta 403), que el módulo de auditoría podrá interceptar de forma centralizada (middleware `process_exception` o `handler403`) sin tocar las vistas. | Auditar aquí exigiría crear el módulo de auditoría (mismo motivo que III.2). No proteger las vistas para evitar el evento dejaría información institucional sin control de acceso, que es un incumplimiento más grave del Principio II. **Cierre previsto**: feature del módulo de auditoría. |
| **II.4 – Protección parcial de vistas** (solo `index` y las 4 listas del menú) | Clarificación Q1 = A: la feature protege lo que enlaza el menú, para que el menú no ofrezca páginas abiertas. | Proteger todas las vistas de Organización y Personas (crear, editar, detalle, cambio de estado, exportar) multiplica el alcance y los tests; se hará en la feature de seguridad posterior. `LoginRequiredMiddleware` global afectaría vistas públicas (registro, recuperación) sin un análisis previo. |

## Notas de proceso

- **Contexto del agente**: speckit 1.2.4 (integración `claude`, scripts `ps`) no incluye un script `update-agent-context`, y el repo no tiene `CLAUDE.md`. No se modificó ningún archivo de contexto del agente. Si se desea, crear `CLAUDE.md` con `/init` en un paso aparte.
- **Hallazgos fuera de alcance**: ver la sección final de [research.md](research.md).
