# Roadmap del LMS Big Data

## Objetivo

Construir una plataforma de aprendizaje propia para Big Data que combine las capacidades operativas esperables de un LMS maduro con una ventaja específica del curso: laboratorios técnicos verificables, seguimiento por evidencia y vistas docentes que permitan intervenir durante la clase.

El objetivo no es copiar Moodle, Brightspace, Blackboard o Classroom pantalla por pantalla. El criterio es cubrir las capacidades que resuelven problemas reales de estudiantes y docentes, manteniendo una experiencia más ligera y orientada al trabajo práctico.

## Principios de producto

1. **Una sola identidad, permisos por curso.** La cuenta LMS puede ser compartida por varios cursos; suspender una matrícula no debe desactivar la identidad global.
2. **El progreso oficial vive en backend.** LocalStorage sirve para comodidad de interfaz, nunca como expediente académico.
3. **Evidencia antes que clics.** Abrir una página no equivale a completar una actividad.
4. **Analítica para intervenir, no para vigilar.** Tiempo y actividad son señales diagnósticas; no otorgan nota por velocidad.
5. **Toda acción administrativa sensible deja auditoría.**
6. **Privacidad por diseño.** Las páginas públicas no contienen roster, notas, correos ni credenciales.
7. **Mobile y accesibilidad son requisitos, no mejoras posteriores.**
8. **La plataforma debe degradar con elegancia.** Si una integración externa falla, el estudiante conserva una ruta clara para continuar.

## Estado actual

### Implementado

- **Fase 1 · Operación docente segura**
  - identidad LMS compartida;
  - matrícula por curso/cohorte;
  - solicitudes de acceso;
  - administrador docente de usuarios;
  - suspensión/reactivación por curso;
  - sesiones y revocación;
  - recuperación/restablecimiento de credenciales;
  - exportación de cohorte y auditoría.
- **Fase 2 · Columna vertebral S01–S16**
  - sesiones declarativas con borrador/visible/cerrado;
  - recursos por sesión;
  - calendario, anuncios y pendientes;
  - portal “qué sigue”;
  - gestor docente del curso.
- **Fase 3 · Evaluación y Gradebook**
  - texto, URL, evidencia automática y archivos privados mediante URLs firmadas;
  - intentos, fechas límite, estados y accommodations;
  - rúbricas reutilizables;
  - retroalimentación e historial de cambios de nota;
  - categorías y ponderaciones;
  - banco versionado de preguntas;
  - quizzes con aleatorización, límite de tiempo, autocalificación y revisión manual;
  - sincronización quiz → Gradebook.
- **Fase 4 · Competencias y dominio**
  - marco de competencias;
  - mapeo evidencia → competencia;
  - reglas transparentes de dominio;
  - vistas estudiante y cohorte.
- **Fase 5 · Analítica e intervención**
  - señales explicables;
  - snapshots longitudinales;
  - fricción por actividad;
  - intervenciones privadas y seguimiento;
  - analítica de cohorte.
- **Fase 6 · Colaboración**
  - equipos;
  - entregas grupales con responsabilidad individual;
  - discusiones por sesión;
  - menciones y respuestas dirigidas;
  - FAQ mediante respuestas destacadas;
  - revisión por pares.
- **S08 · TC1 V4**
  - SECOP Data Pipeline;
  - API + concurrencia;
  - evidencia verificable;
  - integración NoSQL;
  - WALL y validación server-side.
- RLS y revocación de acceso directo para tablas académicas.
- QA acumulativo con guardia explícita para no modificar S07.
- S07 mantiene su archivo fuente protegido por SHA.

### En curso / siguiente

- **Fase 7 · Integraciones y estándares · en curso.**
  - implementado: centro docente de interoperabilidad;
  - implementado: exportación QTI 3 del banco activo de preguntas;
  - implementado: perfil de compatibilidad OneRoster 1.2.1 CSV en modo Bulk;
  - implementado: iCalendar para fechas realmente registradas;
  - implementado: exportación simple del Gradebook;
  - implementado: documentación de versiones, PII y límites de certificación;
  - pendiente: API pública documentada para integraciones autorizadas;
  - pendiente: webhooks salientes firmados y reintentos;
  - pendiente: importación QTI/roster con validación previa;
  - pendiente: Edu-API institucional para educación superior si la universidad dispone de contraparte;
  - pendiente: xAPI/Caliper solo si existe consumidor;
  - pendiente: integración opcional con GitHub;
  - pendiente: políticas de retención de archivos.
