# Evidencia: costo del menú lateral (SC-009) — T068

**Fecha**: 2026-10-29 · **Ejecutado por**: asistente de implementación (Claude) · **Entorno**: desarrollo (Windows, Python 3.13, Django 6.0, SQLite)

## Procedimiento

Variante del escenario 14 de quickstart.md:
- **Página**: `/organizacion/distritos-judiciales/`.
- **Usuario**: con `organizacion.view_distritojudicial` y el grupo "Administradores".
- **Cliente**: cliente de pruebas de Django en el mismo proceso, en lugar de solicitudes HTTP a `runserver`. Así se mide el tiempo de servidor sin la variación de red.
- Una solicitud de calentamiento y luego 20 solicitudes consecutivas.
- **Sin aside**: se vació temporalmente `templates/components/navigation/aside/base.html` y se ejecutó en un proceso aparte (para no reutilizar la caché de plantillas). Después se restauró el archivo.

## Resultados

| Variante | Media (ms) | Mediana (ms) | Consultas por página |
|---|---|---|---|
| Con aside | 12.86 | 12.47 | 7 |
| Sin aside | 13.19 | 12.07 | 6 |
| **Diferencia** | **−0.33** | **+0.40** | **+1** |

Mediciones individuales (ms):
- Con aside: 9.2 10.1 9.7 12.8 12.4 9.6 12.0 10.9 14.9 10.9 9.8 9.2 14.3 12.5 13.4 19.9 16.5 16.8 17.1 15.2
- Sin aside: 9.8 18.2 11.4 10.7 9.9 12.3 15.0 13.8 17.6 18.3 17.1 11.8 13.2 13.0 11.1 15.7 11.7 10.2 11.2 11.8

## Conclusión

SC-009 se cumple. La diferencia de tiempo está dentro del ruido de medición (≪ 20 ms) y el menú añade 1 consulta (≤ 3): la de su grupo principal. Los permisos ya estaban en caché porque `permission_required` de la vista los cargó antes. Sin esa caché, el máximo es 3 consultas, verificado por `test_consultas_acotadas_e_independientes_del_numero_de_items`.
