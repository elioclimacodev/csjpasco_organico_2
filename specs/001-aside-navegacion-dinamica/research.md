# Research: Navegación lateral dinámica filtrada por permisos

**Feature**: 001-aside-navegacion-dinamica | **Fecha**: 2026-10-28

Cada decisión resuelve una incógnita del plan. Formato: Decisión / Justificación / Alternativas descartadas.

---

## R1. Dónde se declara el menú: código versionado vs. base de datos

- **Decisión**: Declaración en código Python versionado, mediante estructuras inmutables (dataclasses `frozen=True`), en un módulo `menu.py` por app.
- **Justificación**: La spec lo exige (FR-002). Las rutas (`url_name`) y los permisos (`app_label.codename`) ya viven en el código; declararlos juntos permite validarlos al arrancar (R5) y revisar los cambios en el control de versiones. No se crea información institucional, así que no aplican inactivación ni auditoría de datos (Principio III).
- **Alternativas descartadas**:
  - *Modelos en BD editables desde Admin*: obligaría a crear modelos, migraciones, el mecanismo de inactivación, auditoría y tests, sin que exista una necesidad, y desincroniza el menú de las rutas reales. Fuera de alcance según la spec.
  - *Diccionario en `settings.py`*: centraliza en `config/` contenido de los módulos de negocio, lo que rompe la cohesión por módulo (Principio IV).

## R2. Descubrimiento de los `menu.py` por app

- **Decisión**: `CommonConfig.ready()` llama a `django.utils.module_loading.autodiscover_modules('menu')`. Cada `apps/<app>/menu.py` importa `apps.common.components.menu` y registra sus secciones e ítems con `registry.register_section(...)` / `registry.register_item(...)`.
- **Justificación**: Es el patrón nativo de Django (el mismo de `admin.autodiscover`). `apps/common` nunca importa por nombre un módulo de negocio: solo pide "el módulo `menu` de cada app instalada", y la dependencia va de negocio → common (Principio IV). Agregar una app con su `menu.py` no exige tocar common ni las plantillas (FR-003, SC-008).
- **Alternativas descartadas**:
  - *Lista explícita de módulos en settings*: es una segunda fuente de verdad y hay que editarla en cada app nueva.
  - *Un `ready()` en cada AppConfig*: el orden de `INSTALLED_APPS` haría frágil el registro, y algunas apps (`organizacion`, `personas`) no tienen AppConfig dedicado en `INSTALLED_APPS`.

## R3. Entrega al template: inclusion tag vs. simple tag vs. context processor

- **Decisión**: `simple_tag(takes_context=True)` llamado `get_sidebar`, en `apps/common/templatetags/navigation_tags.py`. Se usa como `{% get_sidebar as sidebar %}` dentro de `components/navigation/aside/base.html`. Devuelve `None` si el usuario no está autenticado.
- **Justificación**:
  - El cálculo ocurre solo cuando se renderiza el aside. Las respuestas HTMX parciales y las páginas públicas no lo pagan.
  - El marcado se queda en `aside/base.html`. Los layouts siguen haciendo `{% include 'components/navigation/aside/base.html' %}` sin cambios (FR-034).
  - No se genera HTML en Python.
  - El precedente `breadcrumb_tags.render_breadcrumbs` usa un inclusion tag; aquí se prefiere un simple tag "as variable" porque la estructura del aside reparte el árbol entre varios parciales (`_menu.html`, `_user.html`), y así base.html sigue siendo el punto de entrada visible.
- **Alternativas descartadas**:
  - *Context processor*: se ejecutaría en cada render, incluidos los parciales HTMX, el login y los correos.
  - *Inclusion tag que renderiza todo el aside*: es válido, pero obliga a convertir `aside/base.html` en una plantilla "vacía" que solo llama al tag, y oculta la estructura.

## R4. Cálculo del estado activo (incluidas las páginas secundarias)

