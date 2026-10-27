<!--
Sync Impact Report (material temporal de revisión — NO es contenido de gobernanza;
remover antes de commitear .specify/memory/constitution.md)
======================================================================
Versión anterior: ninguna (primera versión registrada)
Versión nueva:   1.0.0 (ratificación inicial)
Sesión:          /speckit.constitution — fecha 2026-10-27

Principios o secciones modificados: NINGUNO.
  El contenido (Título, Propósito, Definiciones, Principios I–IV,
  Restricciones Tecnológicas y Estructura del Proyecto, Estándares de
  UI/UX y Accesibilidad, Validación Normalización y Testing y
  Gobernanza) se conservó textual, en español, sin reescritura,
  resumen reformulación, reordenamiento ni adiciones.
Secciones añadidas: ninguna (solo se añadió la línea de metadatos de
  versión al final de Gobernanza y este reporte temporal).
Secciones eliminadas: ninguna.

Decisiones de metadatos:
- CONSTITUTION_VERSION: 1.0.0 (ratificación inicial; primer registro).
- RATIFICATION_DATE: 2026-10-27 (fecha de registro; el historial estaba
  vacío y no constaba fecha de adopción anterior).
- LAST_AMENDED_DATE: 2026-10-27 (idem ratificación inicial).

Historial: entrada de la versión 1.0.0 añadida en
docs/historial-constitucion.md (la tabla estaba vacía). No se registró
ningún historial dentro de la constitución.
Contradicción reportada — RESUELTA por decisión del Responsable (2026-10-27):
1. "Identidad visual" declara `#A42622` como color institucional
   principal y PERMANECE sin cambios (la constitución prevalece).
   El archivo de tokens del proyecto usa `#A42612` y DEBE alinearse a
   `#A42622` en una corrección aparte (intento diferido de código, no
   parte de la gobernanza; la constitución NO se enmienda).
TODOs de placeholders: ninguno pendiente.
======================================================================
-->
# Constitución del ERP Administrativo — Corte Superior de Justicia de Pasco

## Propósito

Esta constitución define los principios no negociables que gobiernan todo desarrollo en este ERP institucional de la Corte Superior de Justicia de Pasco. Cada especificación, plan y tarea debe alinearse con estos principios. Las decisiones técnicas que se aparten de estas reglas requieren una enmienda o, en los casos que la Gobernanza permite, una excepción aprobada.

### Definiciones

- **Flujo esencial**: toda operación necesaria para autenticarse, cerrar sesión, y consultar, registrar, modificar o inactivar información institucional.
- **Información institucional**: datos que el ERP registra en cumplimiento de las funciones de la Corte Superior de Justicia de Pasco, incluidos sus historiales y registros de auditoría. Excluye los datos técnicos temporales (sesiones, cachés, archivos temporales y tokens expirados).
- **Entidad de identidad**: entidad que representa la identidad de un sujeto (persona natural o, cuando el dominio lo requiera, jurídica) con independencia de los roles, relaciones o procesos que mantenga con la institución. La identidad no se activa ni se inactiva: su existencia es permanente. Los estados de negocio de sus vínculos se gestionan en las entidades de rol, relación o proceso correspondientes. _Entidades de identidad vigentes: `Persona` (apps/personas)._
- **Componente transversal**: componente de interfaz o de comportamiento reutilizable por más de un módulo (por ejemplo, mensajes de éxito y error, toolbar de datatable, offcanvas, dropdown de acciones, wizard por pasos, breadcrumbs, modals, etc), ubicado en `templates/components/` o en el módulo designado para esa capacidad.

---

## Principio I: Server-Rendered First

Todo flujo esencial DEBE tener su lógica, validación y estado resueltos en el servidor. El sistema DEBE implementarse como una aplicación Django monolítica (organizada en módulos conforme al Principio IV) que use Django Templates para el renderizado.

