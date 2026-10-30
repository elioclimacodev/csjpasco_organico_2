# Preparación del despliegue: permisos por grupo y rotación de la clave

**Feature**: 002-seguridad-acceso-configuracion | **Fecha**: 2026-10-30

**Origen**: spec §Assumptions ("Preparación del despliegue"), FR-017; plan §Impacto en despliegue.

**Estado**: **pendiente de aprobación** del Responsable Técnico.

> Hoy las operaciones se usan sin control. Tras desplegar esta feature, un usuario sin permisos solo verá Inicio, con el aviso "Su cuenta aún no tiene permisos asignados…". Antes de habilitar el acceso, esta asignación debe aprobarse y aplicarse en el entorno, desde el panel de administración.

## 1. Grupos existentes

| Entorno | Grupos | Fuente |
|---|---|---|
| Desarrollo (SQLite) | Ninguno. 9 usuarios activos, 2 superusuarios. | Consulta del 2026-10-30 |
| Producción (PostgreSQL) | _Por completar_ | Ejecutar en el servidor: `python manage.py shell -c "from django.contrib.auth.models import Group; print(list(Group.objects.values_list('name', flat=True)))"` |

## 2. Propuesta de grupos y permisos

Permisos nativos: `view` (lista, detalle y exportación), `add` (registro) y `change` (modificación, inactivación y reactivación). Matriz completa: [contracts/vistas-y-permisos.md](contracts/vistas-y-permisos.md) §2.

Marque con ✔ los permisos que corresponden a cada grupo. Los grupos propuestos son orientativos: renómbrelos o sustitúyalos por los existentes en producción.

| Entidad (app.modelo) | Consulta | Registro | Administración |
|---|---|---|---|
| Distritos judiciales (`organizacion.distritojudicial`) | view | view, add, change | view, add, change |
| Materias jurisdiccionales (`organizacion.materiajurisdiccional`) | view | view, add, change | view, add, change |
| Órganos jurisdiccionales (`organizacion.organojurisdiccional`) | view | view, add, change | view, add, change |
| Sedes judiciales (`organizacion.sedejudicial`) | view | view, add, change | view, add, change |
| Personas (`personas.persona`) | view | view, add | view, add |
| Países (`ubicaciones.pais`) | view | view | view, add, change |
| Departamentos (`ubicaciones.departamento`) | view | view | view, add, change |
| Provincias (`ubicaciones.provincia`) | view | view | view, add, change |
| Distritos (`ubicaciones.distrito`) | view | view | view, add, change |
| Usuarios (`usuarios.usuario`) | — | — | view |

Notas:
- El permiso de consulta del menú lateral coincide con el de la vista destino (spec FR-010). Quien no tiene `view` de una entidad no ve su opción en el menú.
- En rutas anidadas se exige solo el permiso de la entidad de la ruta. Por ejemplo, las provincias de un departamento exigen `view_provincia`, no `view_departamento` (decisión CHK003). Para llegar navegando desde la lista padre, el grupo necesita también el `view` del padre.
- Los superusuarios no necesitan grupos.

## 3. Asignación de usuarios a grupos

| Usuario (número de documento) | Grupo(s) |
|---|---|
| _Por completar_ | |

## 4. Aviso a los usuarios por la rotación de la clave (FR-017)

Texto propuesto para comunicar antes del despliegue:

> Con motivo de una actualización de seguridad del ERP, el [fecha] a las [hora] se cerrarán todas las sesiones abiertas. Deberá iniciar sesión nuevamente. Los enlaces de activación de cuenta y de restablecimiento de contraseña enviados antes de esa hora dejarán de ser válidos; si tenía uno pendiente, solicite uno nuevo desde la página de inicio de sesión. Si después de iniciar sesión no puede acceder a alguna opción que usaba, solicite los permisos al administrador del sistema.

## 5. Lista de verificación previa al despliegue

- [ ] Grupos y permisos de §2 aprobados por el Responsable Técnico.
- [ ] Asignación de usuarios de §3 completada.
- [ ] `SECRET_KEY` nueva generada para producción (no reutilizar la de desarrollo ni la del historial de git).
- [ ] `DEBUG=false`, `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` definidos; transporte seguro activado detrás de HTTPS (`.env.example`).
- [ ] Aviso de §4 comunicado a los usuarios.
- [ ] Permisos aplicados en el panel de administración **antes** de habilitar el acceso a los usuarios.

## Aprobación

| Responsable Técnico | Fecha | Firma / conformidad |
|---|---|---|
| ELIO CLIMACO| 30/10/2026 | CONFORME |
