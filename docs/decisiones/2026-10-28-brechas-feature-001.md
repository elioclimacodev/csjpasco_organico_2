# Decisión: brechas preexistentes de auditoría y protección de vistas en la feature 001

| Campo | Valor |
|---|---|
| Fecha | 2026-10-28 |
| Feature | `001-aside-navegacion-dinamica` (specs/001-aside-navegacion-dinamica/) |
| Principios afectados | II (Seguridad por Diseño) y III (Integridad de Datos y Auditoría) |
| Tipo | Brecha preexistente conforme a constitución **v1.1.0 §Gobernanza › Brechas preexistentes**. No es una excepción (§Excepciones no se aplica a II y III) ni una enmienda. |
| Aprobador | Responsable Técnico vigente según `docs/responsables.md`, en la sesión de revisión del checklist `revision-requisitos.md` (CHK008) |
| Fecha de revisión | Al entregarse la feature del módulo de auditoría, o el **2027-01-31**, lo que ocurra primero (confirmada por el Responsable Técnico el 2026-10-28) |

## Contexto

Antes de esta feature:
- El sistema no tiene un módulo de auditoría de eventos: ningún evento de autenticación ni ninguna denegación de autorización se audita.
- Las vistas de Organización y Personas, y la página de Inicio, no exigen autenticación ni permisos.

La feature 001:
- **no introduce** esas desviaciones;
- **reduce** la brecha del Principio II, porque protege Inicio y las 4 páginas de lista que enlaza el menú (FR-008a);
- **deja preparados los puntos de enganche nativos** para la auditoría: el evento `user_logged_out` del cierre de sesión (FR-024a) y la excepción `PermissionDenied` de las denegaciones.

## Brechas registradas

| Id (plan.md) | Brecha | Riesgo aceptado | Cierre comprometido | Estado |
|---|---|---|---|---|
| III.2 | El cierre de sesión no genera registro de auditoría | No queda constancia de cuándo cierra sesión cada usuario | Feature del módulo de auditoría: receptor de `user_logged_in`, `user_logged_out` y `user_login_failed` | Abierta |
| III.2b | Las denegaciones 403 de las 4 listas del menú inicial no se auditan | No queda constancia de intentos de acceso sin permiso | Feature del módulo de auditoría: captura centralizada de `PermissionDenied` (middleware o `handler403`) | Abierta; **ampliada** por la feature 002 (ver abajo) |
| II.4 | Solo se protegen Inicio y las 4 listas; crear, editar, detalle, cambio de estado y exportar de Organización y Personas siguen sin protección | Acceso no autorizado a esas vistas por URL directa | Feature de seguridad: protección de todas las vistas de esos módulos | **Cerrada** el 2026-10-30 por la feature 002 (ver abajo) |

## Cumplimiento de las condiciones (constitución v1.1.0 §Gobernanza › Brechas preexistentes)

| Condición | Cómo se cumple |
|---|---|
| 1. Origen | III.2 y III.2b: el tratamiento (auditar) depende del módulo de auditoría, una capacidad transversal que aún no existe y que el Principio IV obliga a implementar una sola vez en su propio módulo. II.4: las vistas abiertas ya existían antes de la feature y la feature no las crea. |
| 2. No ampliación | La feature no crea operaciones sin protección: Inicio y las 4 listas que enlaza el menú pasan a exigir autenticación y permiso (FR-008a), y el cierre de sesión exige POST + CSRF (FR-024). No se modifican las vistas de II.4. |
| 3. Punto de enganche | El cierre de sesión usa `LogoutView` nativa, que emite `user_logged_out` (FR-024a). Las denegaciones usan `permission_required(raise_exception=True)` → `PermissionDenied`, interceptable con un middleware o `handler403`. |
| 4. Registro | Este documento, referenciado desde `specs/001-aside-navegacion-dinamica/plan.md` §Complexity Tracking. |
| 5. Vigencia | Fecha de revisión indicada en la cabecera. |

## Decisión

Se acepta implementar la feature 001 con las brechas anteriores registradas como **preexistentes**. Las condiciones son:

1. La feature 001 no debe ampliar ninguna de las brechas.
2. Las features de auditoría y de seguridad son compromisos que se priorizan inmediatamente después de la 001.
3. Esta decisión se revisa en la fecha indicada. Si para entonces no se han cerrado las brechas, el Responsable Técnico debe decidir entre priorizarlas o tramitar una enmienda.

## Actualización 2026-10-30: feature 002-seguridad-acceso-configuracion

Registro exigido por `specs/002-seguridad-acceso-configuracion/spec.md` FR-018 y referenciado desde su `plan.md` §Complexity Tracking.

### II.4: cerrada

| Campo | Valor |
|---|---|
| Fecha de cierre | 2026-10-30 |
| Feature | `002-seguridad-acceso-configuracion`, rama del mismo nombre. Commits `718c760` (US1: denegación por defecto) y `159f768` (US2: permiso por operación). |
| Cómo se cierra | Todo el sistema exige sesión salvo las 9 vistas públicas declaradas (`apps/usuarios/middleware.py`). Las 51 rutas de Organización, Personas, Ubicaciones y Usuarios exigen su permiso nativo `view`, `add` o `change` (`contracts/vistas-y-permisos.md` §2). |
| Verificación | `apps/usuarios/tests/test_acceso_global.py`: recorrido de todas las rutas sin sesión y matriz de las 51 rutas. `apps/common/tests/test_matriz_acceso.py`: toda ruta está clasificada. |

### III.2b: ampliada

Alcance nuevo: las denegaciones 403 de las 51 rutas protegidas, presentadas como página completa, aviso en ventana o notificación en tabla (`apps/usuarios/views/denegacion.py`), siguen sin auditarse.

| Condición | Cómo se cumple en la ampliación |
|---|---|
| 1. Origen | Auditar las denegaciones depende del módulo de auditoría, una capacidad transversal que aún no existe y que el Principio IV obliga a implementar una sola vez en su propio módulo. La feature 002 genera las denegaciones, pero no puede auditarlas sin crear ese módulo. |
| 2. No ampliación | La feature no deja ninguna operación sin protección: amplía el número de denegaciones porque protege lo que antes estaba abierto (cierra II.4), no porque relaje controles. |
| 3. Punto de enganche | Toda denegación es un `PermissionDenied` nativo lanzado por `permission_required(raise_exception=True)`, que pasa por `process_exception` de los middleware antes de llegar a `handler403`. Lo verifica `PermisosPorOperacionTests.test_la_denegacion_llega_al_punto_de_enganche_de_la_auditoria`. |
| 4. Registro | Esta sección y `specs/002-seguridad-acceso-configuracion/plan.md` §Complexity Tracking. |
| 5. Vigencia | Sin cambios: al entregarse la feature del módulo de auditoría, o el **2027-01-31**, lo que ocurra primero. |

III.2 (cierre de sesión sin auditar) no cambia.