- **Fase 8 · Plataforma, accesibilidad y confianza.**
  - permisos más granulares;
  - SSO/OIDC y MFA cuando la institución provea identidad compatible;
  - observabilidad y rate limiting;
  - backup/restore;
  - WCAG 2.2 AA y pruebas responsive formales.

### Dependencias externas no simuladas

LTI institucional, SSO/OIDC, sincronización OneRoster y envío xAPI/Caliper requieren endpoints, client IDs, secretos o consumidores externos. El LMS puede dejar adaptadores y contratos listos, pero esas integraciones solo se marcarán “activas” cuando exista una contraparte institucional real.

## Fase 1 · Operación docente segura

**Meta:** que el profesor pueda operar la cohorte sin entrar a Supabase.

- Administrador de usuarios y matrícula.
- Ficha individual de estudiante.
- Sesiones/dispositivos y revocación.
- Restablecimiento de credenciales con advertencia de alcance.
- Solicitudes de acceso.
- Auditoría.
- Exportación de cohorte.

**Criterio de salida:** todas las operaciones habituales de acceso de Big Data se realizan desde el LMS y quedan trazadas.

## Fase 2 · Columna vertebral del curso

**Meta:** que el LMS represente las 16 sesiones y sea la puerta principal del curso.

- Modelo declarativo S01–S16.
- Estado de publicación por sesión: borrador, visible, cerrado.
- Recursos, presentación, laboratorio, lectura y evidencia por sesión.
- Prerrequisitos y reglas de liberación cuando tengan valor pedagógico.
- Calendario con sesiones, entregas y fechas límite.
- Anuncios fijados y comunicaciones del curso.
- Panel estudiante con “qué sigue”, pendientes y actividad reciente.
- Vista docente de cohorte longitudinal.

**Criterio de salida:** un estudiante puede saber desde el portal qué debe hacer hoy, qué debe entregar y qué tiene pendiente sin consultar otro canal.

## Fase 3 · Evaluación y libro de calificaciones

**Meta:** convertir las evaluaciones en un subsistema general, no en lógica específica por sesión.

- Entregas de texto, URL, archivo y evidencia validada automáticamente.
- Intentos, fechas límite y estados de entrega.
- Rúbricas reutilizables con criterios observables.
- Retroalimentación individual.
- Libro de calificaciones por actividad, sesión, módulo y curso.
- Categorías y ponderaciones.
- Excepciones/accommodations de fecha e intentos por estudiante.
- Banco de preguntas y quizzes con versiones/aleatorización cuando sea pedagógicamente pertinente.
- Historial de cambios de nota.

**Criterio de salida:** cualquier nueva sesión puede añadir una evaluación sin crear una Edge Function específica para ese único caso.

## Fase 4 · Competencias y dominio

**Meta:** mostrar qué sabe hacer el estudiante, no solo qué nota obtuvo.

- Marco de competencias del curso.
- Mapeo actividad → competencia.
- Evidencias múltiples por competencia.
- Niveles de dominio y reglas transparentes.
- Vista de dominio por estudiante y por cohorte.
- Prerrequisitos de aprendizaje basados en competencias cuando tenga sentido.
- Explicación visible de por qué una competencia aparece lograda o pendiente.

**Criterio de salida:** una nota alta y una competencia lograda dejan de ser sinónimos automáticos; ambas se pueden explicar con evidencia.

## Fase 5 · Analítica e intervención docente

**Meta:** que la analítica sugiera dónde mirar y facilite actuar.

- Actividad reciente, pendientes, entregas vencidas y progreso.
- Fricción por actividad: intentos, abandonos y errores frecuentes.
- Alertas configurables con reglas explicables.
- Ficha de intervención: nota docente privada, acción tomada y seguimiento.
- Comparación temporal del estudiante consigo mismo.
- Resumen de cohorte y exportaciones.
- Detección de anomalías instrumentales separada de “riesgo académico”.
- Panel en vivo para sesiones con ejercicios sincronizados.