HTMX y Alpine.js forman parte del stack obligatorio y DEBEN usarse así:

- HTMX DEBE ser el mecanismo preferente para cargar parciales de página, modales y fragmentos sin recargarla completa. Los endpoints que devuelven fragmentos HTML para HTMX son vistas del monolito y NO se consideran APIs.
- Alpine.js DEBE usarse para pequeñas interacciones locales y para validaciones de formulario a nivel de navegador como ayuda de usabilidad. NO DEBE contener lógica de negocio ni sustituir la validación autoritativa del servidor.
- El estado necesario para un flujo esencial (paso actual, filtros, paginación) DEBE residir en el servidor y poder reconstruirse desde la URL o la sesión.
- Los componentes de Tabler.io PUEDEN usar el JavaScript que traen incorporado para su funcionamiento (menús, desplegables, modales, etc). Este código se sirve desde los recursos estáticos de terceros con versión fija y NO se considera JavaScript del proyecto.
- El **JavaScript del proyecto** es el código escrito por el equipo de desarrollo. DEBE usarse solo como último recurso, cuando ni HTML y Django, ni HTMX, ni Alpine.js, ni las funcionalidades que Tabler ya incluye puedan resolver el requerimiento. DEBE ubicarse en `static/project/js/` y justificarse en la especificación o el plan.

El sistema NO DEBE depender de frameworks SPA del lado del cliente para sus operaciones principales.

**Prohibiciones explícitas**: Microservicios, CQRS y Event Sourcing están prohibidos a menos que esta constitución sea expresamente modificada.

**APIs**: El sistema NO DEBE exponer ni consumir APIs de interoperabilidad o integración, salvo que una especificación aprobada lo requiera expresamente y justifique su necesidad. Cuando se especifiquen, NO DEBEN sustituir la arquitectura server-rendered principal, DEBEN cumplir los Principios II y III y las reglas de validación, y DEBEN reutilizar la lógica de negocio compartida en lugar de duplicarla.

Las decisiones arquitectónicas DEBEN favorecer las capacidades nativas de Django antes de incorporar infraestructura, patrones o dependencias adicionales. La solución más simple usando el stack tecnológico definido en este documento, que satisfaga correctamente los requisitos DEBE ser preferida.

**Racional**: Mantener lógica, validación y estado en el servidor hace al sistema auditable, verificable y simple de mantener, mientras HTMX y Alpine.js aportan una experiencia fluida sin trasladar reglas de negocio al navegador.

---

## Principio II: Seguridad por Diseño

La seguridad DEBE ser parte del diseño de cada funcionalidad desde su concepción. Toda operación no pública DEBE ejecutarse bajo una sesión autenticada. Toda operación protegida DEBE verificar explícitamente que el usuario tenga la autorización necesaria. **La autenticación por sí sola NO DEBE considerarse autorización suficiente.**

**Denegación por defecto**: ante ausencia, ambigüedad o imposibilidad de determinar una autorización, el sistema DEBE denegar la operación.

Toda operación que consulte o modifique información institucional DEBE:

- Aplicar el principio de mínimo privilegio
- Ser atribuible al usuario o proceso que la ejecuta
- Generar evidencia de auditoría conforme al Principio III

Las funcionalidades públicas DEBEN limitarse a aquellas expresamente identificadas como tales por una especificación aprobada. Las especificaciones DEBEN identificar, cuando aplique:

- Requisitos de autenticación
- Permisos y reglas de autorización
- Eventos sujetos a auditoría
- Requisitos de protección de datos
- Información sensible que requiera tratamiento especial

El sistema nativo de autenticación, autorización, permisos y grupos de Django DEBE constituir la base para el control de acceso. **NO DEBEN implementarse mecanismos paralelos de autenticación o autorización** cuando Django proporcione una capacidad equivalente adecuada. Cuando el requerimiento exceda lo que Django ofrece de forma nativa (autorización a nivel de objeto o por ámbito organizacional), PUEDE implementarse una extensión compartida y documentada, ubicada en el módulo de autenticación y autorización del proyecto, construida sobre los usuarios, grupos y permisos de Django, sin crear identidades ni autorizaciones paralelas.

