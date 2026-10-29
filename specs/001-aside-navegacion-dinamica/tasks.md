---

description: "Lista de tareas de implementación: navegación lateral dinámica filtrada por permisos"
---

# Tasks: Navegación lateral dinámica filtrada por permisos (aside Tabler 1.7.1)

**Input**: Documentos de diseño de `specs/001-aside-navegacion-dinamica/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (menu-declaration.md, sidebar-template.md), quickstart.md · constitución v1.1.0 · `docs/decisiones/2026-10-28-brechas-feature-001.md`

**Tests**: OBLIGATORIOS (constitución §Requisitos de testing; plan.md §Estrategia de tests). En cada fase, las tareas de test van antes que las de implementación y DEBEN fallar antes de implementar.

**Organization**: Tareas agrupadas por historia de usuario (US1–US5 de spec.md) para que cada una sea implementable y verificable de forma independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: Historia de usuario a la que pertenece (US1…US5)
- Cada tarea incluye la ruta exacta y la referencia (FR/SC/research/contrato) que implementa

## Restricciones que aplican a TODAS las tareas

- Sin atributo `style=` en plantillas; sin HTML ni CSS construido en Python; sin JavaScript del proyecto; los colores de la paleta institucional solo en `static/project/css/custom_color.css`; textos visibles y `aria-label` en español formal.
- `apps/common` NO importa módulos de negocio; los `apps/<app>/menu.py` solo importan `apps.common.components.menu` (no vistas, modelos ni consultas a BD).
- Sin modelos ni migraciones.
- No ampliar las brechas de `docs/decisiones/2026-10-28-brechas-feature-001.md`: NO tocar las vistas de crear, editar, detalle, cambio de estado ni exportar.
- Fuera de alcance: "Personalizar" (`navbar-side` sin renderizar), tema oscuro, otras opciones del menú de usuario, módulo de auditoría, variantes `custom_color_*.css`, `apps/common/context_procesors.py`.
- Estilo de código: seguir el precedente `apps/common/components/breadcrumb.py` y `apps/common/templatetags/breadcrumb_tags.py` (docstrings y comentarios en español, dataclasses).

## Path Conventions

Monolito Django: apps en `apps/`, plantillas globales en `templates/`, estáticos del proyecto en `static/project/`. Tests en `apps/<app>/tests.py` y en el paquete `apps/common/tests/` (plan.md §Project Structure).

---

## Phase 1: Setup (Infraestructura compartida)

**Purpose**: Estructura mínima para el resto de tareas.

- [X] T001 [P] Crear el paquete de tests de common: `apps/common/tests/__init__.py` (vacío). Comprobar que `apps/common/` no tenga un `tests.py` que entre en conflicto con el paquete (plan.md §Project Structure)
- [X] T002 [P] Crear `static/project/css/sidebar.css` con un comentario de cabecera en español ("Estilos del componente aside; consume tokens de custom_color.css, no define valores de la paleta") y cargarlo en `templates/base.html` con `<link href="{% static 'project/css/sidebar.css' %}" rel="stylesheet" />` inmediatamente después de la línea de `project/css/custom_color.css` (research R8)
- [X] T003 [P] Crear el directorio `templates/components/icons/` para los parciales SVG (research R6)

---

## Phase 2: Foundational (prerrequisitos bloqueantes)

**Purpose**: Registro único del menú, construcción del árbol filtrado, validación temprana y entrega al template. Bloquea todas las historias.

**⚠️ CRITICAL**: Ninguna historia puede empezar hasta completar esta fase.

### Corrección de ruta

- [X] T004 Corregir el `name` de la ruta de lista de Órganos jurisdiccionales en `apps/organizacion/urls.py`: `path('organos-jurisdiccionales/', oj.organos_jurisdiccionales_list, name='organo_jurisdiccional_toggle')` → `name='organos_jurisdiccionales_list'`. Los usos actuales de `organizacion:organo_jurisdiccional_toggle` (`apps/organizacion/templates/organizacion/organo_jurisdiccional/partials/_table.html:36` y `apps/organizacion/views/organo_jurisdiccional.py:263`) pasan `pk` y apuntan a la ruta de cambio de estado: NO modificarlos. Volver a buscar con `grep -rn "organo_jurisdiccional_toggle"` antes de cerrar la tarea (spec §Assumptions; research R12)

### Tests de fundamentos (escribir primero; deben fallar)

- [X] T005 [P] Tests del registro en `apps/common/tests/test_menu_registry.py`: el registro es idempotente ante el mismo objeto; un `id` duplicado con distinto contenido lanza `ImproperlyConfigured`; dos "apps" registran ítems en la misma sección; `isolated()` sustituye y restaura el contenido; `sections()`, `items()` y `user_items()` son de solo lectura (data-model §1 MenuRegistry; spec FR-003, US5-2)
- [X] T006 [P] Tests de construcción del árbol en `apps/common/tests/test_menu_builder.py`, con `registry.isolated()` y usuarios con permisos asignados en `setUp`:
  - filtrado con 1 permiso y con varios permisos (se exigen todos, `has_perms`);
  - denegación por defecto (hoja sin permisos y sin `visible_to_authenticated` → oculta);
  - `visible_to_authenticated=True` → visible para todo autenticado;
  - poda de contenedores y secciones sin hijos visibles;
  - orden estable `(order, label)` entre hermanos y secciones;
  - el grupo sin sección se ubica primero;
  - `NoReverseMatch` → ítem omitido + `assertLogs('apps.common.components.menu', 'WARNING')`;
  - URL externa → `is_external=True`;
  - columnas: 7 hijos / 3 columnas → 3, 3, 1; 4 hijos / 3 columnas → 2, 2 (sin tercera);
  - superusuario ve todo;
  - usuario anónimo → `build_sidebar` devuelve `None`.

  (data-model §2–§3 reglas 1–5 y 7; spec FR-005, FR-006, FR-007, FR-009, FR-015, Edge Cases)
- [X] T007 [P] Tests del system check en `apps/common/tests/test_menu_checks.py`:
  - un caso por código con un registro aislado: `common.E101` id duplicado, `E102` url_name no resoluble o con argumentos obligatorios, `E103` url_name y url a la vez u hoja sin destino, `E104` contenedor con destino o permisos, `E105` hoja sin permisos y `visible_to_authenticated=False`, `E106` sección inexistente / etiquetas u orden distintos / hijo con `section`, `E107` profundidad > 3, `E108` plantilla de ícono inexistente, `E109` variante de Badge fuera de `{'light','warning','info'}`, `E110` `columns < 1` o `columns > 1` en hoja, `E111` url externa sin `https://`;
  - el registro real del proyecto pasa sin errores;
  - test con BD: cada permiso declarado en el registro real existe en `django.contrib.auth.models.Permission` (`app_label` + `codename`).

  (contracts/menu-declaration.md §Reglas verificadas; research R5; spec FR-009)

