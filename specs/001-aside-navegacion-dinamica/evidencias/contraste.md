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

Navegador: Chrome · Tema: claro

| Combinación | Herramienta | Ratio medido | AA | Fecha | Responsable |
|---|---|---|---|---|---|
| Texto e íconos de opciones (no activas) | DevTools (script de consola, valores computados) | 4.28 : 1 | No | 29/10/2026 | ___ |
| Títulos de sección | DevTools (script de consola, valores computados) | 2.81 : 1 | No | 29/10/2026 | ___ |
| Opción al pasar el cursor | Muestreo de píxeles de captura (blanco sobre 173,60,57) | 6.03 : 1 | Sí | 29/10/2026 | ___ |
| Opción actual (texto) | DevTools (script de consola, valores computados) | 7.27 : 1 | Sí | 29/10/2026 | ___ |
| Marca lateral de la opción actual | Muestreo de píxeles de captura (blanco sobre 164,38,34) | 7.29 : 1 (*) | Sí | 29/10/2026 | ___ |
| Foco visible (contorno) | Muestreo de píxeles de captura (blanco sobre 164,38,34) | 7.29 : 1 | Sí | 29/10/2026 | ___ |
| Avatar (iniciales) | DevTools (script de consola, valores computados) | 7.29 : 1 | Sí | 29/10/2026 | ___ |
| Área de usuario: nombre y grupo | DevTools (script de consola, valores computados) | 4.28 : 1 | No | 29/10/2026 | ___ |
| Menú de usuario desplegable (texto y fondo) | DevTools (script de consola, valores computados) | 12.01 : 1 | Sí | 29/10/2026 | ___ |
| Logo: trazos grises (referencia, exento de 1.4.3) | Muestreo de píxeles de captura (208,208,208 sobre 164,38,34) | 4.72 : 1 | Sí | 29/10/2026 | ___ |
| Logo: texto dorado (referencia, exento de 1.4.3) | Muestreo de píxeles de captura (232,178,15 sobre 164,38,34) | 3.75 : 1 | Sí | 29/10/2026 | ___ |

Observaciones:
- Fallan las opciones no activas, los títulos de sección y el nombre de usuario: Tabler los atenúa pese a `color: #fff` en `sidebar.css` (≈ blanco al 70 % y al 50 %). 

## Corrección aplicada (2026-10-29)

**Causa**: especificidad CSS. Las reglas de `sidebar.css` usaban `.sidebar-institucional` (0,1,0) y perdían frente a las de Tabler:

| Fallo medido | Regla de Tabler que prevalecía | Efecto |
|---|---|---|
| Opciones no activas y área de usuario (4.28 : 1) | `.navbar[data-bs-theme=dark]` (0,2,0) redefine `--tblr-navbar-color` como blanco al 70 % | Texto al 70 % |
| Títulos de sección (2.81 : 1) | `.navbar-vertical[class*=navbar-expand] .navbar-nav .nav-section-title` (0,4,0): `color-mix(… var(--tblr-navbar-color) 70%)` | 70 % de un 70 % ≈ 49 % |
| Opción actual (7.27 : 1 en lugar de 9.69 : 1) | La misma regla de variables impone su `--tblr-navbar-active-bg` | Sin fondo oscurecido |

**Corrección**: los selectores de `sidebar.css` anteponen `.navbar-vertical` (por ejemplo, `.navbar-vertical.sidebar-institucional[data-bs-theme="dark"]` y `.navbar-vertical.sidebar-institucional .navbar-nav .nav-section-title`). Así igualan o superan la especificidad de Tabler, y como `sidebar.css` se carga después, prevalecen. Lo protege el test `test_selectores_con_especificidad_suficiente_frente_a_tabler`.

**Nueva medición (2026-10-29)**: el responsable (ELIO CLIMACO) volvió a medir tras la corrección y confirmó que las combinaciones que fallaban (opciones no activas, títulos de sección, nombre del área de usuario) y la opción actual cumplen AA. Los ratios medidos no se anotaron; según el cálculo, los valores esperados son 7.29 : 1 (texto sobre el fondo) y 9.69 : 1 (opción actual).