**Racional**: El control de acceso centralizado en las capacidades nativas de Django, con denegación por defecto, evita fricciones de seguridad, garantiza trazabilidad y reduce la superficie de ataque generada por mecanismos paralelos y no auditables.

---

## Principio III: Integridad de Datos y Auditoría

La información institucional DEBE mantener su integridad, trazabilidad e historial a lo largo de todo su ciclo de vida. **La información institucional NO DEBE eliminarse físicamente** como parte de las operaciones ordinarias del sistema, por ninguna vía (vistas, Django Admin, acciones masivas o procesos automáticos).

### Inactivación en lugar de eliminación

La baja ordinaria de información institucional se realiza por **inactivación** (eliminación lógica): el registro permanece en el sistema con su indicador de estado `activo` en `False`, y su reactivación vuelve a ponerlo en `True`.

- Toda entidad institucional DEBE usar inactivación mediante **un único mecanismo compartido**, implementado en `apps/common/`, que defina el indicador `activo` una sola vez. Se exceptúan:
    - los registros de auditoría y las entidades que una especificación declare expresamente inmutables, que NO admiten inactivación ni eliminación en operaciones ordinarias;
    - las **entidades de identidad** (ver Definiciones), que NO DEBEN poseer indicador de estado de negocio activo/inactivo, y cuyo registro NO DEBE ser inactivable ni eliminable en operaciones ordinarias. La designación de una entidad como de identidad DEBE constar en esta constitución; una especificación PUEDE proponer una nueva, justificando su naturaleza de identidad, pero su incorporación como excepción DEBE tramitarse por enmienda. Los datos de una entidad de identidad PUEDEN corregirse o actualizarse dejando constancia en la auditoría. Los estados de negocio (activación/desactivación) de una entidad de identidad DEBEN gestionarse en las entidades de rol, relación o proceso que la referencien, las cuales SÍ DEBERÁN usar el mecanismo único de inactivación.
- La inactivación DEBE preservar integridad referencial, historial institucional, trazabilidad, atribución de operaciones e información necesaria para auditoría. Quién inactivó o reactivó un registro, y cuándo, DEBE constar en la auditoría.
- Los registros inactivos DEBEN excluirse por defecto de los selectores y listados operativos; consultarlos DEBE ser explícito y estar autorizado. Los registros inactivos referenciados por información histórica DEBEN seguir resolviéndose y mostrándose en esas relaciones.
- **Unicidad**: las reglas de unicidad de negocio DEBEN aplicarse sobre todos los registros de la entidad, activos o inactivos, mediante restricciones a nivel de base de datos, de modo que una misma entidad de negocio no tenga dos representaciones. Cuando se intente registrar un valor que ya pertenece a un registro inactivo, el sistema DEBE informarlo y ofrecer su reactivación a quien esté autorizado, en lugar de crear un duplicado; si el usuario no está autorizado, DEBE indicar que debe solicitarla, sin exponer datos del registro. La reactivación DEBE ser auditable.
- El borrado desde Django Admin, individual o masivo, DEBE ser una inactivación. Django Admin NO DEBE constituir una vía para eludir este principio.
- Las relaciones hacia registros institucionales NO DEBEN usar eliminación en cascada física.

### Disposición excepcional

La eliminación física, anonimización o disposición excepcional de información institucional SOLO PUEDE realizarse por obligación legal o procedimiento formal autorizado y DEBE ser auditable. Esta regla no aplica a los datos técnicos temporales definidos en este documento.

### Auditoría