- **Decisión**:
  - Cada ítem navegable declara `active_patterns: tuple[str, ...]` con patrones `namespace:url_name` que admiten comodín al estilo `fnmatch` (p. ej., `'organizacion:distrito_judicial_*'`). Por defecto vale `(url_name,)`.
  - Se compara contra `request.resolver_match.view_name`.
  - Si hay varias coincidencias, gana la **más específica**: una coincidencia exacta gana a una con comodín, y entre comodines gana el patrón más largo. Si persiste el empate, gana el primero en orden de menú.
  - Solo un ítem hoja queda activo (SC-003). Sus ancestros reciben `is_active_parent=True` y el desplegable se renderiza abierto (`show` + `aria-expanded="true"`).
- **Requisito de origen**: la precedencia está normada en spec.md FR-020; esta sección describe su implementación.
- **Justificación**: El estado se resuelve en el servidor y se reconstruye desde la URL (Principio I). Los nombres de ruta de `organizacion` siguen un prefijo por entidad (`distrito_judicial_create/update/details/toggle`), así que un comodín cubre las páginas secundarias sin enumerarlas.
- **Alternativas descartadas**:
  - *Comparar prefijos de `request.path`*: es frágil ante cambios de URL y no funciona con `sedes_list`, que depende de `<dj_id>`.
  - *Que cada vista marque el ítem activo en el contexto*: obliga a modificar todas las vistas y es fácil de olvidar.
  - *JavaScript que lea `location`*: lo prohíbe el Principio I.

## R5. Validación temprana de las declaraciones

- **Decisión**:
  - **System check** registrado en `apps/common/checks.py` (desde `CommonConfig.ready()`, tag `urls`). Verifica:
    - (a) ids únicos;
    - (b) cada `url_name` resuelve con `reverse` (los ítems con argumentos obligatorios se rechazan con un mensaje claro);
    - (c) secciones referenciadas que existen y no tienen etiquetas en conflicto;
    - (d) profundidad ≤ 3 niveles;
    - (e) el ítem es hoja (con destino) o contenedor (con hijos), pero no ambas cosas;
    - (f) ningún ítem sin permisos ni `visible_to_authenticated=True`, salvo que sea contenedor, porque los contenedores heredan visibilidad de sus hijos;
    - (g) la plantilla de ícono existe (`get_template`).
  - **Test** que verifica que cada permiso declarado existe en la tabla `Permission` después de migrar. Se hace como test y no como check porque necesita BD.
  - **En ejecución**, si `reverse` falla, el ítem se omite y se registra `logger.warning` (FR-009).
- **Justificación**: Los errores se detectan en `manage.py check`, en `runserver` y en CI antes de producción. La página nunca se rompe.
- **Alternativas descartadas**: *validar solo en tests*: un `menu.py` mal escrito llegaría a ejecutarse sin aviso hasta correr la suite.

## R6. Estrategia de íconos

- **Decisión**: Un parcial SVG por ícono en `templates/components/icons/<nombre>.html`, con `class="icon"`, `aria-hidden="true"` y `focusable="false"`.
  - **Procedencia y versión fija**: los SVG se copian de la distribución **Tabler 1.7.1** que ya está en el repositorio (`static/tabler/*.html`, cuyos SVG llevan el comentario `Download SVG icon from http://tabler.io/icons/icon/<nombre>`). Así la versión de los íconos es la misma, fija, del design system adoptado y no se descarga nada externo. Se verificó que los 8 íconos requeridos están en esa distribución: `home`, `settings` (`accordion.html`); `map-pin`, `scale`, `building-bank`, `external-link` (`icons.html`); `users` (`avatars.html`); `logout` (`dropdowns.html`).
  - **Licencia**: Tabler Icons, MIT.
  - **Trazabilidad**: cada parcial comienza con el comentario de plantilla `{# Tabler Icons (MIT) – <nombre> – copiado de Tabler 1.7.1, static/tabler/<archivo>.html #}`. Los íconos nuevos deben copiarse de la misma distribución; si un ícono no está en ella, se documenta su versión de origen en el mismo comentario. El ítem declara `icon='home'` y la plantilla hace `{% include 'components/icons/'|add:item.icon|add:'.html' %}`. Inicialmente se incluyen solo los íconos usados: `home` (Inicio), `map-pin` (Distritos judiciales), `scale` (Materias jurisdiccionales), `building-bank` (Órganos jurisdiccionales), `users` (Personas), `settings` (Usuarios), `logout` (Cerrar sesión) y `external-link` (indicador de enlaces externos).