### Implementación de fundamentos

- [X] T008 Crear `apps/common/components/menu.py` con las estructuras declarativas `@dataclass(frozen=True)`, siguiendo literalmente data-model §1 (docstrings en español):
  - **`Badge`**: `text: str` (obligatorio, "Texto en español, no vacío") y `variant: str = 'light'`, uno de `'light'`, `'warning'`, `'info'`.
  - **`MenuSection`**: `id: str` ("Slug único global entre secciones"), `label: str` y `order: int = 100`.
  - **`MenuItem`**: `id`, `label`, `section: str | None = None` ("Solo en primer nivel"), `url_name: str | None` ("`namespace:name`, resoluble con `reverse()` sin argumentos"), `url: str | None` ("URL externa absoluta `https://…`"), `icon: str | None`, `badge: Badge | None`, `permissions: tuple[str, ...] = ()` ("se exigen todos"), `visible_to_authenticated: bool = False`, `order: int = 100`, `children: tuple[MenuItem, ...] = ()`, `columns: int = 1` ("≥ 1. Solo en ítems con hijos") y `active_patterns: tuple[str, ...] = ()` (si está vacío, equivale a `(url_name,)`).
  - **`UserMenuItem`**: `id`, `label`, `kind: Literal['link','post']`, `url_name: str`, `icon`, `permissions`, `visible_to_authenticated = False`, `order = 100` y `divider_before = False`.

  (data-model §1; spec FR-004, FR-017)
- [X] T009 Implementar `MenuRegistry` y la instancia de módulo `registry` en `apps/common/components/menu.py`:
  - `register_section`, `register_item` (solo primer nivel) y `register_user_item`, idempotentes; un `id` duplicado con contenido distinto → `ImproperlyConfigured`;
  - `sections()`, `items()` y `user_items()` de solo lectura;
  - el context manager `isolated()` para tests.

  (data-model §1 MenuRegistry; contracts/menu-declaration.md §API pública)
- [X] T010 Implementar en `apps/common/components/menu.py`:
  - las estructuras resueltas `ResolvedItem`, `ResolvedSection` y `Sidebar` (data-model §2);
  - `build_sidebar(user, request) -> Sidebar | None` con las reglas 1–5 y 7 de data-model §3: visibilidad (`visible_to_authenticated` o `permissions` no vacíos y `user.has_perms`), `reverse` con `NoReverseMatch` → omitir y `logger.warning('Menú: no se pudo resolver %s', url_name)`, visibilidad de contenedores y secciones, orden `(order, label)` y columnas con k = ⌈n/c⌉;
  - devolver `None` si `not user.is_authenticated`. Dejar en `is_active`/`is_active_parent` el valor `False` y el `UserPanel` vacío (se completan en US2 y US3). Sin HTML en Python.

  (spec FR-005–FR-009, FR-015; data-model §2–§3)
- [X] T011 Crear `apps/common/checks.py` con una función de system check (`django.core.checks.register`, tag `Tags.urls`) que valide el registro real con los códigos `common.E101`–`common.E111` y los mensajes en español del contrato; usar `django.template.loader.get_template` para E108 (contracts/menu-declaration.md §Reglas; research R5)
- [X] T012 Modificar `apps/common/apps.py`: en `CommonConfig.ready()`, `autodiscover_modules('menu')` (`django.utils.module_loading`) e importar `apps.common.checks` para registrar el check. No importar ningún módulo de negocio por nombre (research R2; constitución Principio IV)
- [X] T013 Crear `apps/common/templatetags/navigation_tags.py` con `@register.simple_tag(takes_context=True) def get_sidebar(context)`, que lee `context.get('request')` y devuelve `build_sidebar(request.user, request)` o `None` si no hay `request` o el usuario no está autenticado; docstring en español (contracts/sidebar-template.md §2; research R3)
- [X] T014 Ejecutar `python manage.py check` y `python manage.py test apps.common`: T005–T007 en verde. Con el registro todavía vacío, los casos "el registro real pasa sin errores" y "cada permiso declarado existe en `Permission`" de T007 pasan de forma trivial; se revalidan con las declaraciones reales en T037

**Checkpoint**: Registro, constructor, check y template tag listos. Las historias pueden comenzar.

---

## Phase 3: User Story 1 - Ver solo las opciones a las que tengo acceso (Priority: P1) 🎯 MVP

**Goal**: Aside real (sin demostración) con secciones y opciones filtradas por permisos, páginas destino protegidas (FR-008a) y página de acceso denegado en español (FR-008b).

**Independent Test**: Con los perfiles `sinpermisos`, `organizacion` y `admin` (quickstart §2), cada uno ve exactamente sus opciones. Una URL escrita a mano sin permiso responde 403 con la página en español.

### Tests for User Story 1 (escribir primero; deben fallar) ⚠️

