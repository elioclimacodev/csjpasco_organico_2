# Quickstart: validar la protección de operaciones y la configuración segura

**Feature**: 002-seguridad-acceso-configuracion

Contratos: [vistas-y-permisos](contracts/vistas-y-permisos.md) · [respuestas-acceso](contracts/respuestas-acceso.md) · [variables-entorno](contracts/variables-entorno.md).

## Requisitos previos

1. `pip install -r requirements.txt`.
2. **`.env` actualizado** (obligatorio tras esta feature):
   - `SECRET_KEY=<nueva>`, generada con `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`. No reutilizar la clave del historial de git (FR-017).
   - Desarrollo: `DEBUG=true`. Opcional: `ALLOWED_HOSTS` (por defecto `localhost,127.0.0.1` con `DEBUG`).
   - Si se accede por IP de la red local en HTTP: `SESSION_COOKIE_SECURE=false` y `CSRF_COOKIE_SECURE=false`.
3. `python manage.py migrate`.

## 1. Verificaciones automáticas

```bash
python manage.py check
DB_ENGINE=sqlite python manage.py test --noinput
python manage.py test --noinput            # con DB_ENGINE=postgresql en .env
```

**Resultado esperado**: sin errores y todos los tests en verde, incluidos los de la feature 001.

## 2. Perfiles de prueba (Admin)

| Usuario | Permisos |
|---|---|
| `nuevo` | ninguno (cuenta recién activada) |
| `consulta` | `ubicaciones.view_provincia`, `organizacion.view_distritojudicial` |
| `editor` | los anteriores más `add_*` y `change_*` de provincia y distrito judicial |
| `admin` | superusuario |

Todos deben estar **activos**.

## 3. Escenarios manuales

| # | Pasos | Resultado esperado | Requisitos |
|---|---|---|---|
| 1 | Sin sesión, abrir `/ubicaciones/paises/` (lista) y `/organizacion/distrito-judicial/1/detalles/` | Redirección al login; tras autenticarse vuelve a la página pedida | FR-001, FR-005, US1 |
| 2 | Sin sesión, abrir login, recuperar contraseña y registro | Responden normalmente | FR-003, SC-002 |
| 3 | Abrir `/signup/` | 404 (retirada) | FR-004 |
| 4 | Como `nuevo`, entrar a Inicio | Aviso "Su cuenta aún no tiene permisos asignados…"; menú solo con "Inicio" | FR-003a |
| 5 | Como `admin`, entrar a Inicio | Sin aviso | FR-003a |
| 6 | Como `consulta`, abrir la lista de provincias y el detalle de una | Acceso | FR-006 |
| 7 | Como `consulta`, pulsar "Nuevo registro" o "Editar" | El modal muestra "Acceso denegado" con un botón "Cerrar"; sin menú lateral dentro | FR-011, US3-2 |
| 8 | Como `consulta`, pulsar "Cambiar estado" | Modal "Acceso denegado"; el registro conserva su estado | FR-009 |
| 9 | Quitar a `consulta` el permiso `view_provincia` con la lista abierta y filtrar la tabla | Toast de error "No tiene permiso para realizar esta operación."; la tabla no cambia | FR-011, US3-3 |
| 10 | Como `consulta`, abrir la exportación de una entidad sin permiso | 403; no se descarga ningún archivo | FR-009 |
| 11 | Con un modal abierto, cerrar la sesión en otra pestaña y abrir otro detalle | La página completa va al login y, tras autenticarse, vuelve a la lista | FR-012, US3-1 |
| 12 | Quitar `SECRET_KEY` del `.env` y ejecutar `python manage.py check` | Falla: "La variable de entorno SECRET_KEY es obligatoria…" | FR-013, SC-007 |
| 13 | Quitar `DEBUG` del `.env` y arrancar | La depuración queda desactivada (404 con la página del ERP, no la técnica); hay que definir `ALLOWED_HOSTS` | FR-014 |
| 14 | Poner `DEBUG=quizas` | Falla indicando los valores aceptados | FR-014 |
| 15 | Con `SECURE_SSL_REDIRECT=true` y `SECURE_HSTS_SECONDS=31536000`, pedir una URL por HTTP | Redirección a HTTPS; la respuesta HTTPS incluye `Strict-Transport-Security` | FR-016a, SC-006a |
| 16 | `git grep -n "django-insecure\|socket.gethostbyname" config/` | Sin resultados | FR-015, FR-017, SC-006 |
| 17 | Como `consulta`, abrir `/ubicaciones/departamentos/999999/provincias/` | 404 (tiene el permiso y el departamento no existe); sin `view_provincia` → 403 | spec §Edge Cases, C6 |
| 18 | Abrir una ventana, cerrar la sesión en otra pestaña, volver a iniciarla y enviar el formulario de la ventana original | La página se recarga (token CSRF nuevo); no aparece la página de error dentro de la ventana | spec §Edge Cases, FR-011 |
| 19 | Con un lector de pantalla, provocar la denegación en una ventana | Se anuncia "Acceso denegado…" y el foco queda en "Cerrar" | FR-011 |