- **Justificación**: El proyecto no tiene webfont ni sprite de Tabler Icons en `static/`, y añadirlos es una dependencia nueva. Los parciales no generan HTML en Python, no usan CDN, se reutilizan en cualquier componente y el system check (R5-g) valida que existan.
- **Alternativas descartadas**:
  - *Webfont tabler-icons*: es una dependencia nueva de unos 2 MB, y las fuentes de íconos dan problemas de accesibilidad.
  - *Sprite SVG con `<use href>`*: requiere un proceso de construcción del sprite.
  - *SVG almacenado como string en el `menu.py`*: es HTML en Python y está prohibido.

## R7. Logo institucional

- **Decisión**: Mover el SVG inline de `_logo.html` a `static/project/img/logo-csjpasco.svg` y renderizar `<img src="{% static 'project/img/logo-csjpasco.svg' %}" alt="Corte Superior de Justicia de Pasco" width="110" height="32" class="navbar-brand-image">` dentro de `<a href="{% url 'main:index' %}">`.
- **Justificación**: La constitución ubica las imágenes institucionales en `static/project/img/`. El navegador puede cachear la imagen y la plantilla queda limpia. El SVG conserva sus colores, pensados para fondo oscuro: blanco, `#D0D0D0` y `#E8B20F`. Ninguno es de la paleta institucional, así que no se repiten tokens.
- **Alternativas descartadas**:
  - *SVG inline*: plantilla de 39 líneas y sin caché.
  - *PNG existente en `logos_pj/`*: no escala y es otro logotipo (PJ, no CSJ Pasco).

## R8. Archivo CSS y regla del "único archivo de tokens"

- **Decisión**:
  - Crear `static/project/css/sidebar.css` solo con **reglas de componente** que consumen los tokens mediante `var(--institutional-primary)` y similares, sin ningún hex de la paleta.
  - Eliminar de `custom_color.css` el bloque `.sidebar-custom { background-color: #f9fafb !important; ... }`, que es la causa del conflicto, y trasladar a `sidebar.css` las reglas de ocultar scrollbar.
  - `custom_color.css` se queda como el único archivo de tokens.
  - Cargar `sidebar.css` en `templates/base.html` después de `custom_color.css`.
- **Justificación**: La constitución exige que **los valores** de la paleta estén en un único archivo de tokens. No prohíbe que otros archivos **consuman** los tokens. Separar las reglas del componente de los tokens mejora la cohesión (como ya pasa con `datatable.css`, `forms.css` y `custom_offcanvas.css`).
- **Alternativas descartadas**: *añadir las reglas en `custom_color.css`*: mezcla tokens y estilos de componente en un archivo que ya pasa de 300 líneas.
- **Nota fuera de alcance**: Existen variantes `custom_color_.css`, `custom_color_02..04.css` y `custom_color_original.css` que podrían repetir valores de la paleta. Se recomienda revisarlas en una feature de limpieza; esta feature no las toca.

## R9. Colores y contraste AA (solo tema claro)

Fondo: color institucional principal `#A42622`, con luminancia relativa L ≈ 0.094. Cálculos según WCAG 2.1 (sRGB linealizado):

