# Evidencia de contraste (SC-006, FR-017, FR-030)

**Estado**: valores **calculados** con la fórmula de luminancia relativa de WCAG 2.1 a partir de los colores declarados en `sidebar.css`, `custom_color.css` y `tabler.min.css` (los colores `oklch` de Tabler se convirtieron a sRGB). **Pendiente (T055)**: medir en el navegador con DevTools o Colour Contrast Analyser y anotar abajo herramienta, fecha y resultado.

Tema: claro (aplicación). Fondo del menú: color institucional principal.

| Combinación | Primer plano | Fondo | Ratio calculado | Mínimo | AA |
|---|---|---|---|---|---|
| Texto e íconos de opciones | blanco (#FFFFFF) | fondo del menú (token `--institutional-primary`) | 7.29 : 1 | 4.5 : 1 | Sí |
| Títulos de sección | blanco (#FFFFFF) | fondo del menú (token `--institutional-primary`) | 7.29 : 1 | 4.5 : 1 | Sí |
| Opción al pasar el cursor | blanco (#FFFFFF) | fondo hover (blanco 10 %) (#AD3C38) | 6.03 : 1 | 4.5 : 1 | Sí |
| Opción actual (texto) | blanco (#FFFFFF) | fondo actual (negro 20 %) (#831E1B) | 9.69 : 1 | 4.5 : 1 | Sí |
| Marca lateral de la opción actual | blanco (#FFFFFF) | fondo actual (#831E1B) | 9.69 : 1 | 3 : 1 | Sí |
| Foco visible (contorno) | blanco (#FFFFFF) | fondo del menú (token `--institutional-primary`) | 7.29 : 1 | 3 : 1 | Sí |
| Foco visible sobre opción actual | blanco (#FFFFFF) | fondo actual (#831E1B) | 9.69 : 1 | 3 : 1 | Sí |
| Botón de menú (ícono) | blanco (#FFFFFF) | fondo del menú (token `--institutional-primary`) | 7.29 : 1 | 3 : 1 | Sí |
| Insignia neutra (texto) | institucional (token `--institutional-primary`) | blanco (#FFFFFF) | 7.29 : 1 | 4.5 : 1 | Sí |
| Insignia neutra (fondo vs menú) | blanco (#FFFFFF) | fondo del menú (token `--institutional-primary`) | 7.29 : 1 | 3 : 1 | Sí |
| Insignia advertencia (texto) | oscuro Tabler (#262626) | amarillo Tabler (#F59F00) | 7.09 : 1 | 4.5 : 1 | Sí |
| Insignia advertencia (fondo vs menú) | amarillo Tabler (#F59F00) | fondo del menú (token `--institutional-primary`) | 3.42 : 1 | 3 : 1 | Sí |
| Insignia informativa (texto) | oscuro Tabler (#262626) | blanco (#FFFFFF) | 15.13 : 1 | 4.5 : 1 | Sí |
| Insignia informativa (fondo vs menú) | blanco (#FFFFFF) | fondo del menú (token `--institutional-primary`) | 7.29 : 1 | 3 : 1 | Sí |
| Avatar (iniciales) | institucional (token `--institutional-primary`) | blanco (#FFFFFF) | 7.29 : 1 | 4.5 : 1 | Sí |
| Área de usuario: nombre y grupo | blanco (#FFFFFF) | fondo del menú (token `--institutional-primary`) | 7.29 : 1 | 4.5 : 1 | Sí |
| Menú de usuario desplegable (texto y fondo) | esquema oscuro de Tabler | esquema oscuro de Tabler | **medir en T055** | 4.5 : 1 | — |
| Logo: trazos grises | #D0D0D0 (#D0D0D0) | fondo del menú (token `--institutional-primary`) | 4.73 : 1 | 3 : 1 | Sí |
| Logo: texto dorado | #E8B20F (#E8B20F) | fondo del menú (token `--institutional-primary`) | 3.75 : 1 | 3 : 1 | Sí |

Mínimos: 4.5:1 para texto normal (WCAG 1.4.3); 3:1 para componentes de interfaz y gráficos (WCAG 1.4.11). El logotipo está exento de 1.4.3; se informa como referencia.

## Medición en navegador (completar en T055)

| Combinación | Herramienta | Ratio medido | AA | Fecha | Responsable |
|---|---|---|---|---|---|
| | | | | | |
