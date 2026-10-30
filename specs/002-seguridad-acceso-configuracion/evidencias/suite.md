# Evidencias: suite completa (T056)

**Fecha**: 2026-10-30 | **Rama**: `002-seguridad-acceso-configuracion` | **Comando**: `python manage.py test --noinput`

| Motor | Tests | Resultado | Duración |
|---|---|---|---|
| PostgreSQL 18.6 (`DB_ENGINE=postgresql`) | 167 | OK | 215 s |
| SQLite (`DB_ENGINE=sqlite`) | 167 | OK | 213 s |

Comprobaciones previas en ambos motores: `python manage.py check` sin avisos; `makemigrations --check` sin cambios.

## Incidencia corregida

La primera ejecución en PostgreSQL dio 3 errores (`StringDataRightTruncation`) en las pruebas que crean distritos judiciales. La causa estaba en la fábrica de pruebas `apps/common/tests/fabricas.py:crear_distrito_judicial`: sin siglas, el modelo las genera como "CSJ <NOMBRE>", que superaba los 20 caracteres del campo. SQLite no aplica esa longitud; PostgreSQL sí. La fábrica ahora asigna siglas cortas, y las dos suites quedaron en verde.

Observación fuera de alcance: el modelo `DistritoJudicial` genera las siglas automáticas sin acortarlas, así que un nombre de distrito judicial de más de 16 caracteres sin siglas explícitas fallaría al guardarse en PostgreSQL. Conviene revisarlo en una feature de Organización.

## Evolución del número de tests

| Momento | Tests |
|---|---|
| Base (feature 001) | 109 |
| Fases 1–2 (matriz y fábricas) | 113 |
| US1 | 123 |
| US2 | 144 |
| US4 | 160 |
| US3 | 167 |
