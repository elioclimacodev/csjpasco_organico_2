# Evidencia: extensibilidad del menú (SC-008, US5-1, US5-4) — T057

**Fecha**: 2026-10-29 · **Ejecutado por**: asistente de implementación (Claude), en la rama `001-aside-navegacion-dinamica`
**Procedimiento**: quickstart.md §4

## 1. Declaración temporal

Se añadió al final de `apps/personas/menu.py`, sin tocar ningún otro archivo:

```python
registry.register_item(MenuItem(
    id='personas_nueva',
    label='Registrar persona',
    section='personas',
    url_name='personas:create',
    icon='users',
    permissions=('personas.add_persona',),
    order=20,
))
```

## 2. Verificación automática

`python manage.py check` → `System check identified no issues (0 silenced).`

## 3. Visibilidad según permisos

`build_sidebar` sobre una base de pruebas:

| Usuario | Ítems visibles |
|---|---|
| Con `personas.add_persona` y `personas.view_persona` | `inicio`, `personas`, `personas_nueva` |
| Solo con `personas.view_persona` | `inicio`, `personas` |

La opción nueva aparece en la sección "Personas", en la posición declarada (`order=20`, después de "Personas"), solo para quien tiene el permiso.

## 4. Archivos modificados (`git diff --stat`)

```
apps/personas/menu.py | 11 +++++++++++
```

Ningún archivo en `templates/components/navigation/aside/`, `apps/common/` ni en otros módulos cambió por la opción. (En ese momento el `diff` también mostraba `apps/common/tests/test_sidebar_render.py`, que correspondía al test de T056 aún sin commit y no a la opción temporal.)

## 5. Reversión

`apps/personas/menu.py` se restauró a su contenido original (`git diff` sin cambios en ese archivo).

**Resultado**: SC-008 cumplido. Agregar una opción solo modifica el módulo que la declara.