| Elemento | Color | L | Contraste vs fondo | AA |
|---|---|---|---|---|
| Texto/íconos de ítems | blanco 100 % | 1.000 | **7.30 : 1** | ✔ texto normal |
| Texto atenuado por defecto de Tabler (`navbar-dark`, ≈ blanco 70 %) | mezcla ≈ `#E4BEBD` | 0.570 | **4.30 : 1** | ✘ texto normal |
| Texto blanco al 80 % (mínimo aceptable) | mezcla ≈ `#EDD4D3` | 0.696 | 5.18 : 1 | ✔ |
| Logo: gris `#D0D0D0` | — | 0.631 | 4.73 : 1 | ✔ |
| Logo: dorado `#E8B20F` | — | 0.490 | 3.75 : 1 | ✔ gráfico ≥ 3:1 (y logotipo exento por 1.4.3) |

- **Decisión**:
  - El texto, los íconos, los títulos de sección y los ítems de submenú usan **blanco 100 %** mediante la variable de Tabler `--tblr-navbar-color`, que se sobrescribe en `sidebar.css`. Nunca la opacidad por defecto de Tabler, porque falla AA.
  - El estado activo usa un **fondo oscurecido** (`rgba(0,0,0,.2)` sobre el principal, con texto blanco y contraste ≈ 10 : 1), más una **marca lateral blanca de 3 px** y `font-weight: 600`. Así hay indicadores no cromáticos (FR-030).
  - El foco visible es un contorno blanco de 2 px con desplazamiento, con contraste ≥ 3 : 1 sobre el fondo.
  - Las insignias usan `bg-white text-primary` o equivalentes con contraste ≥ 4.5 : 1, y siempre llevan texto.
- **Esquema de componente vs. tema de la aplicación**: el `<aside>` lleva `data-bs-theme="dark"` solo para que Tabler aplique al componente colores de primer plano claros sobre su fondo institucional oscuro. Es un **esquema local al componente**: no activa el tema oscuro de la aplicación, que sigue fijada en tema claro (`<html data-bs-theme="light">` en `templates/base.html`), y no constituye el "soporte de tema oscuro" diferido a la feature "Personalizar" (spec, Clarifications Q3). Todas las verificaciones de contraste (SC-006) se hacen con la aplicación en tema claro.
- **Insignias** (spec FR-017): variantes `light` (fondo blanco, texto en el color institucional principal: 7.30 : 1), `warning` (fondo amarillo de Tabler con texto oscuro) e `info` (fondo blanco con borde, texto oscuro). El contraste de cada variante (texto/fondo ≥ 4.5 : 1 y fondo de insignia/fondo del menú ≥ 3 : 1) se calcula y registra al implementar los tokens de `sidebar.css`; una variante que no cumpla se elimina del conjunto.
- **Justificación**: Es el resultado de la clarificación Q2 y del requisito WCAG 1.4.3 y 1.4.11. El hallazgo del 4.30 : 1 obliga a sobrescribir el color atenuado de Tabler.
- **Alternativas descartadas**: *dejar los colores por defecto de `navbar-dark`*: incumple AA.

## R10. Área de usuario e iniciales

- **Decisión**: El constructor del árbol devuelve un `UserPanel` con:
  - `full_name`: `user.get_full_name()` o, si está vacío, `user.get_username()`;
  - `secondary`: nombre del primer grupo del usuario en orden alfabético (`user.groups.order_by('name').values_list('name', flat=True).first()`), o `None` si no tiene grupos. **No** se usa el username, porque es el número de documento (spec §Seguridad, FR-021);
  - `initials`: primera letra del primer nombre y del apellido paterno; con un solo término, sus 2 primeras letras; en mayúsculas con `str.upper()`, conservando tildes y Ñ (p. ej., "Ángel Núñez" → "ÁN"; "Ñuflo" → "ÑU"). Se ignoran los caracteres no alfanuméricos al inicio de cada término. Si el nombre a usar es el username numérico (usuario sin nombre completo), se muestran sus 2 primeros dígitos. El avatar es decorativo (`aria-hidden="true"`). El disparador del menú de usuario lleva `aria-label="Menú de usuario de <nombre completo>"`, que incluye el nombre visible (WCAG 2.5.3, *Label in Name*), así que el lector de pantalla anuncia la función y la identidad;
  - `items`: el menú de usuario filtrado.
  - El avatar se renderiza como `<span class="avatar avatar-sm">{{ panel.initials }}</span>`, sin `style=`.
  - "Cerrar sesión" se declara en `apps/usuarios/menu.py` como `UserMenuItem(kind='post', url_name='usuarios:cerrar_sesion', label='Cerrar sesión', icon='logout', visible_to_authenticated=True)` y se renderiza como `<form method="post">` con `{% csrf_token %}` y `<button type="submit" class="dropdown-item">`.
