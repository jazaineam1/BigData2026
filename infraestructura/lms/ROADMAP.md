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

- Login LMS compartido.
- Matrícula por curso y por cohorte.
- Solicitudes de acceso.
- Sesión 08 integrada de extremo a extremo.
- Validación server-side de `manifest_tc1.json`.
- Progreso por actividad y sesión.
- Tiempo activo con heartbeat controlado.
- WALL docente S08.
- Inicio oficial de sesión y desempate por inicio.
- Administrador docente de usuarios:
  - búsqueda y filtros;
  - matrícula de cuentas LMS existentes;
  - suspensión/reactivación de Big Data;
  - detalle del estudiante;
  - sesiones abiertas;
  - revocación de sesiones;
  - restablecimiento de contraseña;
  - solicitudes de acceso;
  - exportación CSV;
  - auditoría administrativa.
- RLS y revocación de acceso directo para las tablas académicas Big Data.
- QA con guardia explícita para no modificar S07.

### Parcial

- El portal aún representa principalmente S08, no el curso completo.
- El progreso histórico de S01–S06 no está normalizado en el expediente LMS.
- La evaluación está especializada en el manifest de S08; todavía no existe un motor general de entregas y rúbricas.
- Las comunicaciones y fechas viven fuera de un calendario LMS central.
- La analítica docente es útil para S08, pero todavía no forma una vista longitudinal del semestre.

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

- API documentada y webhooks.
- LTI 1.3 para herramientas externas cuando sea necesario.
- Importación/exportación QTI para bancos de preguntas.
- OneRoster o equivalente para sincronización de matrículas si la universidad lo habilita.
- xAPI o Caliper para eventos de aprendizaje si existe un consumidor institucional.
- Integración opcional con repositorios GitHub para evidencias técnicas.
- Integración de calendario.
- Almacenamiento de archivos con URLs firmadas y políticas de retención.

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

1. Generalizar el portal a S01–S16 y crear el modelo de sesión completo.
2. Crear calendario + anuncios + pendientes.
3. Implementar entregas/rúbricas/libro de calificaciones como motor general.
4. Añadir competencias y mapa actividad → competencia.
5. Construir analítica longitudinal + flujo de intervención.
6. Añadir colaboración e integraciones solo después de estabilizar los cinco puntos anteriores.
