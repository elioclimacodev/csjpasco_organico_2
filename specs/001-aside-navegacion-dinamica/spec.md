# Feature Specification: Navegación lateral dinámica filtrada por permisos (aside Tabler 1.7.1)

**Feature Branch**: `001-aside-navegacion-dinamica`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "Modernizar el componente transversal de navegación lateral (aside) del ERP al patrón 'navbar vertical' de Tabler.io 1.7.1, configurado desde el backend, dinámico y filtrado por permisos del usuario. Conservar todas las capacidades del patrón de referencia; menú de usuario solo con 'Cerrar sesión'; 'Personalizar' y demás opciones del menú de usuario quedan para features futuras." (descripción completa en el historial de `/speckit-specify`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver solo las opciones a las que tengo acceso (Priority: P1)

Como usuario autenticado del ERP, al ingresar a cualquier página interna veo un menú lateral con las opciones reales del sistema, en español, agrupadas por secciones, y solo aquellas para las que tengo permiso. No veo enlaces de demostración ni opciones que me llevarían a una página de acceso denegado.

**Why this priority**: Es el valor central de la feature: hoy el menú muestra contenido de demostración que no conduce a ninguna funcionalidad real. Sin esta historia el aside no sirve para navegar el ERP. Además aplica el mínimo privilegio en la presentación (Principio II).

**Independent Test**: Crear dos usuarios con permisos distintos (por ejemplo, uno con permiso de consulta de Distritos judiciales y otro sin él), ingresar con cada uno y comprobar que el menú de cada uno muestra exactamente las opciones correspondientes a sus permisos.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con permiso de consulta de Distritos judiciales, **When** abre cualquier página interna, **Then** el menú lateral muestra la opción "Distritos judiciales" dentro de su sección.
2. **Given** un usuario autenticado sin ese permiso, **When** abre cualquier página interna, **Then** la opción "Distritos judiciales" no aparece en el menú.
3. **Given** una opción declarada sin permiso requerido y sin marcarse como visible para todo usuario autenticado, **When** cualquier usuario abre una página interna, **Then** esa opción no aparece (denegación por defecto).
4. **Given** un usuario sin permiso sobre ninguna opción de una sección o desplegable, **When** abre una página interna, **Then** esa sección o desplegable no aparece, ni siquiera su título.
5. **Given** un usuario que no ve una opción en el menú, **When** escribe directamente la dirección de esa página, **Then** la página aplica su propia verificación de autorización y deniega el acceso (el menú no sustituye la autorización).
6. **Given** un visitante no autenticado, **When** accede a una página pública (por ejemplo, inicio de sesión), **Then** el menú lateral no se muestra.

---

### User Story 2 - Saber dónde estoy (Priority: P1)

Como usuario, al navegar por el ERP el menú me indica claramente la opción correspondiente a la página actual, incluso si está dentro de un desplegable, sin depender solo del color, y esta indicación es perceptible por lectores de pantalla.

**Why this priority**: Navegación consistente y jerarquía visual clara son exigencias de la constitución; hoy el estado activo está fijo en el código y siempre señala una opción de demostración.

**Independent Test**: Navegar a la lista de Distritos judiciales y luego a la de Materias jurisdiccionales y verificar que en cada caso solo la opción correspondiente (y su grupo padre) quedan marcados como actuales.

**Acceptance Scenarios**:

1. **Given** el usuario está en la página de una opción de primer nivel, **When** se muestra el menú, **Then** esa opción aparece marcada como actual y anunciada como "página actual" a tecnologías de asistencia.
2. **Given** el usuario está en una página que corresponde a una opción dentro de un desplegable, **When** se muestra el menú, **Then** la opción hija aparece como actual y su desplegable padre aparece señalado como activo y abierto.
3. **Given** el usuario está en una página secundaria de un mantenimiento (por ejemplo, detalle o edición de un registro), **When** se muestra el menú, **Then** la opción del mantenimiento correspondiente aparece como actual.
4. **Given** el usuario está en una página sin opción de menú asociada, **When** se muestra el menú, **Then** ninguna opción aparece marcada como actual.

---

### User Story 3 - Identificarme y cerrar sesión de forma segura (Priority: P1)

Como usuario autenticado, en la parte inferior del menú lateral veo mi identificación (avatar, nombre completo y un dato secundario) y, al abrirla, encuentro la opción "Cerrar sesión", que finaliza mi sesión de forma segura.

**Why this priority**: Cerrar sesión es un flujo esencial según la constitución; hoy el menú muestra un usuario ficticio y un enlace "Logout" que no cierra la sesión.

**Independent Test**: Ingresar con un usuario, verificar que su nombre aparece en el área de usuario, usar "Cerrar sesión" y comprobar que se vuelve a la pantalla de inicio de sesión y que las páginas internas ya no son accesibles sin autenticarse.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** se muestra el menú lateral, **Then** el área de usuario muestra su nombre completo y un dato secundario propio (no datos fijos ni de ejemplo).
2. **Given** un usuario sin fotografía registrada, **When** se muestra el área de usuario, **Then** el avatar muestra sus iniciales.
3. **Given** el usuario abre su menú de usuario, **When** elige "Cerrar sesión", **Then** su sesión termina y es dirigido a la pantalla de inicio de sesión.
4. **Given** un tercero que intenta provocar el cierre de sesión mediante un simple enlace o una solicitud no originada en el formulario del sistema, **When** dicha solicitud llega, **Then** la sesión NO se cierra.
5. **Given** el menú de usuario, **When** se despliega, **Then** contiene únicamente la opción "Cerrar sesión" en esta versión.

---

### User Story 4 - Usar el menú en cualquier dispositivo y solo con teclado (Priority: P2)

Como usuario en móvil, tablet o escritorio, o que navega solo con teclado o con lector de pantalla, puedo abrir, recorrer y usar todo el menú lateral.

**Why this priority**: La constitución exige diseño mobile first y WCAG 2.1 AA; es imprescindible pero se apoya en las historias anteriores.

**Independent Test**: En un ancho de pantalla móvil, abrir el menú con el botón correspondiente y llegar a una opción anidada usando solo el teclado; repetir con un lector de pantalla y verificar que las etiquetas se anuncian en español.

**Acceptance Scenarios**:

1. **Given** una pantalla de ancho móvil, **When** se carga una página interna, **Then** el menú aparece colapsado y existe un botón con etiqueta accesible en español para mostrarlo u ocultarlo.
2. **Given** un usuario que solo usa teclado, **When** recorre el menú, **Then** puede abrir desplegables y submenús de segundo nivel, activar cualquier opción y abrir el menú de usuario, con un orden de foco lógico y foco visible.
3. **Given** un lector de pantalla, **When** recorre el menú, **Then** la región de navegación tiene un nombre en español, los íconos decorativos no se anuncian y las opciones externas indican que abren en una pestaña nueva.
4. **Given** el tema claro del sistema, **When** se muestra el menú, **Then** textos, íconos, logo y estado actual cumplen el contraste mínimo WCAG AA.

---

### User Story 5 - Incorporar opciones de un módulo sin tocar el componente (Priority: P2)

Como desarrollador de un módulo del ERP, puedo declarar las secciones y opciones de mi módulo (con su permiso, ícono, insignia, orden y submenús) en la configuración de ese módulo, y estas aparecen en el menú sin modificar las plantillas del componente ni la configuración de otros módulos.

**Why this priority**: Garantiza que el menú sea un componente transversal único y mantenible (Principio IV); no aporta valor visible al usuario final de inmediato.

**Independent Test**: Declarar una opción nueva en un módulo, sin editar las plantillas del componente, y verificar que aparece para un usuario con el permiso declarado y no aparece para uno sin él.

**Acceptance Scenarios**:

1. **Given** un módulo declara una nueva opción con su permiso, **When** un usuario con ese permiso abre una página interna, **Then** la opción aparece en la sección y posición declaradas.
2. **Given** dos módulos declaran opciones para la misma sección, **When** se muestra el menú, **Then** ambas aparecen en esa sección ordenadas según el orden declarado.
3. **Given** una opción que declara insignia, ícono, enlace externo, columnas o submenú de segundo nivel, **When** se muestra el menú, **Then** cada capacidad se presenta conforme al patrón de navegación vertical de referencia.
4. **Given** una opción mal declarada (por ejemplo, con una ruta inexistente), **When** se ejecutan las verificaciones del proyecto, **Then** el error se detecta antes de llegar a producción, y en ejecución la opción no se muestra en lugar de romper la página.

---

### Edge Cases

- Usuario autenticado sin ningún permiso: el menú muestra solo las opciones declaradas como visibles para todo usuario autenticado (por ejemplo, "Inicio") y el área de usuario.
- Superusuario: ve todas las opciones declaradas, porque posee todos los permisos.
- Usuario inactivo o sesión expirada: no llega a ver el menú; es redirigido al inicio de sesión.
- Usuario sin nombre completo registrado: el área de usuario muestra su nombre de usuario como nombre principal y las iniciales se derivan de él.
- Opción que exige varios permisos: se muestra solo si el usuario tiene todos los permisos declarados.
- Desplegable cuyos hijos quedan todos ocultos: el desplegable no se muestra; una sección sin opciones visibles tampoco muestra su título.
- Mantenimiento cuya lista depende de otro registro (por ejemplo, Sedes judiciales, cuya lista pertenece a un distrito judicial): no se ofrece como opción directa del menú mientras no exista una página de acceso independiente.
- Etiquetas largas: se ajustan sin desbordar el ancho del menú ni ocultar la insignia.
- Página cargada parcialmente (fragmentos dinámicos): el menú no se duplica ni se vuelve a insertar dentro del contenido.
- Opciones con el mismo orden: se muestran en un orden estable y predecible (por ejemplo, alfabético por etiqueta).

## Requirements *(mandatory)*

### Functional Requirements

**Contenido y filtrado**

- **FR-001**: El sistema DEBE mostrar el menú lateral en todas las páginas internas para usuarios autenticados y NO DEBE mostrarlo a visitantes no autenticados.
- **FR-002**: El contenido del menú (secciones, opciones, submenús, íconos, insignias, permisos y orden) DEBE provenir de una configuración declarada en el servidor y versionada con el código; NO DEBE escribirse de forma fija en las plantillas ni almacenarse en la base de datos.
- **FR-003**: Cada módulo DEBE poder declarar sus propias secciones y opciones; un único mecanismo compartido DEBE reunirlas, ordenarlas y entregarlas al componente. NO DEBE existir una segunda vía para definir el menú.
- **FR-004**: Cada opción DEBE poder declarar: identificador único, etiqueta en español, destino (ruta interna por nombre o dirección externa), ícono opcional, insignia opcional (texto y variante), permiso(s) requerido(s), orden y, opcionalmente, opciones hijas.
- **FR-005**: El sistema DEBE mostrar una opción solo si el usuario posee todos los permisos que esta declara, usando el sistema nativo de permisos y grupos.
- **FR-006**: Denegación por defecto: una opción sin permiso declarado o cuyo permiso no pueda verificarse NO DEBE mostrarse, salvo que se declare explícitamente como visible para todo usuario autenticado.
- **FR-007**: Un desplegable o submenú sin opciones hijas visibles, y una sección sin opciones visibles, NO DEBEN mostrarse.
- **FR-008**: Ocultar una opción DEBE ser solo presentación; cada página DEBE seguir verificando su propia autorización con independencia del menú. Hoy las páginas de destino del menú inicial (Inicio, Distritos judiciales, Materias jurisdiccionales, Órganos jurisdiccionales y Personas) no verifican autenticación ni permisos; solo la lista de Usuarios lo hace.
- **FR-008a**: Las páginas de destino del menú inicial (Inicio y las páginas de lista de Distritos judiciales, Materias jurisdiccionales, Órganos jurisdiccionales y Personas) DEBEN exigir sesión autenticada y, salvo Inicio, el mismo permiso de consulta que declara su opción de menú. Un usuario no autenticado DEBE ser dirigido al inicio de sesión; un usuario autenticado sin permiso DEBE recibir una denegación de acceso. Las demás vistas de esos módulos (crear, editar, detalle, cambio de estado, exportar) quedan fuera de alcance y se protegerán en una feature de seguridad posterior.
- **FR-009**: Una opción cuyo destino interno no pueda resolverse NO DEBE romper la página; DEBE omitirse y el error DEBE detectarse en las verificaciones automáticas del proyecto.

**Capacidades del componente (patrón navbar vertical Tabler 1.7.1)**

- **FR-010**: Botón para mostrar u ocultar el menú en pantallas pequeñas, con etiqueta accesible en español.
- **FR-011**: Logo institucional enlazado a la página de inicio, servido como imagen institucional con texto alternativo en español y legible sobre el fondo del menú.
- **FR-012**: Títulos de sección para agrupar opciones.
- **FR-013**: Opción simple de primer nivel con ícono y etiqueta.
- **FR-014**: Opción desplegable de primer nivel con submenú.
- **FR-015**: Submenú presentado en una o varias columnas, según se declare.
- **FR-016**: Submenú anidado de segundo nivel dentro de un desplegable.
- **FR-017**: Insignia opcional por opción, con texto en español; el color NO DEBE ser el único medio para comunicar su significado.
- **FR-018**: Ícono opcional también en opciones de submenú.
- **FR-019**: Opciones con destino externo que abren en una pestaña nueva, sin dar acceso a la ventana de origen, e indican de forma accesible que abren en pestaña nueva.
- **FR-020**: Estado actual calculado en el servidor a partir de la página actual (incluidas sus páginas secundarias): la opción actual se marca y se anuncia como página actual, y su desplegable padre se marca como activo y se muestra abierto.
- **FR-021**: Área de usuario en la parte inferior del menú, con avatar, nombre completo y un dato secundario del usuario autenticado, y un menú desplegable hacia arriba. Sin fotografía, el avatar DEBE mostrar las iniciales.
- **FR-022**: Zona lateral adicional (reservada para "Personalizar") prevista en la estructura del componente, sin contenido ni presencia visible en esta feature.

**Menú de usuario y cierre de sesión**

- **FR-023**: El menú de usuario DEBE contener únicamente la opción "Cerrar sesión" en esta feature.
- **FR-024**: "Cerrar sesión" DEBE ejecutarse mediante un envío de formulario protegido contra solicitudes falsificadas entre sitios; una simple navegación o enlace NO DEBE cerrar la sesión. Tras cerrar sesión, el usuario DEBE llegar a la pantalla de inicio de sesión.
- **FR-024a**: El cierre de sesión DEBE realizarse mediante el mecanismo nativo de cierre de sesión, de modo que emita el evento estándar de cierre de sesión al que se enganchará el futuro módulo de auditoría. Esta feature NO crea registros de auditoría; la auditoría del cierre de sesión (Principio III) se entregará con la feature del módulo de auditoría.
- **FR-025**: Las opciones del menú de usuario DEBEN provenir de la misma configuración del servidor, de modo que features futuras puedan agregar opciones (Perfil, Configuración, Ayuda, etc.) sin modificar las plantillas del componente.
- **FR-026**: La navegación y el menú de usuario DEBEN existir en un único lugar de la interfaz: el aside. Los layouts que incluyen el aside NO DEBEN mostrar la barra superior (ni su menú horizontal de demostración, ni su menú de usuario, ni sus utilidades de tema, notificaciones o menú de aplicaciones) en ningún tamaño de pantalla.

**Presentación, accesibilidad y limpieza**

- **FR-027**: Todos los textos visibles y etiquetas accesibles del menú DEBEN estar en español, con tono formal.
- **FR-028**: El menú DEBE ser una región de navegación con nombre accesible en español; los íconos decorativos NO DEBEN anunciarse; todo el menú DEBE poder usarse solo con teclado, con orden de foco lógico y foco visible (WCAG 2.1 AA).
- **FR-029**: El menú DEBE ser responsive con enfoque mobile first (escritorio, tablet, móvil).
- **FR-030**: El menú DEBE tener como único fondo el color institucional principal, referenciado mediante los tokens institucionales existentes (sin repetir su valor), eliminando el conflicto actual entre dos fondos. Textos e íconos DEBEN ser claros y cumplir el contraste WCAG AA sobre ese fondo (incluidos los submenús, el logo y el área de usuario). El estado actual DEBE distinguirse con un cambio de fondo más un indicador no cromático (por ejemplo, peso de fuente o marca lateral), no solo por color.
- **FR-031**: Las plantillas del componente NO DEBEN contener estilos inline, y el servidor NO DEBE construir HTML ni estilos en código para el menú.
- **FR-032**: El componente NO DEBE requerir JavaScript propio del proyecto; solo el comportamiento incorporado del design system (colapso y desplegables).
- **FR-033**: Todo el contenido de demostración del design system y los elementos propios de la barra superior (botones de repositorio y patrocinio, modo oscuro, notificaciones, menú de aplicaciones) DEBEN eliminarse del menú lateral.
- **FR-034**: El componente DEBE seguir siendo el único menú lateral del sistema y los layouts DEBEN seguir incluyéndolo de la misma forma; los layouts sobrantes ("base_form copy" y "base_page copy") DEBEN retirarse si no están en uso.

**Contenido inicial**

- **FR-035**: El menú inicial DEBE contener solo opciones reales con página de acceso independiente:
  - "Inicio" (visible para todo usuario autenticado).
  - Sección "Organización": "Distritos judiciales", "Materias jurisdiccionales" y "Órganos jurisdiccionales", cada una con su permiso de consulta.
  - Sección "Personas": "Personas", con su permiso de consulta.
  - Sección "Administración": "Usuarios", con su permiso de consulta.
  - Los mantenimientos sin página de lista independiente (por ejemplo, Cortes de justicia y Sedes judiciales) se incorporarán cuando la tengan.

### Key Entities *(include if feature involves data)*

- **Sección de menú**: agrupación con título visible, orden y opciones. Se muestra solo si tiene al menos una opción visible.
- **Opción de menú**: entrada navegable con identificador, etiqueta, destino (interno o externo), ícono, insignia, permisos requeridos, indicador "visible para todo usuario autenticado", orden y opciones hijas (hasta dos niveles bajo el primer nivel, con presentación en columnas opcional).
- **Insignia**: texto breve en español con una variante visual.
- **Opción de menú de usuario**: acción disponible en el área de usuario; puede ser navegación o una acción que requiere envío protegido (como "Cerrar sesión").
- **Usuario autenticado** (existente): aporta nombre completo, nombre de usuario e iniciales para el área de usuario, y los permisos que determinan la visibilidad.

Ninguna de estas entidades se almacena en la base de datos; no hay información institucional nueva ni migraciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las opciones visibles del menú conduce a una página a la que el usuario tiene acceso (0 opciones que terminen en acceso denegado o página inexistente), verificado con al menos tres perfiles de permisos distintos.
- **SC-002**: El 0 % de las opciones sin permiso declarado (y no marcadas como visibles para todo autenticado) aparece en el menú.
- **SC-003**: En el 100 % de las páginas internas con opción asociada, exactamente una opción aparece como actual.
- **SC-004**: "Cerrar sesión" termina la sesión en el 100 % de los intentos legítimos y en el 0 % de los intentos mediante simple enlace o solicitud falsificada.
- **SC-005**: Un usuario puede llegar a cualquier opción del menú usando solo el teclado, en cualquier ancho de pantalla desde móvil hasta escritorio.
- **SC-006**: La verificación de contraste da conformidad WCAG AA para todas las combinaciones de colores del menú en el tema claro.
- **SC-007**: Las plantillas del componente contienen 0 estilos inline, 0 textos visibles en inglés y 0 enlaces de demostración, y las páginas internas muestran 0 menús de navegación o de usuario fuera del aside.
- **SC-008**: Incorporar una nueva opción de un módulo requiere 0 cambios en las plantillas del componente.
- **SC-009**: Mostrar el menú no añade una demora perceptible a la carga de las páginas internas (el tiempo de respuesta no aumenta de forma apreciable respecto a la versión actual).

## Clarifications

### Session 2026-10-28

- Q: ¿La protección (autenticación + permiso de consulta) de las páginas de destino del menú inicial forma parte de esta feature o de una feature de seguridad separada? → A: Sí, solo las páginas de lista enlazadas por el menú inicial (y la página de Inicio con autenticación). El resto de vistas de esos módulos se protegerá en una feature posterior.
- Q: ¿Qué hacemos con el menú horizontal de demostración de la barra superior, que en escritorio se muestra junto al nuevo aside? → A: Ocultar la barra superior completa en los layouts con aside; navegación y menú de usuario quedan solo en el aside.
- Q: ¿Qué color de fondo debe tener el aside? → A: Color institucional principal, con texto e íconos claros y estado actual marcado por fondo + indicador no cromático.
- Q: ¿El aside debe verse y probarse también en tema oscuro en esta feature, o basta con el tema claro? → A: Solo tema claro; el soporte de tema oscuro llegará con la feature de "Personalizar".
- Q: ¿El cierre de sesión debe dejar registro de auditoría ya en esta feature, o se pospone hasta que exista el módulo de auditoría? → A: Posponer; esta feature solo garantiza que el cierre de sesión emita el evento estándar al que se enganchará el módulo de auditoría.

## Assumptions

- Se reutiliza la autenticación existente del módulo de usuarios: inicio de sesión, cierre de sesión (que ya solo acepta envíos protegidos) y redirecciones ya configurados.
- El modelo de usuario no tiene fotografía ni cargo: el avatar mostrará iniciales y el dato secundario será el nombre de usuario (número de documento). Cuando se incorpore cargo o fotografía, se mostrarán sin cambiar el componente.
- Las etiquetas, nombres de sección y orden inicial del menú son propuestas razonables; el contenido exacto se valida con el Responsable en la clarificación o el plan.
- El menú de usuario y la navegación pasan a vivir solo en el aside (patrón Tabler 1.7.1). La barra superior deja de mostrarse en los layouts con aside (FR-026); sus utilidades (cambio de tema, notificaciones, menú de aplicaciones) son hoy de demostración y, si se necesitan, se reincorporarán al aside en features futuras (por ejemplo, junto con "Personalizar"). El componente de barra superior puede permanecer en el repositorio para otros layouts, pero no se usa en los layouts con aside.
- Existe un defecto conocido en el nombre de ruta de la lista de Órganos jurisdiccionales (comparte nombre con la ruta de cambio de estado); debe corregirse para que la opción pueda resolverse correctamente.
- La opción "Personalizar" (zona lateral adicional), el soporte del tema oscuro y las opciones adicionales del menú de usuario se implementarán en features futuras.
- No se almacenan datos nuevos, por lo que no aplican inactivación ni auditoría de datos. La auditoría del cierre de sesión es una dependencia pendiente del futuro módulo de auditoría (ver FR-024a); hasta entonces existe una brecha conocida respecto del Principio III, que debe registrarse en el plan.
- Las pruebas cubrirán filtrado por permisos, denegación por defecto, ocultamiento de grupos vacíos, estado actual, cierre de sesión protegido, ausencia de menú para no autenticados, ausencia de estilos inline y la protección de las páginas de destino del menú inicial (redirección al inicio de sesión si no hay sesión; denegación si falta el permiso).