La auditoría DEBE registrar, como mínimo: actor (usuario o proceso del sistema), acción, fecha/hora, recurso afectado y resultado, sin almacenar contraseñas, tokens, secretos ni datos sensibles innecesarios.

Están sujetas a auditoría, como mínimo:

- La creación, modificación, inactivación, reactivación, anonimización y eliminación física de información institucional
- Los eventos de autenticación y los cambios en usuarios, grupos y permisos
- Las denegaciones de autorización sobre información protegida
- La consulta o exportación de información que una especificación declare sensible

Los registros de auditoría DEBEN ser inmutables: NO DEBEN poder modificarse ni eliminarse desde interfaces funcionales ni desde Django Admin, donde solo se consultan. Las operaciones realizadas desde Django Admin DEBEN auditarse con la misma fidelidad que las del resto del sistema.

**Racional**: La imposibilidad de destruir información institucional, un mecanismo único de inactivación y una auditoría inmutable preservan la memoria institucional y permiten responder legal y funcionalmente ante cualquier requerimiento.

---

## Principio IV: Monolito Modular con Entidades Canónicas

Cada entidad fundamental del dominio institucional DEBE tener una única representación canónica dentro del ERP. **Ningún módulo DEBE introducir una representación paralela, duplicada o inconsistente** de una entidad de negocio existente.

Las relaciones inter-módulo DEBEN construirse utilizando las entidades canónicas correspondientes. Cuando una funcionalidad necesite extender una entidad existente, DEBE hacerlo mediante un mecanismo explícito de relación o extensión sin duplicar la responsabilidad del dominio.

Cada capacidad funcional DEBE pertenecer a un módulo de negocio claramente identificado, implementado como aplicación Django dentro de `apps/`. Los módulos DEBEN mantener alta cohesión y bajo acoplamiento. Las dependencias inter-módulo DEBEN ser explícitas y documentadas.

Las capacidades transversales (autenticación y autorización, auditoría, notificaciones y parametrización global) DEBEN implementarse una sola vez, cada una en un único módulo designado, y **NO DEBEN duplicarse innecesariamente**. Los componentes técnicos compartidos, como el mecanismo de inactivación, residen en `apps/common/`.

**Racional**: La unicidad canónica de las entidades y de las capacidades transversales evita divergencias entre módulos, reduce costos de integración y garantiza que las operaciones inter-modulares operen sobre una realidad única y consistente.

---

## Restricciones Tecnológicas y Estructura del Proyecto

### Stack tecnológico obligatorio

- **Python** 3.12 o superior, compatible con la versión de Django adoptada por el proyecto
- **Django** 6.x como framework web principal
- **Django Templates** para renderizado server-side
- **HTMX** para cargar parciales de página sin recarga completa (Principio I)
- **Alpine.js** para pequeñas interacciones locales y validaciones de conveniencia en el navegador (Principio I)
- **Tabler.io** (Bootstrap 5) como design system, usando el JavaScript que trae incorporado para su funcionamiento
- **PostgreSQL** como sistema gestor de base de datos de producción
- **Autenticación, autorización, permisos, grupos, sesiones y administración de usuarios nativos de Django**

Las bibliotecas frontend de terceros DEBEN servirse desde recursos estáticos propios, con versión fija, sin depender de CDN externos en producción.

### Base de datos

PostgreSQL DEBE ser el sistema gestor de base de datos de referencia para producción y para las validaciones de integración que dependan del comportamiento de la base de datos. SQLite PUEDE usarse en desarrollo local, pero NO sustituye las validaciones contra PostgreSQL. Toda funcionalidad que dependa de comportamiento específico de PostgreSQL DEBE declararse en su especificación y validarse contra PostgreSQL.

### Estructura de directorios

```
├── .env.example
├── apps/
│   └── common/
├── config/
├── docs/
├── media/
├── static/
│   └── project/
│       ├── css/
│       ├── img/
│       └── js/
└── templates/
    └── components/
```