- [X] T015 [P] [US1] Tests de protección de Inicio en `apps/main/tests.py`: anónimo → 302 a `settings.LOGIN_URL` (`usuarios:iniciar_sesion`); autenticado → 200 (spec FR-008a, US1-6)
- [X] T016 [P] [US1] Tests de protección en `apps/organizacion/tests.py` para `organizacion:distritos_judiciales_list`, `organizacion:materias_jurisdiccionales_list` y `organizacion:organos_jurisdiccionales_list`: anónimo → 302 a login; autenticado sin permiso → 403; con `organizacion.view_distritojudicial` / `view_materiajurisdiccional` / `view_organojurisdiccional` → 200 (spec FR-008a, US1-5)
- [X] T017 [P] [US1] Tests de protección en `apps/personas/tests.py` para `personas:list`: anónimo → 302; sin `personas.view_persona` → 403; con permiso → 200 (spec FR-008a)
- [X] T018 [P] [US1] Tests de render en `apps/common/tests/test_sidebar_render.py` (bloque US1):
  - anónimo en la página de login: la respuesta no contiene `<aside` ni `id="sidebar-menu"`;
  - autenticado: contiene `<nav` con `aria-label="Menú principal"` y el botón con `aria-label="Mostrar u ocultar el menú de navegación"`;
  - `sinpermisos`: solo "Inicio" y ningún `nav-section-title`;
  - `organizacion`: título "Organización" con "Distritos judiciales" y "Materias jurisdiccionales", sin "Órganos jurisdiccionales", "Personas" ni "Administración";
  - ningún archivo bajo `templates/components/navigation/aside/` ni `templates/components/icons/` contiene `style=`;
  - una petición con `HTTP_HX_REQUEST='true'` a `organizacion:distritos_judiciales_list` no contiene `<aside`;
  - el logo es `<img … alt="Corte Superior de Justicia de Pasco">`.

  (spec FR-001, FR-010, FR-011, FR-028, FR-031, SC-002, SC-007; contracts/sidebar-template.md §4)
- [X] T019 [P] [US1] Tests de páginas de error en `apps/common/tests/test_error_pages.py` (bloque US1) con `@override_settings(DEBUG=False)`:
  - 403 de una lista sin permiso: usa `403.html`, contiene el texto en español, NO contiene `view_` ni el nombre del permiso, contiene el aside y el enlace a `main:index`;
  - 404 autenticado: con aside; 404 anónimo: sin aside;
  - ni el 403 ni el 404 contienen "Título de la página", "Pre título" ni "Nuevo registro" (valores por defecto y acciones de demostración de `base_page.html`).

  (spec FR-008b, Edge Cases "Páginas de error"; research R14)

### Implementation for User Story 1

- [X] T020 [US1] Proteger `index` en `apps/main/views.py` con `@login_required` (`django.contrib.auth.decorators`). No modificar `signup` (spec FR-008a; research R12)
- [X] T021 [P] [US1] Proteger `distritos_judiciales_list` en `apps/organizacion/views/distrito_judicial.py` con `@login_required` + `@permission_required('organizacion.view_distritojudicial', raise_exception=True)`, igual que el precedente `apps/usuarios/views/cuentas.py:usuarios_list`. NO tocar crear, editar, detalle, cambio de estado ni exportar (spec FR-008a; docs/decisiones II.4)
- [X] T022 [P] [US1] Proteger `materias_jurisdiccionales_list` en `apps/organizacion/views/materia_jurisdiccional.py` con `@login_required` + `@permission_required('organizacion.view_materiajurisdiccional', raise_exception=True)` (spec FR-008a)
- [X] T023 [P] [US1] Proteger `organos_jurisdiccionales_list` en `apps/organizacion/views/organo_jurisdiccional.py` con `@login_required` + `@permission_required('organizacion.view_organojurisdiccional', raise_exception=True)` (spec FR-008a)
- [X] T024 [P] [US1] Proteger `personas_list` en `apps/personas/views.py` con `@login_required` + `@permission_required('personas.view_persona', raise_exception=True)`. No tocar `persona_create` (spec FR-008a)
- [X] T025 [P] [US1] Crear `apps/main/menu.py`: `MenuItem(id='inicio', label='Inicio', url_name='main:index', icon='home', visible_to_authenticated=True, order=0)` (contracts/menu-declaration.md §Ejemplo normativo; spec FR-035)
- [X] T026 [P] [US1] Crear `apps/organizacion/menu.py`: `MenuSection(id='organizacion', label='Organización', order=10)` y los ítems `distritos_judiciales` (`map-pin`, `organizacion.view_distritojudicial`, `active_patterns=('organizacion:distritos_judiciales_*','organizacion:distrito_judicial_*')`, order 10), `materias_jurisdiccionales` (`scale`, `organizacion.view_materiajurisdiccional`, `active_patterns=('organizacion:materias_jurisdiccionales_*','organizacion:materia_jurisdiccional_*')`, order 20) y `organos_jurisdiccionales` (`building-bank`, `organizacion.view_organojurisdiccional`, `active_patterns=('organizacion:organos_jurisdiccionales_*','organizacion:organo_jurisdiccional_*')`, order 30), exactamente como en el contrato. Los permisos DEBEN coincidir con los de T021–T023 (spec FR-005, FR-035)
- [X] T027 [P] [US1] Crear `apps/personas/menu.py`: `MenuSection(id='personas', label='Personas', order=20)` + `MenuItem(id='personas', url_name='personas:list', icon='users', permissions=('personas.view_persona',), active_patterns=('personas:*',), order=10)` (contrato; spec FR-035)
- [X] T028 [P] [US1] Crear `apps/usuarios/menu.py`: `MenuSection(id='administracion', label='Administración', order=90)` + `MenuItem(id='usuarios', label='Usuarios', url_name='usuarios:list', icon='settings', permissions=('usuarios.view_usuario',), order=10)`. La opción de usuario "Cerrar sesión" se añade en US3 (contrato; spec FR-035)
- [X] T029 [P] [US1] Crear los parciales de íconos en `templates/components/icons/`: `home.html` y `settings.html` (de `static/tabler/accordion.html`), `map-pin.html`, `scale.html`, `building-bank.html` y `external-link.html` (de `static/tabler/icons.html`), `users.html` (de `static/tabler/avatars.html`) y `logout.html` (de `static/tabler/dropdowns.html`). Cada uno:
  - empieza con `{# Tabler Icons (MIT) – <nombre> – copiado de Tabler 1.7.1, static/tabler/<archivo>.html #}`;
  - es el `<svg>` original con `class="icon"`, `aria-hidden="true"` y `focusable="false"`;
  - no lleva `style=`.

  Antes de copiar `scale`, confirmar que es el ícono `scale` y no una variante (`scale-outline`) (research R6)
