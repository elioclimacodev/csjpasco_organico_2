# Feature Specification: Protección de operaciones y configuración segura

**Feature Branch**: `002-seguridad-acceso-configuracion`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Proteger todas las operaciones no públicas del ERP con autenticación y permisos nativos, y obtener del entorno la configuración sensible (clave secreta, modo de depuración, hosts y orígenes de confianza). Cierra la brecha preexistente II.4 de docs/decisiones/2026-10-28-brechas-feature-001.md." (descripción completa en el historial de `/speckit-specify`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nadie opera sin sesión (Priority: P1)

Como Responsable Técnico, necesito que ninguna página ni operación interna del ERP (consultar, registrar, modificar, inactivar o exportar información institucional) sea accesible sin haber iniciado sesión, y que solo un conjunto explícito y revisable de páginas sea público.

**Why this priority**: Hoy más de 40 operaciones de Organización, Personas y Ubicaciones se pueden ejecutar escribiendo su dirección, sin sesión. Es un incumplimiento del Principio II y la brecha II.4 registrada.

**Independent Test**: Sin sesión, recorrer todas las direcciones del sistema y comprobar que solo las páginas públicas declaradas responden; el resto dirige al inicio de sesión.

**Acceptance Scenarios**:

1. **Given** un visitante sin sesión, **When** intenta abrir cualquier página u operación interna (por ejemplo, el detalle o la exportación de un distrito judicial, o la lista de países), **Then** no accede y es dirigido al inicio de sesión.
2. **Given** un visitante sin sesión, **When** abre una página pública declarada (inicio de sesión, recuperación de contraseña y las demás de la lista de FR-003), **Then** la página responde normalmente.
3. **Given** que un desarrollador agrega una página nueva sin declararla pública, **When** se ejecutan las verificaciones automáticas, **Then** la página nueva exige sesión (denegación por defecto) y las verificaciones lo confirman.
4. **Given** un visitante que inicia sesión después de haber sido dirigido al login, **When** se autentica, **Then** vuelve a la página interna que intentaba abrir.

---

### User Story 2 - Cada operación exige su permiso (Priority: P1)

Como usuario autenticado, solo puedo consultar, registrar, modificar, inactivar o exportar la información para la que tengo el permiso correspondiente. Si no lo tengo, recibo un aviso claro en español.

**Why this priority**: Constitución, Principio II: la autenticación no basta como autorización y se aplica el mínimo privilegio.

**Independent Test**: Con usuarios que tengan solo permiso de consulta, solo de registro, etc., comprobar que cada operación se permite o deniega según el permiso.

**Acceptance Scenarios**:

1. **Given** un usuario con permiso de consulta de distritos judiciales y sin permiso de registro, **When** abre la lista y el detalle, **Then** accede; **When** intenta registrar un distrito, **Then** recibe una denegación de acceso.
2. **Given** un usuario sin permiso de exportación de una entidad, **When** solicita la exportación, **Then** recibe una denegación y no se genera ningún archivo.
3. **Given** un usuario sin el permiso de inactivación de una entidad, **When** intenta inactivarla o reactivarla, **Then** recibe una denegación y el estado del registro no cambia.
4. **Given** un usuario con todos los permisos de una entidad, **When** realiza cualquier operación sobre ella, **Then** la operación procede con normalidad (sin regresiones).

---

### User Story 3 - Denegaciones claras dentro de ventanas y fragmentos (Priority: P2)

Como usuario, cuando abro una ventana (modal) o actualizo una tabla y mi sesión expiró o no tengo permiso, veo un aviso claro y no una página completa incrustada dentro de la ventana.

**Why this priority**: Las operaciones de detalle, registro, edición e inactivación se muestran en ventanas que se cargan sin recargar la página. Una denegación mal presentada confunde y puede parecer un error del sistema.

**Independent Test**: Con la sesión expirada y luego sin permiso, abrir el detalle de un registro desde una lista y verificar la respuesta mostrada.

**Acceptance Scenarios**:

1. **Given** un usuario con la sesión expirada, **When** abre una ventana de detalle o filtra una tabla, **Then** la página completa (no solo la ventana o el área actualizada) se dirige al inicio de sesión y, tras autenticarse, el usuario vuelve a la página en la que estaba.
2. **Given** un usuario sin permiso, **When** abre una ventana de una operación no permitida, **Then** ve dentro de la ventana un aviso en español formal de que no tiene permiso, sin detalles técnicos ni el nombre del permiso, y puede cerrarla.
3. **Given** un usuario sin permiso de consulta de una entidad, **When** filtra, ordena o pagina una tabla de esa entidad, **Then** ve una notificación flotante de error en español y la tabla conserva su contenido.