- **Justificación**:
  - El modelo `Usuario` no tiene foto ni cargo (supuesto de la spec).
  - `UsuarioLogoutView` hereda de `LogoutView`, que en Django 5+ solo acepta POST y emite `user_logged_out` (FR-024, FR-024a). No hace falta tocar la vista.
  - Las opciones del menú de usuario vienen del mismo registro (FR-025).
- **Alternativas descartadas**:
  - *Iniciales calculadas en la plantilla con filtros*: es lógica en la plantilla y difícil de probar.
  - *Enlace GET a logout*: es inseguro y Django 6 no lo acepta.

## R11. Barra superior y layouts (FR-026, FR-034)

- **Decisión**:
  - Quitar `{% include 'components/navigation/navbar/base.html' %}` de los 6 layouts con aside: `layouts/base_page.html`, `layouts/base_list.html`, `layouts/htmx_base_page.html`, `layouts/htmx/base_page.html`, `layouts/htmx/page_wrapper.html` y `layouts/dashboards/base_list.html`.
  - Eliminar `layouts/base_form copy.html` y `layouts/base_page copy.html`, verificando antes con búsqueda que nada los referencia.
  - El componente `navigation/navbar/` se conserva en el repositorio para usos futuros, pero ningún layout con aside lo incluye.
  - En `aside/base.html` se eliminan `bg-primary` y `sidebar-custom` y se usa una clase propia del componente, `sidebar-institucional`.
- **Justificación**: Es la clarificación Q1 (opción B).
- **HTMX**: Las vistas de lista devuelven parciales (`partials/_datatable.html`) cuando hay `HX-Request` y no extienden layouts, así que el aside no se duplica. Se añade un test que lo verifica.

## R12. Protección de vistas (FR-008a)

- **Decisión**:
  - `@login_required` en `apps/main/views.py:index`.
  - `@login_required` + `@permission_required('<app>.view_<modelo>', raise_exception=True)` en las vistas de lista, igual que el precedente `apps/usuarios/views/cuentas.py:usuarios_list`:
    - `distritos_judiciales_list` → `organizacion.view_distritojudicial`
    - `materias_jurisdiccionales_list` → `organizacion.view_materiajurisdiccional`
    - `organos_jurisdiccionales_list` → `organizacion.view_organojurisdiccional`
    - `personas_list` → `personas.view_persona`
  - Corregir el `name` duplicado de la ruta de lista de órganos en `apps/organizacion/urls.py` a `organos_jurisdiccionales_list`, revisando antes con búsqueda los usos de `organo_jurisdiccional_toggle` que esperen la lista.
- **Justificación**: Principio II, la clarificación de la spec (Q1 = A) y el precedente que ya existe en el repo.
- **Alternativas descartadas**: *`LoginRequiredMiddleware` (Django 5.1+) global*: cambia el comportamiento de todo el sitio, incluidas vistas fuera de alcance (signup, registro, recuperación de contraseña). Se evaluará en la feature de seguridad.

## R13. Pruebas y base de datos

- **Decisión**:
  - Tests con `django.test.TestCase` en `apps/common/tests/` (convertir en paquete): `test_menu_registry.py`, `test_menu_builder.py`, `test_menu_checks.py` y `test_sidebar_render.py`.
  - Tests de vistas protegidas en los tests de cada app: `apps/organizacion/tests.py`, `apps/personas/tests.py` y `apps/main/tests.py`.
  - Para aislar las pruebas del registro global se usa un `MenuRegistry` nuevo inyectado o `override` mediante un context manager del propio registro.
  - En desarrollo se ejecuta con SQLite (configuración actual). Antes de desplegar, la suite DEBE ejecutarse contra PostgreSQL (constitución).
