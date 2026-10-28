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
- Usuario sin nombre completo registrado: el área de usuario muestra su nombre de usuario como nombre principal (único caso en que se ve el número de documento, por ser la única identificación disponible) y las iniciales se derivan de él.
- Usuario sin grupos: el área de usuario muestra solo el nombre, sin dato secundario.
- Opción que exige varios permisos: se muestra solo si el usuario tiene todos los permisos declarados.
- Desplegable cuyos hijos quedan todos ocultos: el desplegable no se muestra; una sección sin opciones visibles tampoco muestra su título.
- Mantenimiento cuya lista depende de otro registro (por ejemplo, Sedes judiciales, cuya lista pertenece a un distrito judicial): no se ofrece como opción directa del menú mientras no exista una página de acceso independiente.
- Etiquetas largas: se ajustan sin desbordar el ancho del menú ni ocultar la insignia.
- Página cargada parcialmente (fragmentos dinámicos): el menú no se duplica ni se vuelve a insertar dentro del contenido.
- Opciones con el mismo orden: se muestran en un orden estable y predecible (por ejemplo, alfabético por etiqueta).
- "Cerrar sesión" enviado con la sesión ya expirada: el resultado es el mismo que un cierre normal (el usuario llega a la pantalla de inicio de sesión), sin mostrar errores.
- "Cerrar sesión" enviado con una verificación anti-falsificación inválida (por ejemplo, un formulario abierto en otra pestaña antes de iniciar una nueva sesión): la sesión NO se cierra y el usuario ve una página en español, con tono formal, que explica que la solicitud no pudo verificarse y ofrece volver a la página anterior o a "Inicio", sin detalles técnicos.
- Páginas de error para usuarios autenticados: la página de acceso denegado (FR-008b) y la de página no encontrada muestran el menú lateral; la página de error interno del servidor NO muestra el menú lateral (para no depender de componentes que podrían ser la causa del error) y ofrece un enlace a "Inicio". Para visitantes no autenticados, ninguna página de error muestra el menú lateral.

## Requirements *(mandatory)*

### Functional Requirements

**Contenido y filtrado**

- **FR-001**: El sistema DEBE mostrar el menú lateral en todas las páginas internas para usuarios autenticados y NO DEBE mostrarlo a visitantes no autenticados.
- **FR-002**: El contenido del menú (secciones, opciones, submenús, íconos, insignias, permisos y orden) DEBE provenir de una configuración declarada en el servidor y versionada con el código; NO DEBE escribirse de forma fija en las plantillas ni almacenarse en la base de datos.
- **FR-003**: Cada módulo DEBE poder declarar sus propias secciones y opciones; un único mecanismo compartido DEBE reunirlas, ordenarlas y entregarlas al componente. NO DEBE existir una segunda vía para definir el menú.
- **FR-004**: Cada opción DEBE poder declarar: identificador único, etiqueta en español, destino (ruta interna por nombre o dirección externa), ícono opcional, insignia opcional (texto y variante), permiso(s) requerido(s), orden y, opcionalmente, opciones hijas.
- **FR-005**: El sistema DEBE mostrar una opción solo si el usuario posee todos los permisos que esta declara, usando el sistema nativo de permisos y grupos. Toda opción con destino interno (inicial o futura) DEBE declarar los mismos permisos que exige su página destino, de modo que el menú no ofrezca páginas que respondan con una denegación de acceso.
- **FR-006**: Denegación por defecto: una opción con destino (enlace) sin permiso declarado o cuyo permiso no pueda verificarse NO DEBE mostrarse, salvo que se declare explícitamente como visible para todo usuario autenticado. Las opciones que solo agrupan otras (desplegables y submenús) no declaran permisos propios: su visibilidad depende únicamente de que tengan al menos una opción hija visible (FR-007).
- **FR-007**: Un desplegable o submenú sin opciones hijas visibles, y una sección sin opciones visibles, NO DEBEN mostrarse.
- **FR-008**: Ocultar una opción DEBE ser solo presentación; cada página DEBE seguir verificando su propia autorización con independencia del menú. Hoy las páginas de destino del menú inicial (Inicio, Distritos judiciales, Materias jurisdiccionales, Órganos jurisdiccionales y Personas) no verifican autenticación ni permisos; solo la lista de Usuarios lo hace.
- **FR-008a**: Las páginas de destino del menú inicial (Inicio y las páginas de lista de Distritos judiciales, Materias jurisdiccionales, Órganos jurisdiccionales y Personas) DEBEN exigir sesión autenticada y, salvo Inicio, el mismo permiso de consulta que declara su opción de menú. Un usuario no autenticado DEBE ser dirigido al inicio de sesión; un usuario autenticado sin permiso DEBE recibir una denegación de acceso. Las demás vistas de esos módulos (crear, editar, detalle, cambio de estado, exportar) quedan fuera de alcance y se protegerán en una feature de seguridad posterior.
- **FR-008b**: Cuando una página deniega el acceso por falta de permiso, el usuario DEBE ver una página en español, con tono formal, que indique que su cuenta no tiene permiso para acceder a esa página, sugiera solicitar el acceso al administrador del sistema y ofrezca un enlace para volver a "Inicio". Esa página DEBE mostrar el menú lateral al usuario autenticado y NO DEBE exponer detalles técnicos ni el nombre del permiso faltante.
- **FR-009**: Una opción cuyo destino interno no pueda resolverse NO DEBE romper la página; DEBE omitirse y el error DEBE detectarse en las verificaciones automáticas del proyecto.

