# Experiencia LMS V3 · Big Data 2026-2S

## Objetivo

Convertir BigData2026 en una experiencia de aprendizaje integrada: el estudiante entra una sola vez, queda identificado para todo el curso, abre cada sesión desde un módulo único y mantiene su identidad mientras recorre presentación, laboratorios HTML, progreso, evidencias y WALL. El docente observa avance útil en vivo sin convertir tiempo o velocidad en nota.

La plataforma debe conservar lo ya construido (identidad, matrícula, S08, S09, gradebook, quizzes, competencias, colaboración, interoperabilidad) y eliminar excepciones específicas por sesión.

## Principios de producto

1. Una identidad por navegador/sesión, no un login por recurso.
2. El módulo de sesión es la puerta de entrada obligatoria a los recursos de esa sesión.
3. Visitar no equivale a completar; completar no equivale a dominar.
4. Los laboratorios HTML del mismo origen heredan identidad y registran eventos automáticamente.
5. Recursos externos, como Colab, registran lanzamiento y retorno/evidencia, pero no pueden heredar silenciosamente la sesión del navegador por restricciones de origen.
6. El WALL sirve para acompañar, no para clasificar por velocidad.
7. La arquitectura de S09 se vuelve genérica para S10-S16.
8. S07 permanece protegida hasta que se decida una migración explícita.
9. Mobile-first, WCAG 2.2 AA y QA visual forman parte del Definition of Done.
10. El progreso oficial vive en backend; localStorage solo puede mejorar UX, nunca ser expediente académico.

---

## 1. Arquitectura de navegación objetivo

### Entrada pública

`/`

Debe dejar de actuar como LMS paralelo. Su función será:

- presentación del curso;
- sesión actual;
- botón principal **Entrar al aula**;
- si existe sesión válida, botón **Continuar mi curso**;
- información pública mínima;
- nunca mostrar progreso oficial desde localStorage.

### Home autenticado

`/lms/portal.html`

Debe convertirse en un dashboard de curso con cinco destinos principales:

- Inicio
- Módulos
- Pendientes
- Mi progreso
- Comunidad

Para docente/admin se agrega **Gestión**.

### Módulo genérico

`/lms/session.html?s=09`

Una única plantilla debe poder representar S01-S16.

Bloques:

1. cabecera de sesión;
2. identidad activa;
3. objetivo y resultados de aprendizaje;
4. progreso de la sesión;
5. siguiente acción recomendada;
6. ruta secuencial de actividades;
7. recursos;
8. evidencias/checkpoints;
9. cierre y transferencia;
10. acceso a progreso personal.

### Recurso interno

Ejemplos:

- `/Presentaciones/s09-de-palabras-a-significado.html`
- `/assets/tutoriales/...`
- laboratorios HTML.

Regla:

- sin sesión válida → volver al módulo;
- con sesión válida → abrir directamente;
- el recurso registra entrada, actividad y salida;
- al cerrar, el estudiante vuelve al módulo con estado actualizado.

### Recurso externo

Ejemplo: Colab.

Flujo:

`módulo → registrar launch → abrir Colab → realizar práctica → volver al LMS → entregar/verificar evidencia`

No se debe afirmar que Colab “hereda” automáticamente la sesión LMS. El navegador no comparte localStorage entre `jazaineam1.github.io` y `colab.research.google.com`.

---

## 2. Modelo pedagógico de cada sesión

Cada sesión debe declararse como una ruta de actividades, no como un conjunto de enlaces.

Tipos:

- `content`: explicación/presentación;
- `interactive_lab`: laboratorio HTML autenticado;
- `notebook`: ejecución externa reproducible;
- `challenge`: pregunta formativa;
- `evidence`: evidencia verificable;
- `discussion`: interacción;
- `reflection`: cierre/transferencia.

Estados de actividad:

- `locked`
- `not_started`
- `in_progress`
- `completed`
- `mastered`
- `needs_attention`

Tipos de regla de finalización:

- abrir;
- recorrer un umbral de contenido;
- responder;
- alcanzar dominio;
- enviar evidencia;
- validación automática;
- validación docente.

**Nunca** usar tiempo activo como criterio de aprobación.

---

## 3. Modelo de tracking genérico

S08 y S09 no deben seguir creciendo como APIs independientes por sesión.