La estructura aplica sin perjuicio de los directorios y archivos propios de las herramientas de flujo de trabajo (`.specify/`, `specs/`, etc.) y de configuración del repositorio (`manage.py`, `.gitignore`).

### Directrices de estructura

- Las aplicaciones Django del ERP DEBEN ubicarse dentro de `apps/`. `apps/common/` DEBE contener exclusivamente componentes técnicos compartidos (modelo base de inactivación, mixins, validadores, utilidades) que no pertenezcan a ningún módulo de negocio ni de capacidad transversal.
- La configuración del proyecto Django DEBE ubicarse en `config/`.
- Los templates globales DEBEN ubicarse bajo `templates/`; los específicos de cada aplicación DEBEN organizarse evitando colisiones y duplicación (por ejemplo, con espacio de nombres por aplicación). Los componentes de interfaz reutilizables DEBEN ubicarse en `templates/components/`.
- Los archivos JavaScript y CSS específicos del proyecto DEBEN almacenarse en `static/project/js/` y `static/project/css/`; las imágenes institucionales, en `static/project/img/`. Las bibliotecas de terceros (HTMX, Alpine.js, Tabler.io) DEBEN ubicarse en directorios propios bajo `static/`, separados de `static/project/`, con versión fija.
- La documentación técnica y funcional del proyecto DEBE ubicarse en `docs/`.

### Presentación y estilos en código

**Generar HTML mediante strings construidos en código Python cuando dicho contenido corresponda a una plantilla de presentación está prohibido.** Se exceptúan los fragmentos mínimos generados con utilidades nativas de Django que escapen los datos (por ejemplo, `format_html` en las columnas de Django Admin).

**Los estilos CSS inline escritos en templates y la construcción de estilos CSS desde código backend están prohibidos.** La manipulación de estilos en tiempo de ejecución por las bibliotecas del stack (Alpine.js, HTMX, Tabler) no se considera estilo inline escrito.

### Configuración de entorno y dependencias

La configuración dependiente del entorno y toda información sensible DEBEN proporcionarse a la aplicación mediante variables de entorno. En desarrollo local, las variables DEBEN gestionarse mediante un archivo `.env` en la raíz del proyecto, que **NO DEBE incluirse en control de versiones**. El repositorio DEBE incluir `.env.example` con los nombres de las variables requeridas y valores ficticios o vacíos, sin secretos reales.

Credenciales, claves secretas, contraseñas, tokens (incluidos los de servicios de terceros como mapas), cadenas de conexión y otra información sensible **NO DEBEN escribirse directamente en código fuente, archivos versionados, templates o archivos de configuración.** La configuración de Django DEBE obtener estos valores del entorno y DEBE fallar explícitamente cuando una variable requerida no esté definida.

Las dependencias DEBEN declararse de forma explícita, reproducible y versionada. Los entornos virtuales y sus archivos NO DEBEN incluirse en control de versiones.

### Localización

El idioma de la aplicación DEBE ser `es` y la zona horaria de presentación `America/Lima`. El sistema DEBE usar fechas y horas con zona horaria (`USE_TZ`), almacenadas en UTC. Los formatos de fecha, número y moneda DEBEN ser consistentes en todo el sistema y definirse en un único lugar de la configuración.

---

## Estándares de UI/UX y Accesibilidad

### Consistencia y profesionalismo

La experiencia de usuario DEBE ser consistente en todos los módulos del ERP. El sistema DEBE proporcionar componentes administrativos reutilizables para patrones de interfaz comunes, y los módulos DEBEN usarlos en lugar de implementar variantes propias.

Las interfaces DEBEN mantener navegación consistente, jerarquía visual clara y acceso predecible. La estructura específica PUEDE variar según el contexto funcional.

