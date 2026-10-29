# Contrato: vistas públicas, vistas protegidas y permisos

**Fuente normativa** para los tests de acceso (research R8-a y R8-b) y para la revisión de código.

## 1. Vistas públicas (sin sesión)

| Ruta (nombre) | Vista | Cómo queda exenta |
|---|---|---|
| `usuarios:iniciar_sesion` | `UsuarioLoginView` | hereda la exención nativa de `LoginView` |
| `usuarios:cerrar_sesion` | `UsuarioLogoutView` | **explícita**: `method_decorator(login_not_required, name='dispatch')` (solo acepta POST de forma nativa) |
| `usuarios:restablecer_contrasena` | `UsuarioPasswordResetView` | nativa (`PasswordResetView`) |
| `usuarios:restablecer_contrasena_enviado` | `UsuarioPasswordResetDoneView` | nativa |
| `usuarios:restablecer_contrasena_confirmar` | `UsuarioPasswordResetConfirmView` | nativa |
| `usuarios:restablecer_contrasena_completado` | `UsuarioPasswordResetComplete` | nativa |
| `usuarios:registro` | `registro` | **explícita**: `@login_not_required` |
| `usuarios:activar_cuenta` | `activar_cuenta` | **explícita**: `@login_not_required` |
| `usuarios:registro_completo` | `registro_completo` | **explícita**: `@login_not_required` |

Fuera del middleware (no son vistas enrutadas): los manejadores de error 403, 404 y 500 y la página de fallo CSRF.

Excluidas del recorrido de "debe exigir sesión": `admin:*` (tiene su propio control) y la ruta `static()`.

**Se retira**: `main:signup` (vista `apps/main/views.py:signup`, ruta en `apps/main/urls.py` y plantilla `main/signup.html`).

## 2. Vistas protegidas y permiso exigido

`main:index` → solo sesión (sin permiso; FR-003a).

| Módulo | Ruta (nombre) | Permiso |
|---|---|---|
| organizacion | `distritos_judiciales_list`, `distrito_judicial_details`, `distritos_judiciales_export` | `organizacion.view_distritojudicial` |
| organizacion | `distrito_judicial_create` | `organizacion.add_distritojudicial` |
| organizacion | `distrito_judicial_update`, `distrito_judicial_toggle` | `organizacion.change_distritojudicial` |
| organizacion | `materias_jurisdiccionales_list`, `materia_jurisdiccional_details`, `materias_jurisdiccionales_export` | `organizacion.view_materiajurisdiccional` |
| organizacion | `materia_jurisdiccional_create` | `organizacion.add_materiajurisdiccional` |
| organizacion | `materia_jurisdiccional_update`, `materia_jurisdiccional_toggle` | `organizacion.change_materiajurisdiccional` |
| organizacion | `organos_jurisdiccionales_list`, `organo_jurisdiccional_details`, `organos_jurisdiccionales_export` | `organizacion.view_organojurisdiccional` |
| organizacion | `organo_jurisdiccional_create` | `organizacion.add_organojurisdiccional` |
| organizacion | `organo_jurisdiccional_update`, `organo_jurisdiccional_toggle` | `organizacion.change_organojurisdiccional` |
| organizacion | `sedes_list`, `sede_details`, `sedes_export` | `organizacion.view_sedejudicial` |
| organizacion | `sede_create` | `organizacion.add_sedejudicial` |
| organizacion | `sede_update`, `sede_toggle` | `organizacion.change_sedejudicial` |
| personas | `list` | `personas.view_persona` |
| personas | `create` | `personas.add_persona` |
| ubicaciones | `countries_list`, `country_details`, `countries_export` | `ubicaciones.view_pais` |
| ubicaciones | `country_create` | `ubicaciones.add_pais` |
| ubicaciones | `country_update`, `country_toggle` | `ubicaciones.change_pais` |
| ubicaciones | `departamentos_list`, `departamento_details`, `departamentos_export` | `ubicaciones.view_departamento` |
| ubicaciones | `departamento_create` | `ubicaciones.add_departamento` |
| ubicaciones | `departamento_update`, `departamento_toggle` | `ubicaciones.change_departamento` |
| ubicaciones | `provincias_list`, `provincia_details`, `provincias_export` | `ubicaciones.view_provincia` |
| ubicaciones | `provincia_create` | `ubicaciones.add_provincia` |
| ubicaciones | `provincia_update`, `provincia_toggle` | `ubicaciones.change_provincia` |
| ubicaciones | `distritos_list`, `distrito_details`, `distritos_export` | `ubicaciones.view_distrito` |
| ubicaciones | `distrito_create` | `ubicaciones.add_distrito` |
| ubicaciones | `distrito_update`, `distrito_toggle` | `ubicaciones.change_distrito` |
| usuarios | `list` | `usuarios.view_usuario` (ya existente) |
| usuarios | `cambiar_contrasena`, `cambiar_contrasena_completado` | solo sesión (nativo) |

Codenames verificados en la base (2026-10-29): `ubicaciones.view_pais`, `…_departamento`, `…_provincia`, `…_distrito` y `organizacion.*_sedejudicial`.

## 3. Reglas verificadas por tests

- C1. Ninguna ruta enrutada fuera de §1 y de las exclusiones responde a un anónimo sin redirigir al login.
- C2. Toda ruta de §2, salvo `main:index` y `cambiar_contrasena*`, lleva `permission_required` con el permiso de la tabla.
- C3. Con un usuario sin permiso → `403`; con el permiso indicado → no `403`.
- C4. Las rutas de escritura y exportación denegadas no cambian datos ni devuelven archivos.
- C5. Los `apps/<app>/menu.py` declaran el mismo permiso que la tabla para su ruta destino.