Crear una capa común sobre las tablas existentes, reutilizando equivalentes donde ya existan.

### Evento canónico

Campos mínimos:

- `course_run`
- `session_number`
- `user_id`
- `activity_code`
- `resource_id`
- `event_type`
- `client_at`
- `server_at`
- `active_seconds_delta`
- `metadata` minimizada

Eventos:

- `session_entered`
- `resource_opened`
- `resource_closed`
- `slide_viewed`
- `lab_started`
- `lab_attempted`
- `lab_mastered`
- `evidence_submitted`
- `evidence_verified`
- `discussion_posted`
- `session_completed`
- `heartbeat`

### Estado derivado

No recalcular la UI leyendo miles de eventos. Mantener un estado agregado por estudiante/actividad:

- primer intento;
- intentos;
- dominio;
- último paso;
- último acceso;
- tiempo activo aproximado;
- evidencia;
- completion status.

---

## 4. Identidad y sesión

### UX

El estudiante se identifica una vez.

Después del login:

- el header muestra nombre/rol;
- todos los recursos internos reconocen la sesión;
- no se pide alias nuevamente;
- no se pide código de partida salvo que exista una actividad sincrónica deliberada;
- volver atrás no pierde contexto;
- recargar no pierde progreso.

### Seguridad

La implementación actual usa token en localStorage sobre `jazaineam1.github.io`. Para una plataforma académica más robusta:

- tokens cortos;
- rotación/revocación;
- mínima PII en cliente;
- CSP estricta;
- evitar scripts de terceros dentro de páginas autenticadas;
- evaluar dominio propio + cookie segura HttpOnly cuando sea viable;
- mantener auditoría de acciones sensibles.

No guardar notas, roster ni credenciales en páginas públicas.

---

## 5. Nuevo módulo de sesión

Diseño desktop:

- rail lateral: mapa de actividades;
- centro: actividad actual / resumen;
- rail derecho: progreso, identidad, próximos pasos.

Diseño móvil:

- una sola columna;
- barra superior compacta;
- navegación inferior: Inicio / Ruta / Progreso / Ayuda;
- botones mínimo 44×44;
- sin tablas obligatorias horizontales.

Cada actividad muestra:

- tipo;
- duración estimada;
- qué aprenderé;
- qué debo hacer;
- qué se registra;
- criterio de finalización;
- estado;
- botón continuar.

La acción primaria siempre es única: **Continuar**.

---

## 6. Presentaciones y laboratorios

### Presentación

La presentación sigue siendo un recurso pedagógico, no el LMS completo.

Debe recibir del LMS:

- identidad;
- sesión;
- actividad;
- último slide;
- estado de desafíos.

Debe devolver:

- slide visitado;
- desafío intentado;
- dominio;
- actividad;
- salida.

### Laboratorios interactivos

Los laboratorios que el docente necesita ver en vivo deben ser preferentemente HTML same-origin.

Ventajas:

- heredan identidad;
- pueden registrar intentos;
- pueden reportar estado inmediatamente;
- pueden reanudarse;
- alimentan el WALL sin pedir credenciales extra.

Colab queda para ejecución reproducible y código real, no como único mecanismo de seguimiento en vivo.

---

## 7. WALL docente unificado

Ruta objetivo:

`/lms/wall.html?s=09`

No crear un WALL distinto por cada sesión.

### Cabecera

- sesión activa;
- estudiantes activos ahora;
- iniciaron / no iniciaron;
- completaron;
- dominio por checkpoint;
- incidencias instrumentales.

### Matriz central

Una fila por estudiante.

Columnas configurables:

- estudiante;
- presencia;
- actividad actual;
- progreso de ruta;
- checkpoint actual;
- primer intento;
- dominio;
- evidencia;
- última actividad;
- tiempo activo aproximado.

### Filtros

- todos;
- no iniciaron;
- en curso;
- requieren ayuda;
- completaron;
- actividad específica;
- búsqueda por nombre.

### Vista de detalle

Al abrir un estudiante:

- línea de tiempo;
- actividades;
- intentos;
- evidencias;
- feedback;
- notas privadas del docente;
- intervención.

### Realtime

Objetivo:

- Supabase Realtime cuando sea conveniente;
- fallback de polling;
- indicador explícito de “última actualización”.

