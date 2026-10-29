# Evidencia: recorrido con teclado (FR-028, SC-005) — completar en T054

**Navegador y versión**: Google Chrome Versión 156.0.8078.74 (Build oficial) (64 bits) 
**Fecha**: 29/10/2026
**Responsable**: ELIO CLIMACO
**Perfil usado**: `admin` (superusuario)

## Orden de foco

| # | Esperado (spec FR-028) | Observado | ¿Coincide? |
|---|---|---|---|
| 1 | Botón "Mostrar u ocultar el menú de navegación" (solo < 992 px) | Ninguno | Sí |
| 2 | Logo (enlace a Inicio) | Ninguno | Sí |
| 3 | Opciones del menú, en orden de aparición | Ninguno | Sí |
| 4 | Área de usuario (disparador "Menú de usuario de …") | Ninguno | Sí |

## Interacciones

| Tecla | Acción esperada | Resultado |
|---|---|---|
| Tab / Shift+Tab | Recorre los elementos enfocables | Sí |
| Enter / Espacio sobre el área de usuario | Abre el menú de usuario | Sí |
| Esc con el menú de usuario abierto | Lo cierra y devuelve el foco al disparador | Sí |
| Enter sobre "Cerrar sesión" | Envía el formulario y cierra la sesión | Sí |
| Foco visible | Contorno blanco de 2 px en cada elemento | Sí |

## Desviaciones encontradas y corrección aplicada

- **2026-10-29 (recorrido de T071, < 992 px)**: Esc no cerraba el menú desplegado. Se corrigió con un manejador Alpine.js en el `<aside>` que lo colapsa y devuelve el foco al botón, sin interferir con el Esc de los desplegables abiertos (research R15). Verificado por el responsable el 2026-10-29.
- **2026-10-29 (recorrido de T071, < 992 px)**: el menú de usuario se veía recortado, primero dentro de la barra y luego, con el aside desplegado, fuera del borde izquierdo (captura en `hallazgos/`). Se corrigió en `sidebar.css` (research R15) y el responsable lo verificó el 2026-10-29 con el menú colapsado y desplegado.
