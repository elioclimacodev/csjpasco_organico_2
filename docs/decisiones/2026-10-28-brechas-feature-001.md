# Decisión: brechas preexistentes de auditoría y protección de vistas en la feature 001

| Campo | Valor |
|---|---|
| Fecha | 2026-10-28 |
| Feature | `001-aside-navegacion-dinamica` (specs/001-aside-navegacion-dinamica/) |
| Principios afectados | II (Seguridad por Diseño) y III (Integridad de Datos y Auditoría) |
| Tipo | Registro de brecha preexistente. **No es una excepción** (constitución §Excepciones: no aplicable a II y III) **ni una enmienda**. |
| Aprobador | Responsable Técnico vigente según `docs/responsables.md`, en la sesión de revisión del checklist `revision-requisitos.md` (CHK008) |
| Fecha de revisión | Al entregarse la feature del módulo de auditoría, o el **2027-01-31**, lo que ocurra primero (fecha propuesta; ajustable por el Responsable Técnico) |

## Contexto

Antes de esta feature:
- El sistema no tiene un módulo de auditoría de eventos: ningún evento de autenticación ni ninguna denegación de autorización se audita.
- Las vistas de Organización y Personas, y la página de Inicio, no exigen autenticación ni permisos.

La feature 001:
- **no introduce** esas desviaciones;
- **reduce** la brecha del Principio II, porque protege Inicio y las 4 páginas de lista que enlaza el menú (FR-008a);
- **deja preparados los puntos de enganche nativos** para la auditoría: el evento `user_logged_out` del cierre de sesión (FR-024a) y la excepción `PermissionDenied` de las denegaciones.

## Brechas registradas

| Id (plan.md) | Brecha | Riesgo aceptado | Cierre comprometido |
|---|---|---|---|
| III.2 | El cierre de sesión no genera registro de auditoría | No queda constancia de cuándo cierra sesión cada usuario | Feature del módulo de auditoría: receptor de `user_logged_in`, `user_logged_out` y `user_login_failed` |
| III.2b | Las denegaciones 403 de las 4 listas del menú inicial no se auditan | No queda constancia de intentos de acceso sin permiso | Feature del módulo de auditoría: captura centralizada de `PermissionDenied` (middleware o `handler403`) |
| II.4 | Solo se protegen Inicio y las 4 listas; crear, editar, detalle, cambio de estado y exportar de Organización y Personas siguen sin protección | Acceso no autorizado a esas vistas por URL directa | Feature de seguridad: protección de todas las vistas de esos módulos |

## Decisión

Se acepta implementar la feature 001 con las brechas anteriores registradas como **preexistentes**. Las condiciones son:

1. La feature 001 no debe ampliar ninguna de las brechas.
2. Las features de auditoría y de seguridad son compromisos que se priorizan inmediatamente después de la 001.
3. Esta decisión se revisa en la fecha indicada. Si para entonces no se han cerrado las brechas, el Responsable Técnico debe decidir entre priorizarlas o tramitar una enmienda.
