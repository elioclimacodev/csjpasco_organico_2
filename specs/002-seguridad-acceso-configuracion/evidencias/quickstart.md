# Evidencias: recorrido de quickstart.md (T055)

**Fecha**: 2026-10-30 | **Rama**: `002-seguridad-acceso-configuracion`

Leyenda:
- **Automatizado ✔**: el comportamiento lo verifica la suite. Se cita el test.
- **Terminal ✔**: ejecutado desde la terminal; se transcribe la salida.
- **Manual pendiente**: requiere navegador, servidor HTTPS o lector de pantalla. Lo ejecuta el Responsable Técnico y registra aquí el resultado.

| # | Escenario | Estado | Evidencia |
|---|---|---|---|
| 1 | Sin sesión, lista de países y detalle de distrito judicial → login y retorno | Automatizado ✔ · Manual pendiente (navegador) | `test_acceso_global.DenegacionPorDefectoTests.test_toda_ruta_no_publica_redirige_al_anonimo_al_login_con_retorno`; `VistasPublicasTests.test_tras_iniciar_sesion_vuelve_a_la_pagina_pedida` |
| 2 | Login, recuperación y registro sin sesión | Automatizado ✔ | `VistasPublicasTests.test_las_paginas_publicas_responden_sin_sesion` |
| 3 | `/signup/` → 404 | Automatizado ✔ | `apps.main.tests.SignupRetiradaTests` |
| 4 | Usuario sin permisos ve el aviso en Inicio | Automatizado ✔ · Manual pendiente (captura) | `apps.main.tests.AvisoCuentaSinPermisosTests.test_usuario_sin_permisos_ve_el_aviso` |
| 5 | Administrador sin aviso | Automatizado ✔ | `AvisoCuentaSinPermisosTests.test_superusuario_no_lo_ve` |
| 6 | Perfil consulta: lista y detalle de provincias | Automatizado ✔ | `PermisosPorOperacionTests.test_cada_ruta_exige_su_permiso` (`ubicaciones:provincias_list`, `provincia_details`) |
| 7 | Perfil consulta: "Nuevo registro"/"Editar" → modal "Acceso denegado" con "Cerrar" | Automatizado ✔ · Manual pendiente (captura) | `test_respuestas_htmx.FragmentoSinPermisoTests.test_en_ventana_muestra_el_aviso_con_cerrar` |
| 8 | Perfil consulta: "Cambiar estado" → denegado; estado sin cambios | Automatizado ✔ | `SinEfectosUbicacionesTests.test_provincia` (C4) |
| 9 | Sin `view_provincia`, filtrar la tabla → toast; tabla sin cambios | Automatizado ✔ · Manual pendiente (captura) | `FragmentoSinPermisoTests.test_en_tabla_muestra_un_toast_sin_alterar_la_tabla` |
| 10 | Exportación sin permiso → 403, sin archivo | Automatizado ✔ | `comprobar_sin_efectos` (exportación) en las 8 entidades |
| 11 | Sesión cerrada en otra pestaña, abrir otro detalle → página completa al login y retorno | Automatizado ✔ · Manual pendiente (navegador) | `FragmentoSinSesionTests` (401 + `HX-Redirect`) |
| 12 | Sin `SECRET_KEY`, `manage.py check` | Terminal ✔ | `ImproperlyConfigured: La variable de entorno SECRET_KEY es obligatoria y no está definida. Revise el archivo .env (ver .env.example).` |
| 13 | Sin `DEBUG` | Terminal ✔ | Sin `ALLOWED_HOSTS`: `La variable de entorno ALLOWED_HOSTS es obligatoria cuando DEBUG no está activo…`; con `ALLOWED_HOSTS=localhost`: `DEBUG = False` |
| 14 | `DEBUG=quizas` | Terminal ✔ | `La variable de entorno DEBUG tiene el valor no reconocido "quizas". Use true o false (también se aceptan 1, 0, sí, si y no)…` |
| 15 | Transporte seguro: HTTP → HTTPS y HSTS | Automatizado ✔ (simulado) · Manual pendiente (servidor de producción, SC-006a) | `test_entorno.TransporteSeguroTests` |
| 16 | `git grep -n "django-insecure\|socket.gethostbyname" config/` | Terminal ✔ | Sin resultados |
| 17 | `/ubicaciones/departamentos/999999/provincias/` | Automatizado ✔ | `RutasAnidadasUbicacionesTests.test_padre_inexistente` (403 sin permiso; 404 con él) |
| 18 | Fallo CSRF al enviar desde una ventana tras volver a iniciar sesión → la página se recarga | Automatizado ✔ · Manual pendiente (navegador) | `test_respuestas_htmx.FalloCsrfTests.test_en_htmx_responde_con_recarga` |
| 19 | Lector de pantalla: se anuncia "Acceso denegado" y el foco queda en "Cerrar" | Manual pendiente (NVDA) | Marcado verificado por `test_en_ventana_muestra_el_aviso_con_cerrar` (`role="alert"`, un único `autofocus`) |

## Auditoría de código (T054)

| Comprobación | Resultado |
|---|---|
| `style=` en `modal_denegado.html`, `modal_warning.html`, `aviso_persistente.html` y `main/index.html` | Sin resultados |
| Cambios en `static/project/js` respecto de `master` | Ninguno |
| `django-insecure` o `socket` en `config/` | Sin resultados |
| HTML construido en `apps/usuarios/middleware.py` y `apps/usuarios/views/denegacion.py` | Ninguno |
| `mark_safe` o `format_html` añadidos | Ninguno |
| Migraciones nuevas respecto de `master` | Ninguna |
| Archivos fuera de alcance modificados (apps heredadas, `views_.py`, `datatable_tags.py`, paleta) | Ninguno |
| `db.sqlite3` o `.env` en commits de la rama | Ninguno |

## Hallazgo fuera de alcance

`templates/components/modals/modal_form.html` incluye `components/forms/form_fields.html`, una plantilla que no existe en el repositorio. Por eso el formulario de alta de distritos judiciales, materias y órganos jurisdiccionales responde 500, con o sin esta feature. Se registra para corregirlo en otra feature.

## Resultados manuales (completar)

| # | Fecha | Resultado | Observaciones / captura |
|---|---|---|---|
| 1 | 30/10/2026 | Correcto | Verificado por el Responsable Técnico |
| 4 | 30/10/2026 | Correcto | Verificado por el Responsable Técnico |
| 7 | 30/10/2026 | Correcto | Verificado por el Responsable Técnico |
| 9 | 30/10/2026 | Correcto | Verificado por el Responsable Técnico |
| 11 | 30/10/2026 | Correcto | Verificado por el Responsable Técnico |
| 18 | 30/10/2026 | Correcto | Verificado por el Responsable Técnico |
| 19 | 30/10/2026 | Correcto | Verificado por el Responsable Técnico con NVDA |
