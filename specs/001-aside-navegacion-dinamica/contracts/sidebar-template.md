# Contrato: template tag y marcado del aside

**Proveedor**: `apps/common/templatetags/navigation_tags.py` + `templates/components/navigation/aside/`.
**Consumidores**: los layouts globales (sin cambios en su forma de incluir el aside).

## 1. Inclusión desde los layouts (sin cambios)

```django
{% include 'components/navigation/aside/base.html' %}
```

El contexto debe contener `request` (context processor `django.template.context_processors.request`, ya activo).

## 2. Template tag

```django
{% load navigation_tags %}
{% get_sidebar as sidebar %}
```

- Firma: `@register.simple_tag(takes_context=True) def get_sidebar(context) -> Sidebar | None`.
- Lee `context['request']` y `request.user`.
- Devuelve `None` si no hay `request` o si el usuario no está autenticado.
- No genera HTML: devuelve la estructura `Sidebar` de [data-model.md](../data-model.md) §2.
- El árbol entregado solo determina lo que se **muestra**: no sustituye la autorización de cada vista (spec FR-008).

## 3. Marcado obligatorio (Tabler 1.7.1, navbar vertical)

Se renderiza solo `{% if sidebar %}`. Esqueleto normativo (atributos clave; clases auxiliares a criterio).

**Orden en el documento (spec FR-028)**: toggler → logo → `<nav>` (menú) → `navbar-footer` (área de usuario). En la plantilla de referencia de Tabler, `navbar-footer` va **antes** del menú y se reubica abajo solo con CSS (`.navbar-footer { order: 1; margin-top: auto }` en tabler.min.css). Eso hace que el orden de foco no coincida con el orden visual (WCAG 2.4.3 y 1.3.2). Por eso el componente coloca el área de usuario **después** del `<nav>`. Visualmente no cambia nada, porque las reglas `order: 1` y `margin-top: auto` siguen aplicándose.

**Esquema `data-bs-theme="dark"`**: es local al componente y no activa el tema oscuro de la aplicación (ver research R9).

```html
<aside class="navbar navbar-vertical navbar-expand-lg sidebar-institucional" data-bs-theme="dark">
  <div class="container-fluid">
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
            data-bs-target="#sidebar-menu" aria-controls="sidebar-menu"
            aria-expanded="false" aria-label="Mostrar u ocultar el menú de navegación">
      <span class="navbar-toggler-icon"></span>
    </button>

    <!-- _logo.html -->
    <div class="navbar-brand navbar-brand-autodark">
      <a href="{% url 'main:index' %}">
        <img src="{% static 'project/img/logo-csjpasco.svg' %}" width="110" height="32"
             alt="Corte Superior de Justicia de Pasco" class="navbar-brand-image">
      </a>
    </div>

    <!-- _menu.html -->
    <nav class="collapse navbar-collapse" id="sidebar-menu" aria-label="Menú principal">
      <ul class="navbar-nav pt-lg-3">
        <!-- por sección; el título solo si section.label -->
        <li class="nav-section-title">{{ section.label }}</li>
        <!-- _menu_item.html (nivel 1) -->
      </ul>
      <!-- navbar-side: reservado, NO se renderiza en esta feature -->
    </nav>

    <!-- _user.html -->
    <div class="navbar-footer">
      <ul class="navbar-nav">
        <li class="nav-item dropup">
          <a href="#" class="nav-link" data-bs-toggle="dropdown" aria-expanded="false"
             aria-label="Menú de usuario de {{ sidebar.user.full_name }}">
            <span class="avatar avatar-sm" aria-hidden="true">{{ sidebar.user.initials }}</span>
            <div class="nav-link-title">{{ sidebar.user.full_name }}
              {% if sidebar.user.secondary %}<div class="small">{{ sidebar.user.secondary }}</div>{% endif %}</div>
          </a>
          <div class="dropdown-menu">
            <!-- kind == 'post' -->
            <form method="post" action="{{ item.href }}">{% csrf_token %}
              <button type="submit" class="dropdown-item">[ícono] {{ item.label }}</button>
            </form>
            <!-- kind == 'link' --> <a class="dropdown-item" href="{{ item.href }}">…</a>
          </div>
        </li>
      </ul>
    </div>
  </div>
</aside>
```

### Nivel 1 (`_menu_item.html`)

| Caso | Marcado |
|---|---|
| Hoja | `<li class="nav-item{% if is_active %} active{% endif %}"><a class="nav-link" href="…" {% if is_active %}aria-current="page"{% endif %}>` + `<span class="nav-link-icon">ícono</span>` + `<span class="nav-link-title">label</span>` + insignia |
| Contenedor | `<li class="nav-item dropdown{% if is_active_parent %} active{% endif %}">` + `<a class="nav-link dropdown-toggle{% if is_active_parent %} show{% endif %}" href="#" data-bs-toggle="dropdown" data-bs-auto-close="false" role="button" aria-expanded="{{ is_active_parent|yesno:'true,false' }}">` + `<div class="dropdown-menu{% if is_active_parent %} show{% endif %}">` con `dropdown-menu-columns` > `dropdown-menu-column` por columna |

### Niveles 2 y 3 (`_dropdown_item.html`)

| Caso | Marcado |
|---|---|
| Hoja | `<a class="dropdown-item{% if is_active %} active{% endif %}" href="…" {% if is_active %}aria-current="page"{% endif %}>` [ícono `dropdown-item-icon`] label [insignia] |
| Contenedor (solo nivel 2) | `<div class="dropend">` + `<a class="dropdown-item dropdown-toggle" href="#" data-bs-toggle="dropdown" data-bs-auto-close="false" role="button" aria-expanded="…">` + `<div class="dropdown-menu">` hijos nivel 3 |

### Reglas transversales del marcado

- Ícono: `{% include 'components/icons/'|add:item.icon|add:'.html' %}`. El SVG lleva `aria-hidden="true" focusable="false"`.
- Insignia: `<span class="badge badge-sm sidebar-badge-{{ badge.variant }} ms-auto">{{ badge.text }}</span>`.
- Enlace externo: `target="_blank" rel="noopener"` + ícono `external-link` + `<span class="visually-hidden">(se abre en una pestaña nueva)</span>`.
- **Prohibido**: atributo `style=`, textos en inglés, `href` a `.html` de demostración y JavaScript propio.
- `data-bs-theme="dark"` en el `<aside>` hace que Tabler use colores de componente claros sobre el fondo oscuro. Los colores exactos se fijan en `static/project/css/sidebar.css` (research R9).

## 4. Verificaciones de prueba asociadas

| Comportamiento | Verificación |
|---|---|
| Anónimo | La respuesta no contiene `<aside` ni `id="sidebar-menu"`. |
| Activo | Exactamente un `aria-current="page"` en el HTML del aside. |
| Logout | El formulario es POST con `csrfmiddlewaretoken` y `action` igual a `reverse('usuarios:cerrar_sesion')`. |
| Sin estilos inline | Ningún archivo bajo `templates/components/navigation/aside/` ni `templates/components/icons/` contiene `style=`. |
| Sin barra superior | Las páginas que usan los 6 layouts no contienen `navbar/base.html` (`<header class="navbar`). |