- [X] T030 [P] [US1] Extraer el SVG del logo de `templates/components/navigation/aside/_logo.html` a `static/project/img/logo-csjpasco.svg` (archivo SVG válido con `xmlns`) y reescribir `_logo.html` como `<div class="navbar-brand navbar-brand-autodark"><a href="{% url 'main:index' %}"><img src="{% static 'project/img/logo-csjpasco.svg' %}" width="110" height="32" alt="Corte Superior de Justicia de Pasco" class="navbar-brand-image"></a></div>`, sin `bg-primary` (research R7; spec FR-011)
- [X] T031 [US1] Reescribir `templates/components/navigation/aside/base.html` según contracts/sidebar-template.md §3:
  - `{% load static navigation_tags %}{% get_sidebar as sidebar %}{% if sidebar %}`;
  - `<aside class="navbar navbar-vertical navbar-expand-lg sidebar-institucional" data-bs-theme="dark">`, sin `bg-primary` ni `sidebar-custom`;
  - el botón toggler con `aria-label="Mostrar u ocultar el menú de navegación"`;
  - `{% include '…/_logo.html' %}` y `{% include '…/_menu.html' %}`;
  - quitar el include de `_user_options.html`.

  Los layouts siguen incluyendo este archivo sin cambios (spec FR-001, FR-010, FR-034)
- [X] T032 [P] [US1] Reescribir `templates/components/navigation/aside/_menu.html`:
  - `<nav class="collapse navbar-collapse" id="sidebar-menu" aria-label="Menú principal"><ul class="navbar-nav pt-lg-3">`;
  - por cada sección, `<li class="nav-section-title">` solo si `section.label`, seguido de `{% include '…/_menu_item.html' %}` por ítem;
  - un comentario de plantilla que indique que `navbar-side` está reservado y no se renderiza.

  (contracts/sidebar-template.md §3; spec FR-012, FR-022)
- [X] T033 [P] [US1] Crear `templates/components/navigation/aside/_menu_item.html` (nivel 1) según la tabla del contrato:
  - hoja: `nav-item` + `nav-link` + `nav-link-icon` + `nav-link-title` + insignia `badge badge-sm sidebar-badge-{{ variant }} ms-auto`;
  - contenedor: `nav-item dropdown` + `dropdown-toggle` con `data-bs-toggle="dropdown" data-bs-auto-close="false" role="button"` + `dropdown-menu` con `dropdown-menu-columns`/`dropdown-menu-column` por columna, incluyendo `_dropdown_item.html`;
  - externo: `target="_blank" rel="noopener"` + ícono `external-link` + `<span class="visually-hidden">(se abre en una pestaña nueva)</span>`.

  (spec FR-013, FR-014, FR-015, FR-017, FR-018, FR-019)
- [X] T034 [P] [US1] Crear `templates/components/navigation/aside/_dropdown_item.html` (niveles 2–3):
  - hoja: `dropdown-item` con ícono opcional `dropdown-item-icon` e insignia;
  - contenedor (solo nivel 2): `dropend` + `dropdown-item dropdown-toggle` con `data-bs-auto-close="false"` + `dropdown-menu` con los hijos de nivel 3;
  - el mismo tratamiento de enlaces externos que T033.

  (spec FR-016, FR-018, FR-019; contrato)
- [X] T035 [P] [US1] Crear `templates/403.html`, que extiende `layouts/base_page.html`, con un título y un mensaje en español formal: "No tiene permiso para acceder a esta página. Si considera que necesita acceso, solicítelo al administrador del sistema." Incluye el enlace "Volver a Inicio" (`{% url 'main:index' %}`), sin nombre del permiso ni detalles técnicos. Sobrescribir `{% block page_header %}` con un encabezado propio (`<h2 class="page-title">Acceso denegado</h2>`), porque el manejador 403 no pasa `title` y `base_page.html` mostraría "Título de la página", "Pre título" y acciones de demostración (spec FR-008b; research R14)
- [X] T036 [P] [US1] Crear `templates/404.html`, que extiende `layouts/base_page.html`, con el mensaje en español formal "La página solicitada no existe o ha sido movida." y un enlace a Inicio. Sobrescribir `{% block page_header %}` con `<h2 class="page-title">Página no encontrada</h2>`, por el mismo motivo que T035 (spec Edge Cases "Páginas de error"; research R14)
- [X] T037 [US1] Ejecutar `python manage.py check` y `python manage.py test apps.common apps.main apps.organizacion apps.personas`: T015–T019 y el test de permisos existentes de T007 en verde

**Checkpoint**: US1 funcional. Valida los escenarios de aceptación US1-1 a US1-6 y los escenarios 1–4 y 12 de quickstart.md.

---

## Phase 4: User Story 2 - Saber dónde estoy (Priority: P1)

**Goal**: Una sola opción marcada como actual, calculada en el servidor (incluidas las páginas secundarias), con su desplegable padre abierto.

**Independent Test**: En la lista de Distritos judiciales y en el detalle de un distrito, "Distritos judiciales" es la única opción con `aria-current="page"`. En una página sin opción asociada no hay ninguna.

### Tests for User Story 2 (escribir primero; deben fallar) ⚠️