---

### User Story 4 - Configuración sensible fuera del código (Priority: P1)

Como Responsable Técnico, necesito que la clave secreta, el modo de depuración, los hosts permitidos y los orígenes de confianza se definan en el entorno y no en el código versionado, y que el sistema no arranque si falta un dato obligatorio.

**Why this priority**: La constitución prohíbe escribir secretos en archivos versionados y exige fallar explícitamente ante variables requeridas ausentes. Hoy la clave secreta está en el repositorio y el modo de depuración está activo fijo.

**Independent Test**: Arrancar el sistema sin la clave secreta (debe fallar con un mensaje claro) y sin indicar el modo de depuración (debe quedar desactivado).

**Acceptance Scenarios**:

1. **Given** un entorno sin clave secreta definida, **When** se inicia el sistema, **Then** no arranca y muestra un mensaje en español que indica la variable faltante.
2. **Given** un entorno que no define el modo de depuración, **When** se inicia el sistema, **Then** el modo de depuración queda desactivado.
3. **Given** un entorno que define hosts y orígenes de confianza, **When** se inicia el sistema, **Then** acepta solicitudes solo de esos hosts y orígenes.
4. **Given** el repositorio, **When** se revisa el código versionado, **Then** no contiene la clave secreta ni valores de hosts u orígenes propios de un entorno.

---

### Edge Cases

- Página nueva agregada sin declaración: se protege por defecto (exige sesión) y la verificación automática la detecta como no pública.
- Usuario autenticado que pierde un permiso durante la sesión: la siguiente operación se deniega (el permiso se evalúa en cada solicitud).
- Superusuario: accede a todas las operaciones y no ve el aviso de cuenta sin permisos.
- Cuenta autorregistrada recién activada, sin grupos ni permisos: ve Inicio con el aviso de FR-003a y el menú lateral solo con "Inicio".
- Usuario inactivo: no puede iniciar sesión ni operar.
- Página de error (403, 404, 500) y página de verificación fallida: se muestran sin exigir sesión, con el comportamiento de la feature 001.
- Recursos estáticos (estilos, imágenes, scripts de terceros) y el panel de administración: no se ven afectados (el panel conserva su propio control de acceso).
- Exportación denegada: no se genera ni descarga ningún archivo parcial.
- Inactivación denegada: el registro conserva su estado y no se registra ningún cambio.
- Solicitud a una página pública estando ya autenticado (por ejemplo, el inicio de sesión): se comporta como hoy (redirige a Inicio).
- Valor inválido del modo de depuración en el entorno (distinto de verdadero/falso): el sistema no arranca e indica el valor esperado.

## Requirements *(mandatory)*

### Functional Requirements

**Autenticación y denegación por defecto**

- **FR-001**: Toda página u operación del sistema DEBE exigir sesión autenticada, salvo las declaradas explícitamente como públicas (denegación por defecto).
- **FR-002**: La declaración de páginas públicas DEBE ser explícita, estar junto a cada página pública y ser revisable; no DEBE existir una vía implícita para que una página quede pública.
- **FR-003**: Las páginas públicas DEBEN limitarse a: inicio de sesión; cierre de sesión (solo envío protegido); recuperación de contraseña (solicitud, aviso de envío, confirmación y finalización); páginas de error y de verificación fallida; y el autorregistro de cuentas (registro, activación por correo y registro completo). Una cuenta autorregistrada no obtiene ningún permiso hasta que un administrador le asigne grupos o permisos, por lo que solo ve Inicio.
- **FR-003a**: Mientras un usuario autenticado no tenga ningún permiso asignado (directamente o por grupos), Inicio DEBE mostrar un aviso en español formal: "Su cuenta aún no tiene permisos asignados. Solicítelos al administrador del sistema." El aviso DEBE desaparecer en cuanto el usuario tenga al menos un permiso, y NO DEBE mostrarse a superusuarios.
- **FR-004**: La página de demostración de registro del módulo principal (`signup`, basada en una plantilla de ejemplo del design system) DEBE retirarse.
- **FR-005**: Un visitante sin sesión que intenta abrir una página interna DEBE ser dirigido al inicio de sesión y, tras autenticarse, volver a la página que intentaba abrir.

**Autorización por operación**

- **FR-006**: Cada operación sobre información institucional DEBE exigir el permiso nativo correspondiente, con esta convención:
  - lista, detalle y exportación → permiso de consulta (`view`) de la entidad;
  - registro → permiso de alta (`add`);
  - modificación → permiso de cambio (`change`);
  - inactivación y reactivación → permiso de cambio (`change`) de la entidad.
