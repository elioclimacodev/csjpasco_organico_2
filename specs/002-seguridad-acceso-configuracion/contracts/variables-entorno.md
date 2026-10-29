# Contrato: variables de entorno

**Proveedor**: `config/entorno.py` (lectura) y `config/settings.py` (uso). **Plantilla**: `.env.example`.

| Variable | Obligatoria | Por defecto | Formato | Error si… |
|---|---|---|---|---|
| `SECRET_KEY` | Sí | — | texto | falta o está vacía |
| `DEBUG` | No | `False` | booleano | valor no reconocido |
| `ALLOWED_HOSTS` | Sí si `DEBUG` es falso | con `DEBUG`: `localhost,127.0.0.1` | lista (comas) | vacía con `DEBUG` falso |
| `CSRF_TRUSTED_ORIGINS` | No | vacía | lista de orígenes con esquema | un elemento sin `http://` o `https://` |
| `SESSION_COOKIE_SECURE` | No | `True` | booleano | valor no reconocido |
| `CSRF_COOKIE_SECURE` | No | `True` | booleano | valor no reconocido |
| `SECURE_SSL_REDIRECT` | No | `False` | booleano | valor no reconocido |
| `SECURE_HSTS_SECONDS` | No | `0` | entero ≥ 0 | no entero o negativo |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | No | `False` | booleano | valor no reconocido |
| `SECURE_HSTS_PRELOAD` | No | `False` | booleano | valor no reconocido |
| `SECURE_PROXY_SSL_HEADER` | No | sin definir (`None`) | `CABECERA,valor` | distinto de 2 elementos |
| `DB_ENGINE`, `DB_*` | (feature 001) | — | — | — |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | (existentes) | — | — | — |

- **Booleanos**: `true`, `false`, `1`, `0`, `sí`, `si`, `no` (sin distinguir mayúsculas).
- **Cadena vacía**: equivale a no definida.

**Mensajes de error**: en español, con el nombre de la variable y la indicación "Revise el archivo .env (ver .env.example)".

**Reglas de coherencia** (spec FR-015 y FR-016a; se documentan en `.env.example`):
- Detrás de un proxy HTTPS, `CSRF_TRUSTED_ORIGINS` debe incluir `https://<host>` para cada host de `ALLOWED_HOSTS` que reciba formularios.
- Si `SECURE_SSL_REDIRECT=true` detrás de un proxy que termina TLS, hay que definir `SECURE_PROXY_SSL_HEADER`; si no, cada solicitud se redirige indefinidamente.

**Despliegue (FR-017)**: cada entorno genera una `SECRET_KEY` nueva con `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`. La clave del historial de git se da por comprometida. Al rotarla se cierran todas las sesiones y dejan de valer los enlaces pendientes de activación y de restablecimiento de contraseña; hay que avisar a los usuarios.

**Producción típica detrás de un proxy HTTPS**:

```
DEBUG=false
ALLOWED_HOSTS=erp.ejemplo.pe
CSRF_TRUSTED_ORIGINS=https://erp.ejemplo.pe
SECURE_SSL_REDIRECT=true
SECURE_HSTS_SECONDS=31536000
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

El dominio es ilustrativo; los valores reales los fija el procedimiento de despliegue.