La interfaz DEBE seguir un diseño institucional, profesional, sobrio, minimalista, claro y acogedor para el usuario. **La simplicidad, la comprensión de acciones y la prevención de errores DEBEN tener prioridad sobre elementos puramente decorativos.** Todos los módulos DEBEN proporcionar una interfaz responsive para escritorio, tablet y móvil, siguiendo un enfoque **mobile first**.

**Los mensajes orientados al usuario DEBEN escribirse en español con tono formal, claro, preciso y orientado a la acción.**

Los mensajes de éxito y de error DEBEN mostrarse mediante los componentes transversales establecidos para tal fin; los módulos NO DEBEN implementar mecanismos propios de notificación.

### Accesibilidad

La interfaz DEBE cumplir como mínimo WCAG 2.1 nivel AA. DEBE permitir completar todos los flujos esenciales mediante teclado y mantener un orden de foco lógico. Los controles interactivos DEBEN usar HTML semántico y proporcionar información accesible suficiente para tecnologías de asistencia.

Los cambios parciales de contenido (actualizaciones HTMX, mensajes de error o de éxito) DEBEN anunciarse a las tecnologías de asistencia mediante regiones `aria-live` o una gestión de foco equivalente.

### Identidad visual

La identidad visual institucional DEBE usar la siguiente paleta, cuyos valores se definen únicamente en esta constitución y en un único archivo de tokens de estilo ubicado en `static/project/css/`. Ningún otro archivo, template o código DEBE repetir estos valores:

- `#A42622`: Color institucional principal
- `#EAE4D2`: Color institucional claro
- `#7A7562`: Color institucional neutro

Toda combinación de colores DEBE cumplir el contraste mínimo de WCAG AA (4.5:1 para texto normal y 3:1 para texto grande y componentes de interfaz). **El color NO DEBE ser el único medio para comunicar estado, significado o resultado de una operación.**

---

## Validación, Normalización y Testing

### Validación de datos

Cada dato recibido por el sistema DEBE ser validado y normalizado antes de su persistencia final, sea cual sea su vía de entrada (formularios, endpoints HTMX o, de existir, APIs). **La validación autoritativa DEBE ejecutarse en el servidor y NO DEBE depender de JavaScript.** La validación en el navegador (por ejemplo, con Alpine.js) PUEDE usarse como ayuda de usabilidad, pero NO sustituye a la del servidor.

Las reglas de normalización DEBEN garantizar una representación consistente y canónica de los datos. La normalización NO DEBE modificar información cuyo formato o representación tenga significado propio dentro del dominio.

**Los datos inválidos NO DEBEN persistirse ni producir modificaciones al estado del sistema.** Las reglas de validación DEBEN implementarse en la capa Django apropiada, priorizando formularios, modelos, validadores y restricciones de base de datos.

### Manejo de errores

Cuando un formulario contenga errores, la interfaz DEBE:

- Preservar los datos válidos ingresados por el usuario
- Identificar claramente los campos que contienen errores
- Mostrar mensajes específicos y comprensibles cerca del campo afectado
- Permitir al usuario identificar y corregir errores sin ambigüedad

Cuando una operación se complete exitosamente, el sistema DEBE proporcionar retroalimentación clara y oportuna.

### Integración con Django Admin

Los modelos de negocio que requieran consulta, supervisión, parametrización o mantenimiento administrativo DEBEN tener una interfaz adecuada en Django Admin. La integración DEBE usar las capacidades nativas de Django y respetar las reglas de autenticación, autorización, integridad, inactivación y auditoría de esta constitución.

**La disponibilidad de un modelo en Django Admin NO DEBE implicar acceso irrestricto a sus datos ni permitir eludir reglas de negocio, validación o normalización.**

**Django Admin DEBE considerarse una herramienta administrativa y de soporte interno y NO DEBE usarse como sustituto de interfaces funcionales destinadas a usuarios finales del ERP.**

### Requisitos de testing

Cada funcionalidad nueva o modificada DEBE tener tests proporcionales a su comportamiento y riesgo.