- **FR-007**: El alcance de FR-006 DEBE cubrir todas las operaciones de: Distritos judiciales, Materias jurisdiccionales, Órganos jurisdiccionales, Sedes judiciales, Personas, Países, Departamentos, Provincias y Distritos (ubicación geográfica). Las operaciones ya protegidas por la feature 001 DEBEN conservar su protección.
- **FR-008**: Un usuario autenticado sin el permiso requerido DEBE recibir una denegación de acceso con el mecanismo nativo de denegación, de modo que el futuro módulo de auditoría pueda registrarla sin modificar las vistas.
- **FR-009**: Una operación denegada NO DEBE producir efectos: ni cambios de datos, ni archivos de exportación, ni cambios de estado.
- **FR-010**: Los permisos que declara cada opción del menú lateral DEBEN seguir coincidiendo con los que exige su página destino (spec 001, FR-005).

**Respuestas en ventanas y fragmentos**

- **FR-011**: Cuando una solicitud de fragmento se deniega por falta de permiso, el sistema DEBE usar los componentes transversales de mensajes existentes, con un aviso en español formal sin detalles técnicos ni nombres de permisos:
  - **en ventanas** (detalle, registro, edición, inactivación): la ventana muestra la advertencia transversal de ventana con el mensaje y un botón "Cerrar";
  - **en actualizaciones de tabla** (filtrar, ordenar, paginar): se muestra una notificación flotante de error y la tabla conserva su contenido.
  En ningún caso DEBE incrustarse la página completa de denegación ni el menú lateral.
- **FR-012**: Cuando una solicitud de fragmento llega sin sesión, el sistema DEBE dirigir la página completa al inicio de sesión (con retorno a la página en la que estaba el usuario) y NO DEBE incrustar la página de inicio de sesión dentro de la ventana o del área actualizada.

**Configuración sensible**

- **FR-013**: La clave secreta DEBE obtenerse del entorno y ser obligatoria; si falta, el sistema NO DEBE arrancar y DEBE indicar en español la variable faltante.
- **FR-014**: El modo de depuración DEBE obtenerse del entorno y quedar desactivado si no se define; un valor no reconocido DEBE impedir el arranque con un mensaje que indique los valores aceptados.
- **FR-015**: Los hosts permitidos y los orígenes de confianza DEBEN obtenerse del entorno como listas; el código versionado NO DEBE contener valores propios de un entorno (direcciones, puertos o dominios concretos).
- **FR-016**: El archivo de ejemplo de variables de entorno DEBE documentar todas las variables nuevas, sin valores secretos reales.
- **FR-016a**: El transporte seguro de producción (redirección de HTTP a HTTPS, política HSTS y confianza en la cabecera de protocolo del proxy) DEBE poder activarse desde el entorno y DEBE estar desactivado por defecto, de modo que el desarrollo por HTTP siga funcionando y cada entorno de producción lo active con sus variables. Las marcas de seguridad de las cookies de sesión y de verificación DEBEN controlarse también desde el entorno y estar activas por defecto.
- **FR-017**: La clave secreta que hoy figura en el código versionado DEBE considerarse comprometida: DEBE retirarse del código y cada entorno DEBE usar una clave nueva.

**Registro de gobernanza**

- **FR-018**: El registro de brechas de la feature 001 DEBE actualizarse: la brecha II.4 (operaciones sin protección) se marca como cerrada por esta feature, y la brecha III.2b (denegaciones sin auditar) se amplía a las nuevas denegaciones, conforme a la constitución §Gobernanza › Brechas preexistentes.

### Key Entities *(include if feature involves data)*

- **Página pública**: página que puede abrirse sin sesión; su lista es cerrada (FR-003) y su declaración es explícita (FR-002).
- **Operación protegida**: cualquier otra página u operación; exige sesión y el permiso correspondiente (FR-006).
- **Permiso**: permiso nativo por entidad y acción (consulta, alta y cambio; la inactivación usa el de cambio), asignado a usuarios o grupos desde el panel de administración.
- **Variable de entorno**: dato de configuración que se lee del entorno (clave secreta, modo de depuración, hosts, orígenes de confianza), con su obligatoriedad y valor por defecto.