- [ ] T038 [P] [US2] Tests de estado activo en `apps/common/tests/test_menu_builder.py` (bloque US2), con registro aislado y un `request` de `RequestFactory` con `resolver_match` simulado:
  - una coincidencia exacta gana a un comodín;
  - entre comodines gana el patrón más largo;
  - si persiste el empate, gana el primero en el orden del menú;
  - como máximo una hoja con `is_active=True`;
  - los ancestros reciben `is_active_parent=True`;
  - sin coincidencia o sin `resolver_match` → nada activo;
  - `active_patterns` vacío equivale a `(url_name,)`.

  (spec FR-020, SC-003; data-model §3 regla 6; research R4)
- [ ] T039 [P] [US2] Tests de render en `apps/common/tests/test_sidebar_render.py` (bloque US2):
  - en `organizacion:distritos_judiciales_list` y en `organizacion:distrito_judicial_details` (con un registro creado en `setUp`), el HTML del aside contiene exactamente un `aria-current="page"`, en el enlace "Distritos judiciales";
  - en una página sin opción asociada, cero ocurrencias;
  - con un registro aislado que tenga un contenedor, el padre de la hoja activa tiene `active`, `show` y `aria-expanded="true"`.

  (spec US2-1 a US2-4, FR-020, SC-003)

### Implementation for User Story 2

- [ ] T040 [US2] Implementar la regla 6 de data-model §3 en `build_sidebar` (`apps/common/components/menu.py`):
  - comparar `request.resolver_match.view_name` con `fnmatch` contra los `active_patterns` (o `(url_name,)`) de las hojas visibles;
  - aplicar la precedencia de spec FR-020;
  - marcar `is_active` en la hoja ganadora e `is_active_parent` en sus ancestros.
- [ ] T041 [US2] Añadir el marcado de estado en `templates/components/navigation/aside/_menu_item.html` y `_dropdown_item.html`:
  - hoja activa: clase `active` y `aria-current="page"`;
  - contenedor con `is_active_parent`: `active` en el `li`, `show` en el toggle y en `dropdown-menu`, y `aria-expanded="{{ item.is_active_parent|yesno:'true,false' }}"`.

  (contracts/sidebar-template.md §3, tablas nivel 1 y niveles 2–3; spec FR-020)
- [ ] T042 [US2] Ejecutar `python manage.py test apps.common`: T038–T039 en verde

**Checkpoint**: US1 y US2 funcionan. Valida los escenarios US2-1 a US2-4 y el escenario 5 de quickstart.md.

---

## Phase 5: User Story 3 - Identificarme y cerrar sesión de forma segura (Priority: P1)

**Goal**: Área de usuario al final del aside con iniciales, nombre y grupo principal, y "Cerrar sesión" por POST + CSRF.

**Independent Test**: El área de usuario muestra los datos reales del usuario (sin número de documento como dato secundario). "Cerrar sesión" termina la sesión; un GET no la termina.

### Tests for User Story 3 (escribir primero; deben fallar) ⚠️

- [ ] T043 [P] [US3] Tests de `UserPanel` en `apps/common/tests/test_menu_builder.py` (bloque US3):
  - `full_name` = `get_full_name()` o, si está vacío, `get_username()`;
  - iniciales: "Ángel Núñez" → "ÁN"; "Ñuflo" → "ÑU"; se ignoran los caracteres no alfanuméricos iniciales; un username numérico sin nombre → sus 2 primeros dígitos;
  - `secondary` = el primer grupo en orden alfabético, o `None` sin grupos, y nunca el username;
  - las opciones de usuario se filtran y ordenan como los ítems.

  (spec FR-021, FR-025, Edge Cases; research R10; data-model §2 UserPanel)
- [ ] T044 [P] [US3] Tests de cierre de sesión en `apps/usuarios/tests.py`:
  - POST a `usuarios:cerrar_sesion` → sesión cerrada y redirección a `usuarios:iniciar_sesion`;
  - GET → 405 y la sesión sigue activa;
  - POST como anónimo (sesión expirada) → redirección al inicio de sesión sin error.

  (spec FR-024, FR-024a, SC-004, Edge Cases; research R14)
- [ ] T045 [P] [US3] Tests de render en `apps/common/tests/test_sidebar_render.py` (bloque US3):
  - `class="navbar-footer"` aparece DESPUÉS de `</nav>` en el HTML;
  - existe `<form method="post" action="<reverse('usuarios:cerrar_sesion')>">` con `csrfmiddlewaretoken` y un botón "Cerrar sesión";
  - el menú de usuario tiene una sola opción;
  - el disparador tiene `aria-label="Menú de usuario de <nombre completo>"`;
  - con un usuario en un grupo se muestra el nombre del grupo y el username (número de documento) no aparece como dato secundario;
  - con un usuario sin grupos no hay dato secundario.

  (spec FR-021, FR-023, FR-024, FR-028; contracts/sidebar-template.md §3–§4)

### Implementation for User Story 3

- [ ] T046 [US3] Completar en `apps/common/components/menu.py` el `UserPanel` y `ResolvedUserItem`:
  - `full_name` con fallback;
  - `secondary = user.groups.order_by('name').values_list('name', flat=True).first()`;
  - `initials` según research R10: `str.upper()`, conservando tildes y Ñ, ignorando los caracteres no alfanuméricos iniciales, y con los 2 primeros dígitos si el username es numérico;
  - resolución, filtrado y orden de `UserMenuItem` con las mismas reglas que los ítems.

  (data-model §2; spec FR-021, FR-025)
- [ ] T047 [US3] Añadir en `apps/usuarios/menu.py` la opción `UserMenuItem(id='cerrar_sesion', label='Cerrar sesión', kind='post', url_name='usuarios:cerrar_sesion', icon='logout', visible_to_authenticated=True, order=1000)` (contracts/menu-declaration.md; spec FR-023)
- [ ] T048 [US3] Crear `templates/components/navigation/aside/_user.html` según el contrato:
  - `navbar-footer` > `navbar-nav` > `nav-item dropup`;
  - el disparador `nav-link` con `data-bs-toggle="dropdown" aria-expanded="false" aria-label="Menú de usuario de {{ sidebar.user.full_name }}"`;
  - `<span class="avatar avatar-sm" aria-hidden="true">{{ sidebar.user.initials }}</span>`, el nombre y `{% if sidebar.user.secondary %}`;
  - por cada opción: `kind == 'post'` → `<form method="post" action="{{ item.href }}">{% csrf_token %}<button type="submit" class="dropdown-item">`; `kind == 'link'` → `<a class="dropdown-item">`; `divider_before` → `dropdown-divider`.

  Sin `style=` (spec FR-021, FR-024; research R10)