La suite de tests DEBE ejecutarse y aprobarse contra PostgreSQL antes de cualquier despliegue a producción.

Los tests DEBEN incluir, según aplique:

- Lógica de dominio
- Validaciones
- Permisos, autorización y denegación por defecto
- Operaciones que modifiquen información institucional, incluida la auditoría correspondiente
- Inactivación, unicidad (incluida la detección de duplicados contra registros inactivos), reactivación y borrado desde Django Admin
- Entidades de identidad: verificación de que NO poseen campo de estado activo/inactivo, que NO admiten eliminación (incluida desde Django Admin) y que los estados de sus roles, relaciones y procesos residen en entidades que sí usan el mecanismo único de inactivación
- Flujos críticos de usuario
- Integración entre componentes cuando el comportamiento no pueda validarse adecuadamente mediante tests unitarios aislados

**Una funcionalidad NO DEBE considerarse completa cuando falle tests aplicables, salvo excepción aprobada conforme a la Gobernanza.**

---

## Gobernanza

### Enmienda de la constitución

Cualquier desviación permanente respecto de los principios, restricciones tecnológicas o estándares de esta constitución requiere una enmienda explícita:

1. **Propuesta**: redactar el cambio indicando el principio o sección afectada, la justificación y el impacto esperado.
2. **Aprobación**: la enmienda DEBE ser revisada y aprobada por el Responsable Técnico del Proyecto antes de su integración.
3. **Registro**: toda enmienda DEBE actualizar `CONSTITUTION_VERSION` y `LAST_AMENDED_DATE` conforme a la política de versionado, añadir una entrada a `docs/historial-constitucion.md` (fecha, versión, resumen del cambio y aprobador) e integrarse en un commit propio. El Sync Impact Report generado por `/speckit.constitution` es un instrumento temporal de revisión y NO sustituye al historial. Tras cada enmienda DEBEN revisarse las plantillas y artefactos dependientes.
4. **Efectividad**: la enmienda entra en vigencia únicamente al momento de su registro formal conforme al punto 3.

El **Responsable Técnico del Proyecto** es la persona o comité designado institucionalmente para aprobar enmiendas y excepciones.

El Responsable Técnico vigente consta en `docs/responsables.md`, con su nombre, cargo, documento de designación y fecha. Todo cambio de responsable DEBE registrarse allí y NO requiere enmienda de esta constitución.

### Excepciones

Una excepción es una desviación puntual, temporal y documentada respecto de un estándar, que no modifica la constitución. DEBE indicar su alcance, justificación, riesgo aceptado, aprobador y fecha de revisión o vencimiento; DEBE ser aprobada por el Responsable Técnico del Proyecto y registrarse en `docs/`.

Las excepciones SOLO PUEDEN aplicarse a los estándares de testing, de estructura de directorios y de UI/UX. NO PUEDEN aplicarse a los Principios II y III. Toda desviación de los Principios I y IV o de las restricciones tecnológicas requiere enmienda.

### Limitaciones del stack

En caso de que una funcionalidad no se pueda implementar con las características nativas de Django ni con el stack establecido, se deberá informar al desarrollador sobre la limitación y proponer alternativas compatibles con esta constitución antes de implementar. Si la alternativa elegida implica una desviación, DEBE tramitarse como enmienda o excepción según corresponda.

### Revisión de cumplimiento

- Toda especificación, plan y tarea DEBE ser revisada contra esta constitución antes de su aprobación e implementación.
- Las especificaciones DEBEN identificar explícitamente los requisitos de autenticación, autorización, auditoría, protección de datos e información sensible aplicables.
- Las desviaciones que no hayan sido enmendadas ni exceptuadas constituyen incumplimiento y DEBEN corregirse o tramitarse antes de considerarse aceptables.

**Version**: 1.0.0 | **Ratified**: 2026-10-27 | **Last Amended**: 2026-10-27