No se crean modelos de datos ni permisos nuevos: se usan los permisos nativos existentes de cada entidad.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las páginas y operaciones no declaradas públicas rechazan a un visitante sin sesión, verificado por un recorrido automático de todas las direcciones del sistema.
- **SC-002**: El 100 % de las páginas públicas declaradas responden sin sesión.
- **SC-003**: Para cada operación protegida, un usuario sin el permiso requerido es denegado (0 operaciones accesibles sin su permiso) y uno con el permiso accede, verificado con al menos un perfil por tipo de permiso.
- **SC-004**: 0 operaciones denegadas producen cambios de datos, archivos o cambios de estado.
- **SC-005**: El 100 % de las denegaciones en ventanas muestran la advertencia de ventana con el botón "Cerrar", y el 100 % de las denegaciones en actualizaciones de tabla muestran la notificación flotante sin alterar la tabla; ninguna incrusta páginas completas.
- **SC-006**: El código versionado contiene 0 claves secretas y 0 valores de hosts u orígenes propios de un entorno.
- **SC-006a**: Sin variables de transporte seguro definidas, el sistema responde por HTTP (desarrollo); con ellas activas, el 100 % de las solicitudes HTTP se redirigen a HTTPS y las respuestas incluyen la política HSTS.
- **SC-007**: Sin clave secreta definida, el sistema no arranca en el 100 % de los intentos; sin modo de depuración definido, arranca con la depuración desactivada.
- **SC-007a**: Un usuario sin permisos ve el aviso de FR-003a en Inicio en el 100 % de los casos, y un usuario con al menos un permiso o superusuario no lo ve.
- **SC-008**: Las opciones del menú lateral visibles para cada perfil conducen solo a páginas a las que ese perfil tiene acceso (0 opciones que terminen en denegación).

## Clarifications

### Session 2026-10-29

- Q: ¿El autorregistro de cuentas (registro, activación por correo y registro completo) debe seguir siendo público? → A: Sí, sigue público; la cuenta no obtiene permisos hasta que un administrador le asigne grupos o permisos.
- Q: ¿Qué permiso exigen la inactivación y la reactivación? → A: El permiso de cambio (`change`) de la entidad.
- Q: ¿Qué ocurre cuando una ventana o tabla se carga con la sesión expirada? → A: La página completa se dirige al inicio de sesión y, tras autenticarse, el usuario vuelve a la página en la que estaba.
- Q: ¿Debe esta feature incluir la configuración de transporte seguro para producción (HTTPS, HSTS, cabecera del proxy)? → A: Sí, controlada desde el entorno y desactivada por defecto; producción la activa con variables.
- Q: ¿Cómo se muestra el aviso de acceso denegado en ventanas y actualizaciones de tabla? → A: En ventanas, con la advertencia transversal de ventana y un botón "Cerrar"; en actualizaciones de tabla, con una notificación flotante de error, sin cambiar la tabla.
- Q: ¿Qué ve un usuario autorregistrado que aún no tiene grupos ni permisos? → A: Inicio muestra un aviso de que la cuenta aún no tiene permisos asignados y debe solicitarlos al administrador; el aviso desaparece al tener al menos un permiso.

## Assumptions

- Se reutilizan el sistema nativo de usuarios, grupos y permisos, las plantillas de error 403, 404, 500 y de verificación fallida, y el patrón de variables de entorno obligatorias de la feature 001.
- Las vistas de detalle, registro, edición e inactivación devuelven fragmentos que se cargan en ventanas sin recargar la página; las listas devuelven fragmentos al filtrar, ordenar o paginar.
- El permiso de exportación es el de consulta (`view`), según la convención indicada por el Responsable Técnico; no hay información declarada sensible que exija un permiso de exportación distinto.
- Las variables de transporte seguro y de cookies (FR-016a) se documentan en `.env.example`; los valores concretos de cada servidor (dominios, duración de HSTS) los fija la feature o el procedimiento de despliegue.
- Las listas de hosts permitidos y orígenes de confianza se definen en el entorno como valores separados por comas. Con la depuración activa y la lista vacía, se admiten solo `localhost` y `127.0.0.1`; con la depuración desactivada y la lista de hosts vacía, el sistema no arranca e indica la variable faltante.
- La verificación automática de FR-001 recorre todas las direcciones enrutadas; las que tienen parámetros (identificadores, tokens) se prueban con valores de prueba, porque la exigencia de sesión se evalúa antes de buscar el registro. El panel de administración, los recursos estáticos y las páginas públicas declaradas quedan fuera del recorrido de "debe exigir sesión" y se verifican por separado.
- La asignación de permisos a usuarios y grupos se realiza desde el panel de administración; no se construyen interfaces para ello.
- Las páginas del módulo de configuración y las vistas heredadas no enrutadas (archivos de respaldo y aplicaciones con sufijos `_`/`__`/`___`) no están activas y quedan fuera de alcance; la verificación automática de FR-001 cubre todas las direcciones realmente enrutadas.
- No existe aún el módulo de auditoría; las denegaciones se producen con el mecanismo nativo para que pueda engancharse después (FR-008, FR-018).
- Los usuarios de prueba y de operación deben estar activos; la creación de usuarios mantiene su comportamiento actual (inactivos hasta su activación).