**Capacidades del componente (patrón navbar vertical Tabler 1.7.1)**

- **FR-010**: Botón para mostrar u ocultar el menú en pantallas pequeñas, con etiqueta accesible en español.
- **FR-011**: Logo institucional enlazado a la página de inicio, servido como imagen institucional con texto alternativo en español y legible sobre el fondo del menú.
- **FR-012**: Títulos de sección para agrupar opciones.
- **FR-013**: Opción simple de primer nivel con ícono y etiqueta.
- **FR-014**: Opción desplegable de primer nivel con submenú.
- **FR-015**: Submenú presentado en una o varias columnas, según se declare. Las opciones se reparten en orden, llenando cada columna de arriba hacia abajo antes de pasar a la siguiente; cada columna, salvo la última, contiene ⌈n / c⌉ opciones (n = opciones visibles, c = columnas declaradas), y nunca se muestran columnas vacías.
- **FR-016**: Submenú anidado de segundo nivel dentro de un desplegable.
- **FR-017**: Insignia opcional por opción, con texto en español; el color NO DEBE ser el único medio para comunicar su significado. Las variantes visuales de insignia DEBEN pertenecer a un conjunto cerrado y predefinido (una variante neutra, una de advertencia y una informativa), y cada variante DEBE cumplir contraste WCAG AA (≥ 4.5:1) entre su texto y su fondo, y ≥ 3:1 entre su fondo y el fondo del menú.
- **FR-018**: Ícono opcional también en opciones de submenú.
- **FR-019**: Opciones con destino externo que abren en una pestaña nueva, sin dar acceso a la ventana de origen, e indican de forma accesible que abren en pestaña nueva.
- **FR-020**: Estado actual calculado en el servidor a partir de la página actual (incluidas sus páginas secundarias): la opción actual se marca y se anuncia como página actual, y su desplegable padre se marca como activo y se muestra abierto. Cada opción declara qué páginas la activan (su propia página y, opcionalmente, un grupo de páginas secundarias). Si la página actual corresponde a más de una opción, se marca **una sola**, según esta precedencia: (1) la opción que declara exactamente esa página prevalece sobre las que la incluyen en un grupo; (2) entre grupos, prevalece el más específico (el que abarca menos páginas, es decir, el patrón más largo); (3) si persiste el empate, prevalece la primera opción en el orden del menú.
- **FR-021**: Área de usuario en la parte inferior del menú, con avatar, nombre completo y un dato secundario del usuario autenticado, y un menú desplegable hacia arriba. Sin fotografía, el avatar DEBE mostrar las iniciales. El dato secundario DEBE ser el nombre del grupo principal del usuario (el primero de sus grupos en orden alfabético); si el usuario no pertenece a ningún grupo, no se muestra dato secundario. El número de documento NO DEBE mostrarse como dato secundario.
- **FR-022**: Zona lateral adicional (reservada para "Personalizar") prevista en la estructura del componente, sin contenido ni presencia visible en esta feature.