**Criterio de salida:** cada alerta muestra la evidencia que la originó y ofrece una acción docente concreta; ninguna etiqueta opaca decide por el profesor.

## Fase 6 · Colaboración

**Meta:** soportar el trabajo real del curso sin llevar la conversación a cinco plataformas.

- Grupos/equipos con vigencia por actividad.
- Entregas grupales y responsabilidad individual.
- Discusiones ligadas a sesiones.
- Revisión por pares con rúbrica.
- Comentarios y menciones.
- Espacios de preguntas frecuentes con respuestas docentes fijadas.

**Criterio de salida:** un trabajo en pareja o equipo tiene membresía, evidencia, entrega y retroalimentación trazables.

## Fase 7 · Integraciones y estándares

**Meta:** evitar encerrar el curso en una plataforma aislada.

- Centro docente que distingue exportaciones disponibles, configuración pendiente e integraciones externas no configuradas.
- Exportación QTI 3 del banco de preguntas; importación pendiente.
- OneRoster 1.2.1 CSV como perfil de compatibilidad; para educación superior se prioriza evaluar Edu-API con la institución.
- iCalendar y Gradebook CSV.
- API documentada y webhooks firmados pendientes.
- LTI 1.3 para herramientas externas solo cuando exista plataforma y credenciales reales.
- xAPI o Caliper solo si existe un consumidor institucional.
- Integración opcional con repositorios GitHub para evidencias técnicas.
- Almacenamiento de archivos con URLs firmadas ya implementado; política de retención pendiente.

**Criterio de salida:** datos académicos esenciales se pueden exportar y las integraciones no dependen de copiar secretos al navegador.

## Fase 8 · Plataforma, accesibilidad y confianza

**Meta:** que el LMS pueda sostener más cursos sin degradar seguridad ni experiencia.

- Roles y permisos granulares.
- SSO institucional/OIDC cuando esté disponible.
- MFA para roles docentes/administrativos.
- Políticas de sesión y recuperación de cuenta.
- Auditoría consultable y exportable.
- Retención y borrado de datos documentados.
- Backups y procedimiento de recuperación.
- Observabilidad: errores frontend, Edge Functions y consultas críticas.
- Límites/rate limiting para acciones sensibles.
- WCAG 2.2 AA: teclado, foco, contraste, lectores de pantalla y movimiento reducido.
- Pruebas responsive en teléfono, tablet y escritorio.
- PWA/offline solo para contenidos que realmente se beneficien de ello.

**Criterio de salida:** existe una matriz de permisos, una prueba de restauración, un checklist de accesibilidad y un tablero de salud operacional.

## Ventaja diferencial que sí vale construir

La plataforma no ganará por tener más menús que un LMS comercial. Puede destacar si hace especialmente bien estas cuatro cosas:

1. **Laboratorios ejecutables con evidencia verificable.**
2. **Explicación del progreso a nivel de etapa y competencia.**
3. **WALL docente en vivo para ejercicios técnicos.**
4. **Ruta de aprendizaje que conecta presentación, ejecución, evidencia, retroalimentación y siguiente decisión.**

Esas capacidades deben ser el núcleo; calendario, notas, usuarios y comunicaciones son infraestructura necesaria para que ese núcleo sea usable.

## Próximos incrementos recomendados

1. Cerrar fase 7 con **exportaciones estándar primero**: QTI, roster/gradebook, calendario y API documentada.
2. Añadir **webhooks firmados** y registro de entregas/reintentos.
3. Preparar adaptadores LTI 1.3, OneRoster y xAPI/Caliper sin declararlos activos hasta tener credenciales institucionales.
4. Integrar GitHub opcionalmente para evidencias técnicas, usando permisos mínimos.
5. Ejecutar fase 8: matriz de permisos, observabilidad, backup/restore, rate limiting y recuperación.
6. Cerrar con una auditoría WCAG 2.2 AA + pruebas responsive en teléfono, tablet y escritorio.

