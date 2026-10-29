# Evidencia: suite contra PostgreSQL (constitución §Requisitos de testing) — T070

**Estado**: pendiente. Requiere un servidor PostgreSQL accesible.

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

## Resultado (completar)

| Campo | Valor |
|---|---|
| Versión de PostgreSQL | |
| Fecha | |
| Responsable | |
| `manage.py check` | |
| Tests (encontrados / OK / fallos / errores) | |
| Observaciones | |