**Menú de usuario y cierre de sesión**

- **FR-023**: El menú de usuario DEBE contener únicamente la opción "Cerrar sesión" en esta feature.
- **FR-024**: "Cerrar sesión" DEBE ejecutarse mediante un envío de formulario protegido contra solicitudes falsificadas entre sitios; una simple navegación o enlace NO DEBE cerrar la sesión. Tras cerrar sesión, el usuario DEBE llegar a la pantalla de inicio de sesión.
- **FR-024a**: El cierre de sesión DEBE realizarse mediante el mecanismo nativo de cierre de sesión, de modo que emita el evento estándar de cierre de sesión al que se enganchará el futuro módulo de auditoría. Esta feature NO crea registros de auditoría; la auditoría del cierre de sesión (Principio III) se entregará con la feature del módulo de auditoría.
- **FR-025**: Las opciones del menú de usuario DEBEN provenir de la misma configuración del servidor, de modo que features futuras puedan agregar opciones (Perfil, Configuración, Ayuda, etc.) sin modificar las plantillas del componente.
- **FR-026**: La navegación y el menú de usuario DEBEN existir en un único lugar de la interfaz: el aside. Los layouts que incluyen el aside NO DEBEN mostrar la barra superior (ni su menú horizontal de demostración, ni su menú de usuario, ni sus utilidades de tema, notificaciones o menú de aplicaciones) en ningún tamaño de pantalla.

**Presentación, accesibilidad y limpieza**

- **FR-027**: Todos los textos visibles y etiquetas accesibles del menú DEBEN estar en español, con tono formal.
- **FR-028**: El menú DEBE ser una región de navegación con nombre accesible en español; los íconos decorativos NO DEBEN anunciarse; todo el menú DEBE poder usarse solo con teclado (WCAG 2.1 AA), con estas condiciones:
  - **Orden de foco**: DEBE coincidir con el orden visual en todos los tamaños de pantalla: botón de mostrar/ocultar menú (solo cuando está visible) → logo → opciones del menú en orden de aparición → área de usuario (que se presenta al final).
  - **Interacción**: Tab y Shift+Tab recorren los elementos enfocables; Enter o Espacio abren o cierran un desplegable o el menú de usuario y activan una opción; Esc cierra el desplegable o menú de usuario abierto y devuelve el foco al elemento que lo abrió.
  - **Foco visible**: todo elemento enfocable DEBE mostrar un indicador de foco de al menos 2 px de grosor y contraste ≥ 3:1 respecto del fondo adyacente.
- **FR-029**: El menú DEBE ser responsive con enfoque mobile first (escritorio, tablet, móvil). Por debajo de 992 px de ancho, el menú se muestra colapsado al cargar la página y se despliega con el botón de FR-010; desde 992 px se muestra siempre expandido como barra lateral. Al desplegar el menú en pantallas pequeñas, el desplegable que contiene la opción actual DEBE aparecer abierto, igual que en escritorio (FR-020).
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

### Seguridad, auditoría y protección de datos

Resumen consolidado de los requisitos que la constitución exige identificar (Gobernanza §Revisión de cumplimiento). Los requisitos normativos son los FR citados.