El WALL no ordena por rapidez.

---

## 8. Progreso del estudiante

Ruta:

`/lms/progress.html`

Debe consolidar:

- avance por sesión;
- actividades terminadas;
- competencias;
- entregas;
- quizzes;
- feedback;
- evidencias;
- próximos pendientes.

Separar visualmente:

- **Visitado**
- **Completado**
- **Dominado**
- **Calificado**

Esto evita que una barra de progreso confunda navegación con aprendizaje.

---

## 9. Corrección de gráficas y regla visual

### Regla base

Ninguna gráfica puede pintar fuera de su contenedor.

Requisitos:

- todos los SVG con `viewBox`;
- `preserveAspectRatio="xMidYMid meet"`;
- wrapper `.viz-frame` con `overflow:hidden`;
- SVG con `max-width:100%`, `max-height:100%`;
- prohibir `overflow:visible` en gráficas de presentación;
- grid children con `min-width:0`;
- tablas en wrapper de scroll;
- código con overflow interno;
- controles fijos nunca deben tapar contenido.

### Presentaciones 16:9

En escritorio:

- todo el contenido principal cabe en el stage;
- 75–90% de ocupación útil;
- ninguna caja sale por laterales;
- si una diapositiva necesita scroll para ser entendida, se divide o se rediseña.

En móvil:

- se permite scroll vertical;
- nunca scroll horizontal global.

### QA automático

Agregar Playwright a CI y probar, como mínimo:

- 1280×720
- 1366×768
- 1536×864
- 1920×1080
- 390×844
- 412×915
- tablet 768×1024

Asserts:

- `document.documentElement.scrollWidth <= innerWidth + tolerancia`;
- ningún SVG excede su `.viz-frame`;
- ningún elemento principal intersecta navegación fija;
- botones visibles y ≥44 px;
- screenshots de slides críticas;
- contraste y foco básico.

---

## 10. Home del curso de vanguardia

El dashboard no debe abrir mostrando una parrilla de 16 sesiones como único centro.

Orden recomendado:

1. **Continúa donde quedaste**
2. **Hoy / próxima sesión**
3. **Pendientes**
4. **Ruta de aprendizaje**
5. **Feedback reciente**
6. **Competencias**
7. **Anuncios**
8. **Calendario**

La ruta de 16 sesiones queda accesible, pero secundaria frente a la siguiente acción.

---

## 11. Inspiraciones funcionales

Tomar patrones, no copiar interfaces:

- Canvas: módulos, requisitos, prerrequisitos, publicación y progresión.
- Brightspace: progreso por múltiples indicadores y vista individual/cohorte.
- Blackboard Ultra: estados claro de progreso y bloqueo en learning modules.
- Moodle: completion criteria + restrict access.

Diferenciador Big Data:

- laboratorios ejecutables;
- evidencias técnicas verificables;
- WALL en vivo;
- primer intento vs dominio;
- misma ruta presentación → laboratorio → evidencia → feedback.

---

## 12. Plan de implementación

### Incremento A · estabilización visual

- corregir overflow SVG S09;
- estandarizar `.viz-frame`;
- revisar todas las gráficas S09;
- agregar QA responsive/overflow;
- mantener S07 intacta.

### Incremento B · puerta única

- convertir index en gateway;
- retirar progreso local como progreso “oficial”;
- portal como home autenticado;
- sesión actual coherente con el calendario real del curso;
- login único y retorno seguro.

### Incremento C · módulo genérico

- crear `session.html?s=n`;
- mover estructura S09 a configuración declarativa;
- recursos con estados y criterios;
- navegación continuar/anterior;
- progreso agregado.

### Incremento D · tracking genérico

- endpoint común de eventos;
- actividad/estado por sesión;
- migrar S09 sin perder datos;
- adaptar S08;
- eliminar necesidad de una Edge Function por sesión.

### Incremento E · WALL unificado

- `wall.html?s=n`;
- presencia;
- progreso;
- dominio;
- evidencias;
- filtros;
- detalle por estudiante;
- Realtime/polling.

### Incremento F · experiencia estudiante

- progreso unificado;
- feedback;
- pendientes;
- competencias;
- notificaciones de siguiente acción;
- retorno de recursos externos.

### Incremento G · S10-S16

