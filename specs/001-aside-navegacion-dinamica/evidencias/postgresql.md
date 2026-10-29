# Evidencia: suite contra PostgreSQL (constitución §Requisitos de testing) — T070

**Estado**: completada (2026-10-29).

## Preparación (una vez)

1. Instalar las dependencias: `pip install -r requirements.txt`. Incluye `psycopg[binary]==3.3.6`, que trae su propia `libpq` y no necesita cliente de PostgreSQL instalado.
2. Crear en PostgreSQL un rol con permiso para crear bases (Django crea y destruye la base de pruebas):
   ```sql
   CREATE ROLE erp_csjpasco LOGIN PASSWORD '<contraseña>' CREATEDB;
   CREATE DATABASE erp_csjpasco OWNER erp_csjpasco;
   ```
3. En `.env` (no versionado; plantilla en `.env.example`):
   ```
   DB_ENGINE=postgresql
   DB_NAME=erp_csjpasco
   DB_USER=erp_csjpasco
   DB_PASSWORD=<contraseña>
   DB_HOST=localhost
   DB_PORT=5432
   ```

## Ejecución

```bash
python manage.py check
python manage.py test --noinput
```

Para volver a SQLite en desarrollo, poner `DB_ENGINE=sqlite` (o quitar la variable).

## Resultado

| Campo | Valor |
|---|---|
| Versión de PostgreSQL | PostgreSQL 18.6 on x86_64-windows, compiled by msvc-19.44.35229, 64-bit |
| Driver | psycopg 3.3.6 (implementación `binary`, libpq 18.0.4) |
| Fecha | 2026-10-29 |
| Responsable | Ejecutado por el asistente de implementación (Claude) a pedido de ELIO CLIMACO, con la configuración de su `.env` |
| `manage.py check` | `System check identified no issues (0 silenced).` |
| Tests (encontrados / OK / fallos / errores) | 102 / 102 / 0 / 0 (`Ran 102 tests in 86.515s` · `OK`) |
| Observaciones | Base de pruebas `test_csjpasco`, creada y destruida por el runner; el rol tiene `CREATEDB`. La base principal tiene 29 migraciones sin aplicar; no se modificó, porque la suite usa su propia base. |