- **Autenticación**: el menú lateral y las páginas de destino del menú inicial exigen sesión autenticada (FR-001, FR-008a). Sin sesión, el usuario es dirigido al inicio de sesión.
- **Autorización**: visibilidad por permisos nativos con denegación por defecto (FR-005, FR-006, FR-007). El menú no autoriza: cada página verifica su propio permiso (FR-008). Las 4 páginas de lista del menú inicial exigen su permiso de consulta (FR-008a).
- **Cierre de sesión**: solo por envío protegido contra falsificación; una navegación simple no cierra la sesión (FR-024), mediante el mecanismo nativo (FR-024a). Sesión expirada y verificación inválida: ver Edge Cases.
- **Mensajes de denegación**: en español formal, sin detalles técnicos ni nombres de permisos (FR-008b).
- **Eventos auditables que genera esta feature** (constitución §III Auditoría):
  - *Cierre de sesión* (evento de autenticación).
  - *Denegación de autorización* al acceder sin permiso a una página de destino del menú inicial (FR-008a).
  - Esta feature **no** crea registros de auditoría: ambos eventos se producen mediante los mecanismos nativos (el evento estándar de cierre de sesión y la denegación estándar de acceso), que son los puntos de enganche del futuro módulo de auditoría. La brecha temporal se registra en el plan (Complexity Tracking).
- **Información sensible y protección de datos**: el área de usuario muestra el nombre completo del usuario autenticado (dato personal visible solo para su titular) y, como dato secundario, el nombre de su grupo principal. El **número de documento de identidad** (que es el nombre de usuario) es un dato personal y **NO DEBE mostrarse** en el menú lateral, salvo como último recurso para el nombre principal cuando el usuario no tiene nombre completo registrado (ver Edge Cases).
- **Brechas registradas**: la auditoría pendiente (cierre de sesión y denegaciones) y la protección parcial de vistas se registran como brechas preexistentes, no introducidas por esta feature, en `docs/decisiones/2026-10-28-brechas-feature-001.md`.
- **Información no persistida**: la feature no almacena datos nuevos (ver Key Entities).

### Key Entities *(include if feature involves data)*

- **Sección de menú**: agrupación con título visible, orden y opciones. Se muestra solo si tiene al menos una opción visible.
- **Opción de menú**: entrada navegable con identificador, etiqueta, destino (interno o externo), ícono, insignia, permisos requeridos, indicador "visible para todo usuario autenticado", orden y opciones hijas (hasta dos niveles bajo el primer nivel, con presentación en columnas opcional).
- **Insignia**: texto breve en español con una variante visual.
- **Opción de menú de usuario**: acción disponible en el área de usuario; puede ser navegación o una acción que requiere envío protegido (como "Cerrar sesión").
- **Usuario autenticado** (existente): aporta nombre completo (o nombre de usuario como último recurso), iniciales y grupo principal para el área de usuario, y los permisos que determinan la visibilidad.

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
- **SC-008**: Incorporar una nueva opción de un módulo requiere 0 cambios en las plantillas del componente, 0 cambios en el mecanismo compartido del menú y 0 cambios en archivos de otros módulos (solo cambian archivos del módulo que declara la opción).
- **SC-009**: Mostrar el menú añade como máximo **3 consultas a la base de datos** por página (permisos del usuario, permisos de sus grupos y grupo principal), independientemente del número de opciones declaradas (verificable con conteo de consultas en las pruebas automáticas), y como máximo **20 ms** al tiempo medio de respuesta del servidor de una página interna, medido como la diferencia de la media de 20 solicitudes consecutivas a la misma página con y sin el menú, en el mismo entorno.

## Clarifications

### Session 2026-10-28