Toda nueva sesión se publica mediante datos/configuración, sin crear arquitectura adicional.

---

## 13. Criterios de aceptación

Un estudiante nuevo debe poder:

1. entrar a Big Data;
2. identificarse una vez;
3. ver qué sigue;
4. abrir S09;
5. abrir la presentación sin volver a identificarse;
6. resolver laboratorios;
7. ver su progreso;
8. abrir Colab;
9. volver y registrar evidencia;
10. cerrar sesión.

El docente debe poder:

1. abrir el WALL;
2. saber quién inició;
3. ver dónde está cada estudiante;
4. distinguir primer intento de dominio;
5. encontrar fricción;
6. abrir detalle;
7. revisar evidencias;
8. exportar o usar gradebook cuando corresponda.

La plataforma pasa QA si:

- no existe overflow horizontal global;
- las gráficas están contenidas;
- mobile funciona;
- S07 conserva su SHA protegido;
- navegación y tracking no dependen de localStorage;
- CI/Pages están verdes.


---

## Estado de implementación · 26-sep-2026

### Implementado

- Gateway público sin progreso académico simulado en `localStorage`.
- Portal autenticado centrado en la siguiente acción.
- Módulo universal `/lms/session.html?s=N` para S01–S16.
- S01–S16 declaradas en la capa de sesiones; S10–S16 permanecen borrador.
- Motor Edge Function genérico `bigdata-session` por sesión y actividad.
- Tracking server-side reutilizando `bd_lms_events`, `bd_lms_session_progress` y `bd_lms_activity_progress`.
- Claves de checkpoints formativos en `bd_lms_activity_keys`, RLS habilitado y sin acceso anon/authenticated.
- S09 migrada de forma compatible al motor genérico sin exponer las respuestas correctas.
- Progreso unificado con cuatro dimensiones visibles: visitado, completado, dominado y calificado.
- WALL universal `/lms/wall.html?s=N` con búsqueda, filtros, fricción, dominio, actividad actual y detalle individual.
- Ficha docente de estudiante con línea de tiempo de eventos de la sesión.
- Inicio oficial y reinicio protegido por sesión con auditoría.
- Bridge de identidad/tracking para las guías HTML same-origin de S04–S06.
- S08 accesible desde el módulo universal sin modificar su archivo evaluativo protegido.
- S07 conserva su SHA protegido y no se modifica.
- Contención SVG S09 y estándar compartido `.viz-frame`.
- QA visual con Playwright en laptop, escritorio, tablet y móvil.
- Recorrido automático de las 35 diapositivas S09 para detectar overflow.
- Auditoría automatizada de accesibilidad con axe sobre landing y módulo.
- Playwright y axe fijados a versiones concretas en `package.json`.

### Decisiones deliberadas / límites reales

- **Colab es cross-origin.** El LMS registra el lanzamiento y el retorno/evidencia; nunca envía el token LMS por query string ni intenta leer el almacenamiento de otro origen.
- **S07 permanece protegida.** Su experiencia legacy no se reescribe como parte de V3; el módulo universal puede registrar el acceso sin alterar el archivo fuente.
- **WALL en vivo:** con la identidad LMS actual basada en tokens propios, V3 usa polling de 15 s. Supabase Realtime/Broadcast queda preparado como evolución cuando exista un canal autenticado compatible; no se expone el token LMS en una suscripción insegura.
- **Cookies HttpOnly:** GitHub Pages no puede emitir por sí mismo una cookie HttpOnly first-party para el dominio de la Edge Function. Migrarla correctamente requiere dominio/proxy de aplicación; V3 mantiene la sesión actual, revocable y corta, sin afirmar una protección que el hosting estático no puede ofrecer.
- **SSO/OIDC institucional, MFA, LTI y Edu-API** siguen dependiendo de contraparte/credenciales institucionales y no se marcan como activas.

### Definition of Done V3

El incremento se considera publicable únicamente si:

1. QA funcional acumulativo queda verde.
2. QA visual/responsive queda verde.
3. S07 y S08 conservan sus SHA protegidos.
4. GitHub Pages publica `session.html`, `wall.html` y `progress.html`.
5. Después del despliegue, las rutas S01–S09 en la base apuntan al módulo canónico.
6. La verificación web final confirma landing, módulo y S09 sin overflow.
