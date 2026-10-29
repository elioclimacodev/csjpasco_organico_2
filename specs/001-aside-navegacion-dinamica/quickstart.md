# Quickstart: validar la navegación lateral dinámica

**Feature**: 001-aside-navegacion-dinamica

Guía de validación de punta a punta. Detalles de las estructuras en [data-model.md](data-model.md) y de los contratos en [contracts/](contracts/).

## Requisitos previos

- Rama `001-aside-navegacion-dinamica` con la implementación completa.
- Entorno virtual activo, dependencias instaladas y `.env` configurado.
- Base de datos migrada: `python manage.py migrate`.

## 1. Verificaciones automáticas

```bash
python manage.py check                 # sin errores common.E1xx
python manage.py test apps.common apps.main apps.organizacion apps.personas apps.usuarios
```

La suite usa la base que fija `DB_ENGINE` en `.env` (research R17). Para forzar SQLite sin editar `.env`:

```bash
DB_ENGINE=sqlite python manage.py test --noinput
```

Antes de desplegar, repetir la suite con `DB_ENGINE=postgresql` (constitución, sección Testing; procedimiento en `evidencias/postgresql.md`).

**Resultado esperado**: `System check identified no issues` y todos los tests en verde.

## 2. Preparar perfiles de prueba (shell o Admin)

| Usuario | Permisos | Menú esperado |
|---|---|---|
| `sinpermisos` | ninguno | Solo "Inicio" + área de usuario |
| `organizacion` | `organizacion.view_distritojudicial`, `organizacion.view_materiajurisdiccional` | Inicio; sección Organización con Distritos y Materias (sin Órganos) |
| `admin` | superusuario | Todas las opciones |

## 3. Escenarios manuales

| # | Pasos | Resultado esperado | Requisitos |
|---|---|---|---|
| 1 | Abrir `/` sin sesión. | Redirige a iniciar sesión; no hay aside. | FR-001, FR-008a |
| 2 | Ingresar como `sinpermisos`. | Solo "Inicio"; ninguna sección; sin barra superior. | FR-006, FR-007, FR-026 |
| 3 | Como `sinpermisos`, escribir la URL `/organizacion/distritos-judiciales/`. | Respuesta 403 (acceso denegado). | FR-008, FR-008a |
| 4 | Ingresar como `organizacion`. | Sección "Organización" con 2 opciones; "Personas" y "Administración" ausentes. | FR-005, FR-007 |
| 5 | Abrir Distritos judiciales y luego el detalle de un distrito. | "Distritos judiciales" activo (fondo + marca lateral + negrita) en ambas páginas; un único `aria-current="page"`. | FR-020, SC-003 |
| 6 | Abrir el menú de usuario (con un usuario que pertenezca a un grupo y con otro sin grupos). | Iniciales, nombre completo y nombre del grupo principal (sin dato secundario si no tiene grupos); el número de documento no aparece como dato secundario; única opción "Cerrar sesión". | FR-021, FR-023 |
| 7 | Pulsar "Cerrar sesión". | Sesión cerrada; pantalla de inicio de sesión. | FR-024 |
| 8 | Con sesión iniciada, visitar `GET /usuarios/sesion/cerrar/` directamente. | La sesión **no** se cierra (405). | FR-024, SC-004 |
| 9 | Reducir la ventana a ancho móvil (< 992 px). | Menú colapsado; botón con etiqueta en español lo despliega. | FR-010, FR-029 |
| 10 | Recorrer el aside solo con Tab/Shift+Tab/Enter/Espacio/Esc. | Se llega a todas las opciones y al menú de usuario; foco visible blanco. | FR-028, SC-005 |
| 11 | Revisar con lector de pantalla (NVDA). | Región "Menú principal"; íconos no anunciados; ítem actual anunciado como "página actual". | FR-028 |
| 12 | Usar un filtro o la paginación de una lista (petición HTMX). | El fragmento se actualiza y el aside no se duplica. | Edge case HTMX |
| 13 | Medir el contraste (DevTools o Colour Contrast Analyser) de texto, ícono, activo y foco. | ≥ 4.5:1 en texto y ≥ 3:1 en indicadores (valores en research R9). | FR-030, SC-006 |
| 14 | Medir la carga: 20 solicitudes consecutivas a `/organizacion/distritos-judiciales/` con el aside y 20 con el include del aside comentado temporalmente, en el mismo entorno; comparar las medias del tiempo de respuesta del servidor. | Diferencia ≤ 20 ms; consultas extra ≤ 3 (también lo cubre `assertNumQueries`). | SC-009 |

### Evidencia que se conserva

Los escenarios manuales que no cubren las pruebas automáticas dejan evidencia en `specs/001-aside-navegacion-dinamica/evidencias/`, versionada con la feature:

| Escenario | Evidencia | Archivo |
|---|---|---|
| 9 (móvil) | Capturas a 375 px (menú colapsado y desplegado) y a ≥ 992 px | `movil-375-colapsado.png`, `movil-375-desplegado.png`, `escritorio-1280.png` |
| 10 (teclado) | Registro del recorrido: orden de foco observado frente al esperado (FR-028), teclas probadas y resultado | `teclado.md` |
| 11 (lector de pantalla) | Lector y versión usados, y textos anunciados en la región, el ítem actual y el menú de usuario | `lector-pantalla.md` |
| 13 (contraste) | Tabla con cada combinación medida (primer plano, fondo, ratio, AA sí/no) y la herramienta usada | `contraste.md` |
| 14 (carga) | Las 20 + 20 mediciones, las medias y la diferencia | `rendimiento.md` |

## 4. Declarar una opción nueva (prueba de extensibilidad, SC-008)

1. En una app existente, editar o crear `apps/<app>/menu.py` y registrar un `MenuItem` según [contracts/menu-declaration.md](contracts/menu-declaration.md).
2. Ejecutar `python manage.py check` y corregir cualquier `common.E1xx`.
3. Recargar como un usuario con el permiso declarado: la opción aparece. Sin el permiso, no aparece.
4. Verificar con `git diff --stat` que solo cambiaron archivos del módulo que declara la opción (ninguno bajo `templates/components/navigation/aside/`, `apps/common/` ni otros módulos), según SC-008.