- [ ] T049 [US3] En `templates/components/navigation/aside/base.html`, incluir `_user.html` DESPUÉS del include de `_menu.html`, para que el orden del documento sea menú → área de usuario (spec FR-028; contracts/sidebar-template.md §3 "Orden en el documento")
- [ ] T050 [US3] Ejecutar `python manage.py test apps.common apps.usuarios`: T043–T045 en verde

**Checkpoint**: US1–US3 funcionan. Valida los escenarios US3-1 a US3-5 y los escenarios 6–8 de quickstart.md.

---

## Phase 6: User Story 4 - Usar el menú en cualquier dispositivo y solo con teclado (Priority: P2)

**Goal**: Fondo institucional con contraste AA, estado activo no cromático, foco visible, responsive desde 992 px y uso completo con teclado.

**Independent Test**: Escenarios 9, 10, 11 y 13 de quickstart.md, con sus evidencias en `specs/001-aside-navegacion-dinamica/evidencias/`.

### Tests for User Story 4 ⚠️

- [ ] T051 [P] [US4] Test en `apps/common/tests/test_sidebar_render.py` (bloque US4):
  - `static/project/css/sidebar.css` no contiene ningún valor hex de la paleta (`#A42622`, `#EAE4D2`, `#7A7562`, sin distinguir mayúsculas);
  - el `<aside>` tiene `navbar-expand-lg` y `data-bs-theme="dark"` y no tiene `bg-primary` ni `sidebar-custom`;
  - los SVG de `templates/components/icons/` tienen `aria-hidden="true"`.

  (spec FR-029, FR-030; constitución §Identidad visual)

### Implementation for User Story 4

- [ ] T052 [US4] Escribir en `static/project/css/sidebar.css` las reglas de `.sidebar-institucional`:
  - fondo con `var(--institutional-primary)`;
  - `--tblr-navbar-color` y el texto de ítems, títulos de sección, submenús, íconos y área de usuario en blanco 100 % (nunca la opacidad por defecto de Tabler: 4.30:1 falla AA);
  - ítem activo con `background-color: rgba(0,0,0,.2)`, marca lateral blanca de 3 px y `font-weight: 600`;
  - `:focus-visible` con contorno blanco de 2 px y `outline-offset`;
  - variantes `.sidebar-badge-light|warning|info`;
  - las reglas de ocultar la barra de desplazamiento trasladadas desde `.sidebar-custom` de `custom_color.css`.

  Sin valores hex de la paleta (research R8, R9; spec FR-017, FR-028, FR-030)
- [ ] T053 [US4] Verificar el comportamiento responsive con el navegador: por debajo de 992 px el menú está colapsado al cargar y el botón lo despliega, y el desplegable activo se ve abierto; desde 992 px el menú está siempre expandido. Guardar `movil-375-colapsado.png`, `movil-375-desplegado.png` y `escritorio-1280.png` en `specs/001-aside-navegacion-dinamica/evidencias/`. Si algo no se cumple, corregirlo en las plantillas o en `sidebar.css` (spec FR-010, FR-029; quickstart esc. 9)
- [ ] T054 [US4] Recorrido con teclado: orden toggler → logo → opciones → área de usuario; Enter o Espacio abren; Esc cierra y devuelve el foco; foco visible. Registrarlo en `specs/001-aside-navegacion-dinamica/evidencias/teclado.md`. Prueba con NVDA (región "Menú principal", "página actual", íconos no anunciados, aviso de enlace externo): registrarla en `evidencias/lector-pantalla.md`. Corregir las desviaciones encontradas (spec FR-028, SC-005; quickstart esc. 10–11)
- [ ] T055 [US4] Medir el contraste de todas las combinaciones (texto, títulos de sección, submenús, ítem activo, foco, insignias de cada variante, avatar y área de usuario) con DevTools o Colour Contrast Analyser, y registrar la tabla en `specs/001-aside-navegacion-dinamica/evidencias/contraste.md`. Ajustar en `sidebar.css` los colores de cualquier variante que no cumpla ≥ 4.5:1 de texto y ≥ 3:1 frente al fondo hasta que cumpla. El conjunto de variantes de spec FR-017 (neutra, advertencia e informativa) no se reduce (spec FR-017, FR-030, SC-006; research R9; quickstart esc. 13)

**Checkpoint**: Valida los escenarios US4-1 a US4-4 y los escenarios 9, 10, 11 y 13 de quickstart.md.

---

## Phase 7: User Story 5 - Incorporar opciones de un módulo sin tocar el componente (Priority: P2)

**Goal**: Demostrar que las capacidades completas del patrón (insignia, externo, columnas, dropend) se renderizan desde la declaración, y que agregar una opción solo toca el módulo.

**Independent Test**: Escenario §4 de quickstart.md y `git diff --stat` limitado al módulo.

### Tests for User Story 5 ⚠️

- [ ] T056 [P] [US5] Test en `apps/common/tests/test_sidebar_render.py` (bloque US5), con `registry.isolated()`: un ítem con insignia, uno externo, un contenedor con `columns=2` y 3 hijos, y un `dropend` de nivel 2 con hijos de nivel 3. El HTML debe contener:
  - `sidebar-badge-` con el texto de la insignia;
  - `rel="noopener"` y "(se abre en una pestaña nueva)";
  - dos `dropdown-menu-column`;
  - un `dropend` con su `dropdown-menu`.

  (spec US5-3, FR-014–FR-019)

### Implementation for User Story 5