- **Justificación**: Es lo que pide la constitución (sección de testing) y SC-001 a SC-008.

## R14. Páginas de error y fallo de verificación CSRF (spec FR-008b, Edge Cases)

- **Decisión**:
  - `templates/403.html` y `templates/404.html` extienden `layouts/base_page.html`, así que muestran el aside si hay sesión (el tag `get_sidebar` devuelve `None` para anónimos). Usan mensajes en español formal, sin detalles técnicos ni nombres de permisos, y un enlace a `main:index`. Django los usa automáticamente con `DEBUG=False` (`handler403`/`handler404` por defecto, con `RequestContext`).
  - `templates/500.html` es autocontenido: no extiende layouts, no usa template tags del proyecto ni contexto de request y tiene un enlace a `/`. El `handler500` por defecto de Django renderiza sin contexto, y la página no debe depender del aside, que podría ser la causa del error.
  - `templates/403_csrf.html`: el `csrf_failure` por defecto de Django lo usa automáticamente si existe. Es autocontenido (se renderiza sin `RequestContext`) y explica en español que la solicitud no pudo verificarse, con enlaces a `main:index` y al inicio de sesión. No hace falta `CSRF_FAILURE_VIEW` propio.
  - **Cierre de sesión con la sesión expirada**: la cookie CSRF es independiente de la sesión (configuración por defecto), así que el POST se valida y `LogoutView` redirige al inicio de sesión aunque el usuario ya sea anónimo. No requiere código.
- **Justificación**: Usa los mecanismos nativos de Django (Principio I) y cumple la regla constitucional de mensajes en español formal y orientados a la acción.
- **Alternativas descartadas**: vistas de error personalizadas (`handler403 = ...`). No se necesitan: las plantillas con los nombres estándar bastan.

## R15. Observaciones de T071 por debajo de 992 px

- **Esc no cerraba el menú desplegado.** El colapso de Bootstrap no atiende Esc.
  - **Decisión**: un manejador Alpine.js en el `<aside>` (`@keydown.escape.window`). Si el menú tiene `show` y el evento no fue consumido (`$event.defaultPrevented`, que Bootstrap marca al cerrar un desplegable con Esc), pulsa el botón del propio Bootstrap y le devuelve el foco.
  - **Alternativas descartadas**: convertir el menú en `offcanvas`, que atiende Esc de forma nativa pero cambia todo el marcado del patrón de referencia; o un archivo en `static/project/js/`, que el Principio I reserva como último recurso cuando Alpine.js basta.
- **El menú de usuario se veía recortado.** Bootstrap define `.navbar-nav .dropdown-menu { position: static }` para navbars colapsados, y por debajo de 992 px el menú se dibujaba dentro de la barra de altura fija. La regla de Tabler `.navbar-footer .dropup .dropdown-menu { top: 100%; … }` no surtía efecto.
  - **Decisión**: en `sidebar.css`, por debajo de 992 px, el menú del pie pasa a `position: absolute` con el `z-index` de los desplegables.

## Hallazgos fuera de alcance (registrados para features futuras)

- `apps/common/context_procesors.py:htmx_base_template` no está registrado en `TEMPLATES` y usa `request.htmx` sin `django-htmx`, pero `apps/personas/templates/personas/create.html` extiende `base_template`. Es un riesgo de error en esa vista.
- Las vistas de crear, editar, detalle, cambio de estado y exportación de Organización y Personas no tienen protección (feature de seguridad posterior).
- Las variantes `custom_color_*.css` pueden repetir valores de la paleta.
- No hay script de actualización del contexto del agente en speckit 1.2.4 (ver plan.md).