- Q: ¿La protección (autenticación + permiso de consulta) de las páginas de destino del menú inicial forma parte de esta feature o de una feature de seguridad separada? → A: Sí, solo las páginas de lista enlazadas por el menú inicial (y la página de Inicio con autenticación). El resto de vistas de esos módulos se protegerá en una feature posterior.
- Q: ¿Qué hacemos con el menú horizontal de demostración de la barra superior, que en escritorio se muestra junto al nuevo aside? → A: Ocultar la barra superior completa en los layouts con aside; navegación y menú de usuario quedan solo en el aside.
- Q: ¿Qué color de fondo debe tener el aside? → A: Color institucional principal, con texto e íconos claros y estado actual marcado por fondo + indicador no cromático.
- Q: ¿El aside debe verse y probarse también en tema oscuro en esta feature, o basta con el tema claro? → A: Solo tema claro; el soporte de tema oscuro llegará con la feature de "Personalizar".
- Q: ¿El cierre de sesión debe dejar registro de auditoría ya en esta feature, o se pospone hasta que exista el módulo de auditoría? → A: Posponer; esta feature solo garantiza que el cierre de sesión emita el evento estándar al que se enganchará el módulo de auditoría.
- Q (revisión CHK004): ¿Qué dato secundario debe mostrarse bajo el nombre, dado que el nombre de usuario es el número de documento? → A: El nombre del grupo principal del usuario; el número de documento no se muestra como dato secundario.
- Q (revisión CHK008): ¿Cómo se tramitan las brechas de auditoría (cierre de sesión, 403) y la protección parcial de vistas frente a los Principios II y III? → A: Como brechas preexistentes no introducidas por la feature, registradas por el Responsable Técnico en `docs/decisiones/2026-10-28-brechas-feature-001.md` con fecha de revisión y cierre comprometido.

## Assumptions

- Se reutiliza la autenticación existente del módulo de usuarios: inicio de sesión, cierre de sesión (que ya solo acepta envíos protegidos) y redirecciones ya configurados.
- El modelo de usuario no tiene fotografía ni cargo: el avatar mostrará iniciales y el dato secundario será el grupo principal (FR-021). Cuando se incorporen cargo o fotografía, podrán mostrarse sin cambiar la estructura del componente.
- Las etiquetas, nombres de sección y orden inicial del menú son propuestas razonables; el contenido exacto se valida con el Responsable en la clarificación o el plan.
- El menú de usuario y la navegación pasan a vivir solo en el aside (patrón Tabler 1.7.1). La barra superior deja de mostrarse en los layouts con aside (FR-026); sus utilidades (cambio de tema, notificaciones, menú de aplicaciones) son hoy de demostración y, si se necesitan, se reincorporarán al aside en features futuras (por ejemplo, junto con "Personalizar"). El componente de barra superior puede permanecer en el repositorio para otros layouts, pero no se usa en los layouts con aside.
- Existe un defecto conocido en el nombre de ruta de la lista de Órganos jurisdiccionales (comparte nombre con la ruta de cambio de estado); debe corregirse para que la opción pueda resolverse correctamente.
- La opción "Personalizar" (zona lateral adicional), el soporte del tema oscuro y las opciones adicionales del menú de usuario se implementarán en features futuras.
- No se almacenan datos nuevos, por lo que no aplican inactivación ni auditoría de datos. La auditoría del cierre de sesión (FR-024a) y la de las denegaciones de autorización de las páginas protegidas por FR-008a son dependencias pendientes del futuro módulo de auditoría. Hasta entonces existe una brecha conocida respecto del Principio III (constitución §III Auditoría: eventos de autenticación y denegaciones de autorización), que se registra en el plan.
- Las pruebas cubrirán filtrado por permisos, denegación por defecto, ocultamiento de grupos vacíos, estado actual, cierre de sesión protegido, ausencia de menú para no autenticados, ausencia de estilos inline y la protección de las páginas de destino del menú inicial (redirección al inicio de sesión si no hay sesión; denegación si falta el permiso).