- [ ] T057 [US5] Ejecutar el escenario §4 de quickstart.md: declarar temporalmente una opción en `apps/personas/menu.py`, ejecutar `python manage.py check`, comprobar la visibilidad con y sin el permiso y comprobar con `git diff --stat` que solo cambió el módulo. Registrarlo en `specs/001-aside-navegacion-dinamica/evidencias/extensibilidad.md` y revertir la opción temporal (spec SC-008, US5-1, US5-4)

**Checkpoint**: Las cinco historias funcionan de forma independiente.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Retiro de la barra superior, limpieza, páginas de error restantes, rendimiento y validación final.

### Tests (escribir primero; deben fallar)

- [ ] T058 [P] Test en `apps/common/tests/test_sidebar_render.py`: en páginas que usan cada uno de los 6 layouts (`layouts/base_page.html`, `base_list.html`, `htmx_base_page.html`, `htmx/base_page.html`, `htmx/page_wrapper.html` y `dashboards/base_list.html`, renderizados con un contexto mínimo con `request`), la respuesta NO contiene `<header class="navbar` ni `id="navbar-menu"` (spec FR-026, SC-007)
- [ ] T059 [P] Tests en `apps/common/tests/test_error_pages.py`: `500.html` se renderiza con `Template` sin contexto y no contiene `<aside`; contiene un enlace a `/` (spec Edge Cases; research R14). En `apps/usuarios/tests.py`: un POST a `cerrar_sesion` con `Client(enforce_csrf_checks=True)` sin token → 403 con la plantilla `403_csrf.html`, texto en español y la sesión sigue activa (spec Edge Cases; research R14)
- [ ] T060 [P] Test de rendimiento en `apps/common/tests/test_sidebar_render.py`: `assertNumQueries` sobre el render de `components/navigation/aside/base.html` para un usuario con grupo → ≤ 3 consultas, igual con 2 que con 20 ítems declarados (spec SC-009)

### Implementación y limpieza

- [ ] T061 Quitar `{% include 'components/navigation/navbar/base.html' %}` (y el comentario "Navbar" asociado) de `templates/layouts/base_page.html`, `templates/layouts/base_list.html`, `templates/layouts/htmx_base_page.html`, `templates/layouts/htmx/base_page.html`, `templates/layouts/htmx/page_wrapper.html` y `templates/layouts/dashboards/base_list.html`, sin tocar el include del aside. `templates/components/navigation/navbar/` se conserva (spec FR-026; research R11)
- [ ] T062 Buscar referencias con `grep -rn "base_form copy\|base_page copy" apps templates config`. Si no hay ninguna, eliminar `templates/layouts/base_form copy.html` y `templates/layouts/base_page copy.html`; si las hay, informarlo y no eliminar (spec FR-034)
- [X] T063 Buscar referencias a `_user_options.html` y eliminar `templates/components/navigation/aside/_user_options.html` (spec FR-033)
- [ ] T064 Eliminar de `static/project/css/custom_color.css` el bloque `.sidebar-custom` (fondo `#f9fafb !important` y las reglas de barra de desplazamiento ya trasladadas en T052). Buscar con `grep -rn "sidebar-custom" templates static/project apps` que no quedan usos (research R8; spec FR-030)
- [ ] T065 [P] Crear `templates/500.html`, autocontenido: HTML completo sin `{% extends %}`, sin template tags del proyecto ni variables de contexto, sin `style=` (puede usar `{% load static %}` para enlazar `tabler/dist/css/tabler.min.css`, que no requiere contexto), con el mensaje en español formal "Ocurrió un error interno. Inténtelo nuevamente en unos minutos." y un enlace `<a href="/">Volver a Inicio</a>` (spec Edge Cases; research R14)
- [ ] T066 [P] Crear `templates/403_csrf.html`, autocontenido: mensaje en español formal "La solicitud no pudo verificarse. Vuelva a la página anterior o regrese a Inicio e inténtelo nuevamente.", con enlaces a `{% url 'main:index' %}` y a `{% url 'usuarios:iniciar_sesion' %}` (la etiqueta `url` funciona aunque la plantilla se renderice sin `RequestContext`), sin detalles técnicos ni `style=` (spec Edge Cases; research R14)
- [ ] T067 Auditoría de restricciones con búsquedas:
  - (a) `grep -rn "style=" templates/components/navigation/aside templates/components/icons templates/403.html templates/404.html templates/500.html templates/403_csrf.html` → vacío;
  - (b) textos en inglés y enlaces `.html` de demostración en `templates/components/navigation/aside/` → ninguno;
  - (c) valores de la paleta (`A42622`, `EAE4D2`, `7A7562`) fuera de `static/project/css/custom_color*.css` → ninguno nuevo;
  - (d) `apps/common/` sin `import apps.(main|organizacion|personas|usuarios|ubicaciones|configuracion)`;
  - (e) los `apps/*/menu.py` solo importan `apps.common.components.menu`;
  - (f) `git diff --stat master -- static/project/js` → sin cambios, y `grep -rn "<script" templates/components/navigation/aside templates/components/icons` → vacío.

  (spec FR-027, FR-031, FR-032, SC-007; constitución)
- [ ] T068 Medición de carga según el escenario 14 de quickstart.md (20 + 20 solicitudes a `/organizacion/distritos-judiciales/`) y registro en `specs/001-aside-navegacion-dinamica/evidencias/rendimiento.md` (diferencia ≤ 20 ms) (spec SC-009)
- [ ] T069 Ejecutar `python manage.py check` y la suite completa `python manage.py test` (SQLite, desarrollo): todo en verde
- [ ] T070 Ejecutar la suite completa contra PostgreSQL (configurando la base de datos de prueba por variables de entorno, sin credenciales en archivos versionados) y registrar el resultado en `specs/001-aside-navegacion-dinamica/evidencias/postgresql.md`. Es obligatorio antes de desplegar (constitución §Requisitos de testing)
- [ ] T071 Recorrer todos los escenarios de quickstart.md (1–14) con los perfiles de §2 y completar las evidencias de §"Evidencia que se conserva" (quickstart.md)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: depende de Setup. **Bloquea todas las historias.** T004 (ruta) es independiente del resto de la fase. T008 → T009 → T010 (mismo archivo, en orden). T011 depende de T008–T009. T012 depende de T011. T013 depende de T010.
- **US1 (Phase 3)**: depende de Phase 2. Es el MVP.
- **US2 (Phase 4)**: depende de Phase 2 y, para los tests de render (T039), de las declaraciones y plantillas de US1 (T026, T031–T034).
- **US3 (Phase 5)**: depende de Phase 2 y, para el render (T045, T049), de `aside/base.html` de US1 (T031). T047 modifica `apps/usuarios/menu.py`, creado en T028.
- **US4 (Phase 6)**: depende de US1–US3, porque los estilos y las verificaciones cubren el menú y el área de usuario.
- **US5 (Phase 7)**: depende de US1 (plantillas) y US2 (marcado de estado).
- **Polish (Phase 8)**: depende de las historias deseadas. T064 depende de T052. T061 puede adelantarse tras US1 si se quiere ver el aside sin la barra superior durante el desarrollo.

### User Story Dependencies

- **US1 (P1)**: solo de Fundamentos.
- **US2 (P1)**: lógica (T040) independiente; marcado y render sobre las plantillas de US1.
- **US3 (P1)**: lógica (T046) independiente; render sobre `aside/base.html` de US1.
- **US4 (P2)** y **US5 (P2)**: sobre las plantillas de US1–US3.

### Within Each User Story

- Tests primero (DEBEN fallar) → declaraciones y lógica → plantillas → ejecución de la suite de la historia.
- No avanzar a la siguiente prioridad sin pasar el checkpoint.

### Parallel Opportunities

- Phase 1: T001, T002 y T003 en paralelo.
- Phase 2: T004 en paralelo con T005–T007 (tests en archivos distintos).
- US1: los tests T015–T019 en paralelo; protección de vistas T021–T024 en paralelo (archivos distintos; T020 también); declaraciones T025–T028 en paralelo; T029, T030 y T032–T036 en paralelo; T031 después de T030 y T032.
- US2: T038 ∥ T039. US3: T043 ∥ T044 ∥ T045. Polish: T058 ∥ T059 ∥ T060; T065 ∥ T066.
- Una vez completada la Fase 2, la lógica de US2 (T040) y de US3 (T046) puede avanzar en paralelo con las plantillas de US1, porque `menu.py` se edita en bloques distintos. Coordinar si trabaja más de una persona sobre el mismo archivo.

---

## Parallel Example: User Story 1

```bash
# Tests de US1 en paralelo:
Task: "T015 Tests de protección de Inicio en apps/main/tests.py"
Task: "T016 Tests de protección de las 3 listas en apps/organizacion/tests.py"
Task: "T017 Tests de protección en apps/personas/tests.py"
Task: "T018 Tests de render US1 en apps/common/tests/test_sidebar_render.py"
Task: "T019 Tests 403/404 en apps/common/tests/test_error_pages.py"

# Protección de vistas en paralelo:
Task: "T021 distritos_judiciales_list en apps/organizacion/views/distrito_judicial.py"
Task: "T022 materias_jurisdiccionales_list en apps/organizacion/views/materia_jurisdiccional.py"
Task: "T023 organos_jurisdiccionales_list en apps/organizacion/views/organo_jurisdiccional.py"
Task: "T024 personas_list en apps/personas/views.py"

# Declaraciones y recursos en paralelo:
Task: "T025 apps/main/menu.py"  ·  "T026 apps/organizacion/menu.py"  ·  "T027 apps/personas/menu.py"  ·  "T028 apps/usuarios/menu.py"
Task: "T029 parciales de íconos en templates/components/icons/"  ·  "T030 logo en static/project/img/logo-csjpasco.svg"
```

## Parallel Example: User Story 3

```bash
Task: "T043 Tests de UserPanel en apps/common/tests/test_menu_builder.py"
Task: "T044 Tests de cierre de sesión en apps/usuarios/tests.py"
Task: "T045 Tests de render del área de usuario en apps/common/tests/test_sidebar_render.py"
```

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2 + US1)

1. Completar Phase 1 (Setup).
2. Completar Phase 2 (Fundamentos). Es crítica porque bloquea todas las historias.
3. Completar Phase 3 (US1): menú real filtrado, vistas protegidas y 403 en español.
4. **DETENERSE Y VALIDAR**: escenarios US1-1 a US1-6 y quickstart 1–4 y 12.
5. Opcional: adelantar T061 (retirar la barra superior) para la demostración.

### Incremental Delivery

1. Setup + Fundamentos → base lista.
2. US1 → validar → demo (MVP).
3. US2 (estado activo) → validar.
4. US3 (área de usuario y cierre de sesión) → validar.
5. US4 (estilos, accesibilidad y responsive, con evidencias) → validar.
6. US5 (extensibilidad) → validar.
7. Polish (barra superior, limpieza, 500/403_csrf, rendimiento, PostgreSQL).

### Parallel Team Strategy

Con varias personas, después de la Fase 2: A → plantillas y declaraciones de US1; B → lógica de activo (T038, T040); C → lógica de UserPanel y tests de cierre de sesión (T043, T044, T046). Se integran en los checkpoints de US2 y US3.

---

## Notes

- [P] = archivos distintos y sin dependencias pendientes.
- [USn] = trazabilidad con la historia de spec.md.
- Verificar que los tests fallen antes de implementar.
- Hacer commit por tarea o por grupo lógico; detenerse en cada checkpoint para validar la historia de forma independiente.
- Evitar tareas vagas, conflictos en el mismo archivo y dependencias entre historias que rompan la independencia.
- Desviación respecto del prompt de entrada: `build_sidebar` se implementa en la Fase 2 con las reglas de filtrado, resolución, poda, orden y columnas. El cálculo del estado activo (regla 6) se implementa en US2 y el `UserPanel` en US3, para que sus tests puedan fallar primero, como exige el TDD de cada historia.
