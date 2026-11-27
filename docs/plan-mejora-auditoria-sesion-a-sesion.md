# Auditoría pedagógica y plan de mejora por sesión · Big Data 2026
**Fecha:** 26 de noviembre de 2026. **Rama:** mejora-pedagogica-integral. **Objeto auditado:** reconstrucción preliminar commit 88ae30d3aa157e7fadf09ea3b7bedce063c42bca y 17 cuadernos canónicos referenciados.

## Dictamen
No reemplazar materiales originales por la presentación preliminar. Las 425 pantallas constituyen una estructura funcional de navegación, no una clase completa. La nueva capa tiene 5.227 palabras de explicación breve, aproximadamente 307 por sesión y 12 por pantalla, excluyendo actividades, casos y texto previo. Hay 68 casos precalculados, 17 calculadoras y 102 referencias de celda. El informe anterior documenta pruebas en DOM simulado, no navegador, aula ni cuentas externas. Se releyeron los 17 cuadernos y se comprobaron los 102 destinos (primera línea no vacía de cada celda); algunos son separadores o secciones distintas, por lo cual estar dentro del rango no acredita alineación. Los 17 notebooks tienen cero celdas de código con salida persistida en los archivos leídos; esto NO demuestra que jamás se ejecutaran. El total de texto markdown es bruto, incluye código en bloques, títulos, posibles duplicados y referencias; no certifica 40.000 palabras elegibles y no es el total de todos los recursos. No se realizaron ejecuciones nuevas ni observación de estudiantes para esta auditoría. No se modifican materiales docentes ni evaluaciones con este documento.

## Evaluación con evidencia
La rúbrica del plan maestro (0–5, ponderaciones 20,20,20,15,10,10,5) se aplica aquí únicamente a la nueva capa de presentación; no es una nota de los estudiantes ni una evaluación cuantitativa completa del material histórico. D: profundidad; A: aprendizaje activo y autonomía; P: práctica auténtica y reproducibilidad; T: alineación/transferencia; I: interpretación; V: visual/accesibilidad; F: viabilidad temporal. 0 ausente; 1 declarado; 2 presente pero sin verificación suficiente; 3 parcial comprobado; 4 evidencia sólida; 5 verificación independiente y transferencia. La evidencia disponible justifica un perfil provisional común 2/2/2/1/2/2/1: definición y actividad presentes pero breves; 4 casos y un control funcional por sesión sin autonomía demostrada; enlace a cuaderno existente sin ejecución de la ruta reconstruida; referencias y contratos declarados pero integración no probada; límites escritos sin interpretación de salidas reales; UI simulada sin proyección; tiempos asignados sin ensayo. No se inventan diferencias de décimas por disciplina: se distinguen prioridades, evidencia y brechas concretas por sesión. En particular S03, S06, S08, S09, S12 y S14 conservan material previo más desarrollado que la nueva capa; la valoración histórica requiere evaluación de todos sus recursos, no solo esta síntesis.
La aceptación sigue siendo ≥4,5/5 y ninguna dimensión esencial menor de 4; las puertas críticas son independientes de la puntuación. No se certifica ninguna sesión.

## Referentes
- Alineación constructiva: Carnegie Mellon Eberly Center, https://www.cmu.edu/teaching/assessment/basics/alignment.html : cada objetivo requiere actividad y evidencia observable.
- Aprendizaje activo: Freeman et al. (2014), https://pubmed.ncbi.nlm.nih.gov/24821756/ ; 225 estudios universitarios STEM. No transponer directamente el tamaño de efecto a esta maestría.
- Mayer: https://doi.org/10.1017/9781108894333.019 y https://doi.org/10.1017/9781108894333.025 : coherencia, señalización, contigüidad, segmentación y preparación conceptual. La lectura extensa no se proyecta toda a la vez.
- PRIMM, https://suesentance.net/2017/09/01/primm-a-structured-approach-to-teaching-programming/ : predecir, ejecutar, investigar, modificar y crear. Adaptación a posgrado, no evidencia directa de efectividad en este grupo.
- MIT 6.5840, https://pdos.csail.mit.edu/6.5840/general.html : laboratorios para comprender mecanismos, implementar y depurar. No copiar carga de trabajo ni prerrequisitos de ese curso.

## Inventario medido
| Sesión | Explicación nueva | Markdown bruto del cuaderno | Celdas totales | Código | Salidas guardadas | Nota provisional capa nueva | Prioridad |
|---|---:|---:|---:|---:|---:|---:|---|
| S01 | 431 | 5471 | 85 | 33 | 0 | 1.80 | P1 |
| S02 | 353 | 4888 | 41 | 9 | 0 | 1.80 | P1 |
| S03 | 327 | 21277 | 130 | 54 | 0 | 1.80 | P1 |
| S04 | 303 | 4197 | 39 | 21 | 0 | 1.80 | P1 |
| S05 | 296 | 7986 | 82 | 26 | 0 | 1.80 | P1 |
| S06 | 304 | 10224 | 119 | 40 | 0 | 1.80 | P1 |
| S07 | 308 | 2705 | 31 | 12 | 0 | 1.80 | P1 |
| S08 | 292 | 11227 | 81 | 31 | 0 | 1.80 | P1 |
| S09 | 295 | 3435 | 21 | 11 | 0 | 1.80 | P1 |
| S10 | 314 | 4946 | 48 | 23 | 0 | 1.80 | P1 |
| S11 | 313 | 5490 | 73 | 31 | 0 | 1.80 | P0 |
| S12 | 258 | 10088 | 111 | 45 | 0 | 1.80 | P1 |
| S13 | 320 | 3250 | 55 | 22 | 0 | 1.80 | P0 |
| S14 | 289 | 9015 | 71 | 23 | 0 | 1.80 | P0 |
| S14A | 293 | 2386 | 28 | 9 | 0 | 1.80 | P0 |
| S15 | 266 | 864 | 19 | 6 | 0 | 1.80 | P0 |
| S16 | 265 | 3534 | 34 | 16 | 0 | 1.80 | P0 |

Totales: 5227 palabras nuevas; 110983 palabras brutas markdown; 1068 celdas totales; 412 de código. Ningún total puede compensar faltantes de una sesión. P0 = riesgo técnico, evaluación final próxima o necesidad crítica de desarrollo; P1 = reconstrucción obligatoria. La prioridad no implica que las demás sesiones estén aceptadas.

## Presupuesto editorial y tiempo
El mínimo obligatorio sigue siendo 40.000 palabras ORIGINALES por sesión: contexto 2.000, mecanismos 8.000, ejemplos y contraejemplos 6.000, experimentación 5.000, laboratorio y explicación de código 9.000, diagnóstico e interpretación 3.000, ejercicios y transferencia 5.000, profundización y síntesis 2.000. 640.000 para 16 obligatorias y 680.000 incluyendo S14A. Conteo por fuente canónica, deduplicado, sin código, datos, menús, QA ni texto repetido. No restar automáticamente el inventario bruto de la meta. Dos recursos principales: presentación con proyección y lectura ampliada; un cuaderno con código visible y práctica. Referencias, glosario y material avanzado dentro de esos recursos. Mantener enlaces históricos y material especializado como consulta integrada. El cronograma de cada capítulo se expresa en siete bloques: apertura/diagnóstico, enseñanza conceptual, ejemplo/experimentación, pausa, práctica o integración, autonomía/transferencia, cierre. Suman 150 con pausa de 10; no se garantiza la duración hasta ensayar. La agenda original de S02 de 180 y S11 de aproximadamente 54 minutos de fase 1 no se pueden mezclar sin reconciliar. Se propone distinguir núcleo de 150 y ampliación opcional, sin alterar calendario oficial. El tiempo de defensa S16 es provisional hasta comprobar número de equipos y modalidad.

## S01 · Fundamentos y adquisición
**Prioridad:** P1. **Diagnóstico verificable:** El piloto original ofrece más desarrollo que la nueva síntesis. La pantalla de paginación remite a la celda 35, que abre fragmentación, no a una práctica de offset.

**Inventario:** 431 palabras breves nuevas; 5471 palabras markdown brutas, 85 celdas y 33 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Cinco V con cola; memoria de archivo vs DataFrame; grano proceso/contrato; HTTP, esquema, orden, offset y cambios de fuente; media ponderada. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Conservar el piloto visual; agregar diagramas de cola, memoria y páginas con IDs visibles; predecir, calcular y explicar cuatro contraejemplos. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Ampliar el cuaderno con una función de adquisición paginada explícita, control de claves y cobertura sobre snapshot, comparación secuencial por bloques, manifiesto RAW y relectura; separar consulta remota real de referencia local. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Variar offset y tamaño sin copiar solución; verificar mismos IDs en fuente congelada y explicar por qué HTTP 200 no implica cobertura. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** RAW con grano, fecha, fuente, IDs, esquema y hash; S02 importa contrato.

**Tiempo propuesto:** apertura 5 min; fundamentos 30; ejemplo/experimentación 25; pausa 10; práctica 55; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Ruta local primero; llamada remota pequeña y docente. No descargar millones por defecto.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S02 · Arquitectura y requisitos
**Prioridad:** P1. **Diagnóstico verificable:** El cuaderno conserva agenda de 180 minutos y laboratorio Git de 90; las celdas 27–31 son pasos de edición y PR, no simulación de carga ni contrato ejecutable.

**Inventario:** 353 palabras breves nuevas; 4888 palabras markdown brutas, 41 celdas y 9 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** BPM AS-IS/TO-BE, requisitos funcionales y no funcionales, ciclo analítico, capacidad, costo, arquitectura por capas y contratos. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Usar diagramas de flujo con decisiones y tiempos; elegir arquitectura bajo restricciones cambiantes; diferenciar capa lógica, máquina y servicio. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Mantener experiencia Git pero crear celdas de validación de contrato, cálculo de carga, matriz con restricciones duras, diagrama generado y exportación versionada. No exigir ramas nuevas por ejercicio si no son necesarias. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Cambiar límite de frescura o latencia y demostrar cómo cambia el diseño; justificar con cálculo y prueba de contrato. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Contrato y arquitectura con consultas, esquema, versión y restricciones para S03.

**Tiempo propuesto:** apertura 5 min; fundamentos 25; ejemplo/experimentación 30; pausa 10; práctica 55; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Eliminar pasos administrativos redundantes del núcleo; conservarlos como ampliación.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S03 · MongoDB documental
**Prioridad:** P1. **Diagnóstico verificable:** El cuaderno es el más extenso del inventario; no debe perderse su desarrollo. La celda 101 corresponde al cruce de fuentes, no a medición de índices.

**Inventario:** 327 palabras breves nuevas; 21277 palabras markdown brutas, 130 celdas y 54 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** BSON, diseño embebido y referenciado, CRUD, predicados, arrays, elemMatch, agregación, índices y planes. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Representar documentos y estados de pipeline; animar cardinalidad de unwind; comparar índice compuesto mediante árbol conceptual; leer explain real. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Conservar las secciones útiles; dividir ruta esencial y avanzada. Crear pruebas de índice antes/después con la misma colección, métricas de examined/returned y control independiente; no atribuir resultados de mock al motor. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Resolver predicado sobre un array y justificar índice para consulta nueva; verificar IDs y plan auténtico. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Expediente y consulta con claves estables, evidencia de motor y exportación para S04.

**Tiempo propuesto:** apertura 5 min; fundamentos 30; ejemplo/experimentación 25; pausa 10; práctica 55; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Preflight de motor antes de clase; restringir escritura a colección aislada.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S04 · Atlas, persistencia y bandeja
**Prioridad:** P1. **Diagnóstico verificable:** La celda 20 carga datos SECOP en pandas, no reconecta Atlas; la 35 demuestra Astra, no exporta bandeja. Mezcla de alcance con S05.

**Inventario:** 303 palabras breves nuevas; 4197 palabras markdown brutas, 39 celdas y 21 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Cliente-servidor, DNS/TLS, autenticación, persistencia, replicación y partición, vista y ausencia de dato. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Línea de tiempo de réplica, diagrama de cliente y clúster, tabla de null/ausente/cero; no presentar simulación como failover. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Separar preflight, carga idempotente, consultas, vista, reconexión y exportación en bloques reales; verificar relectura con un cliente nuevo; mover demostración extensa de Cassandra a la ruta correspondiente sin borrar contenido histórico. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Cambiar regla de bandeja, recuperar mismo estado tras reconexión y explicar qué garantía no se probó. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Bandeja, criterios y patrones de acceso para S05.

**Tiempo propuesto:** apertura 5 min; fundamentos 25; ejemplo/experimentación 25; pausa 10; práctica 60; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Cuenta y permisos previamente probados; sin URI pública ni prueba destructiva.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S05 · Cassandra y query-first
**Prioridad:** P1. **Diagnóstico verificable:** Existe buen desarrollo de query-first; las celdas 45, 49 y 65 empiezan con separadores y la 59 no se titula medición de concentración. Falta demostrar dos patrones completos.

**Inventario:** 296 palabras breves nuevas; 7986 palabras markdown brutas, 82 celdas y 26 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Partición, clustering, CQL, desnormalización, distribución lógica, consistencia y escrituras. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Cajones por clave, orden por fecha, histograma de tamaños y cambio de bucket; explicar que worker, nodo y partición son distintos. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Construir dos tablas reales bajo permisos y cuota; contrastar CQL con pandas, calcular distribución por clave, repetir upsert y exportar resultados; validar identidad en ambas. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Diseñar clave para consulta nueva con intervalo y contrastar IDs y tamaño máximo. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Catálogo de consultas y claves; identidad y relaciones verificadas para S06.

**Tiempo propuesto:** apertura 5 min; fundamentos 30; ejemplo/experimentación 25; pausa 10; práctica 55; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** No usar ALLOW FILTERING como solución universal; no certificar Astra con pandas.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S06 · Neo4j y grafos
**Prioridad:** P1. **Diagnóstico verificable:** El cuaderno tiene un recorrido zero-to-hero valioso. La medición apunta a consulta de conectividad (59); la exportación a ficha con respuestas modelo (100).

**Inventario:** 304 palabras breves nuevas; 10224 palabras markdown brutas, 119 celdas y 40 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Identidad, dirección, relaciones, caminos, grado, DISTINCT, MERGE, restricciones e integridad referencial. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Grafo manipulable con resaltado de caminos, tabla de aristas y comparación de nodos/caminos. Evitar vínculos inferidos solo por nombre. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Mantener carga real y consultas Cypher; añadir control independiente por tablas de aristas, consulta a uno/dos saltos, reejecución de MERGE y exportación con procedencia. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Elegir nodo y profundidad no resueltos; comparar conjuntos de IDs y explicar duplicación de caminos. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Subgrafo de contexto y documentos textuales para S07.

**Tiempo propuesto:** apertura 5 min; fundamentos 25; ejemplo/experimentación 30; pausa 10; práctica 55; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Confirmar Aura, permisos y datos; no inferir fraude por centralidad.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S07 · BM25 y Elasticsearch
**Prioridad:** P1. **Diagnóstico verificable:** Presentación especializada debe conservarse. Celda 19 es ingesta bulk, no análisis; 23 es multi_match/filter/highlight, no explain. El control nuevo solo aísla TF.

**Inventario:** 308 palabras breves nuevas; 2705 palabras markdown brutas, 31 celdas y 12 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Analizador, postings, TF/DF/IDF, BM25 completo, normalización, DSL, juicios y métricas. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Construir índice invertido visual; controles de k1, b, longitud, frecuencia e IDF; mostrar contribución por término y cambios en ranking. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Añadir _analyze y _explain reales, mapping, corpus fijo, al menos un conjunto de consultas y juicios independientes; medir P@k y recall con denominador explícito. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Cambiar término y filtro, anticipar ranking y evaluar contra juicios congelados; encontrar un falso positivo. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Corpus, ranking lexical, consultas y juicios congelados para S09.

**Tiempo propuesto:** apertura 5 min; fundamentos 30; ejemplo/experimentación 30; pausa 10; práctica 50; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Usar índice aislado y credenciales seguras; no presentar puntajes como probabilidades.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S08 · Taller de control 1
**Prioridad:** P1. **Diagnóstico verificable:** El cuaderno evaluativo tiene seis etapas y pesos. Las pantallas documental/operacional/relacional apuntan a secciones anteriores equivocadas (7/29/51).

**Inventario:** 292 palabras breves nuevas; 11227 palabras markdown brutas, 81 celdas y 31 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Repaso formativo de identidad, cobertura, concurrencia, modelos y calidad; sin resolver los seis productos evaluados. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Usar casos de biblioteca distintos al taller, mapa de dependencias, estaciones de trabajo, checklist y clínica de fallos. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Corregir enlaces E1–E6 y conservar íntegramente enunciado, pesos y soluciones no públicas; preflight de tres motores, controles de entrega y recuperación de entorno. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Cada equipo demuestra sus evidencias según la rúbrica vigente; retroalimentación sobre proceso, no respuesta evaluada. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** V1 y manifiesto individual según modalidad oficial.

**Tiempo propuesto:** apertura 5 min; fundamentos 15; ejemplo/experimentación 15; pausa 10; práctica 75; autonomía/transferencia 20; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Dar prioridad al trabajo autónomo; no introducir nuevas tareas calificables.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S09 · Búsqueda semántica y vectorial
**Prioridad:** P1. **Diagnóstico verificable:** S09 es referente interno de interacción; reemplazarla por una frase y coseno unidimensional perdería calidad. Celda 10 crea índice, no consulta ANN; 13 consulta, no demuestra fusión completa por sí sola.

**Inventario:** 295 palabras breves nuevas; 3435 palabras markdown brutas, 21 celdas y 11 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Producto punto, norma, coseno, representación aprendida, prefijos E5, ANN/ENN, filtros, RRF, latencia y evaluación. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Retener explorador original; agregar vectores 2D, contribuciones de RRF, curvas recall-latencia y comparación de ranking por consulta. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Fijar modelo, dimensión, prefijos, corpus y juicios; prueba exacta y aproximada real si Atlas lo admite, filtros, fusión y exportación. Verificar cuota antes de crear índices. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Consulta no vista: compara lexical/vectorial/híbrida con juicios y explica error de recuperación. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Contrato de vectores y benchmark reutilizable por multimedia.

**Tiempo propuesto:** apertura 5 min; fundamentos 30; ejemplo/experimentación 30; pausa 10; práctica 50; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Usar lote pequeño, cache etiquetada y evitar crear índices innecesarios.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S10 · Imágenes y audio
**Prioridad:** P1. **Diagnóstico verificable:** La ruta nueva reduce la riqueza del material multimedia existente; celda 22 es inventario de voces, no cálculo de características. El control RGB solo cubre tamaño.

**Inventario:** 314 palabras breves nuevas; 4946 palabras markdown brutas, 48 celdas y 23 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Píxeles, canales, resolución, histograma, interpolación, contenedor/códec, muestreo, RMS, FFT, espectrograma, centroide, MFCC, formatos y threads. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Mostrar originales y derivados, histogramas comparables, formas de onda y espectrogramas con ejes y ventanas; controles de resolución y frecuencia. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Preservar al menos diez audios reales autorizados y catálogo de imágenes existente; inspeccionar metadatos reales, transformar copia, medir features y throughput secuencial/concurrente con mismo lote; exportar Parquet/JSONL y créditos. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Elegir transformación según legibilidad o señal, medir antes/después y explicar pérdida de información. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Catálogo RAW/derivados, hashes y fuentes para S11.

**Tiempo propuesto:** apertura 5 min; fundamentos 30; ejemplo/experimentación 30; pausa 10; práctica 50; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Usar archivos preparados y subconjunto de clase; ampliación sobre corpus completo con presupuesto.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S11 · OCR, ASR y recuperación
**Prioridad:** P0. **Diagnóstico verificable:** Cuaderno existente tiene 122 fuentes y dos fases; nuevos enlaces no prueban audio largo, embeddings o visor. Hay retroceso de ASR celda 28 a embeddings celda 22 y de búsqueda 64 a catálogo 60.

**Inventario:** 313 palabras breves nuevas; 5490 palabras markdown brutas, 73 celdas y 31 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** OCR y PSM, PDF nativo/escaneado, CER, ASR y WER, segmentación con offsets, códec, embeddings y trazabilidad. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Visor página/texto, recorte, PSM y CER; reproductor con segmentos, cobertura temporal; búsqueda por modalidad con apertura de evidencia. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Codespace autónomo sin video; verificar ≥30 imágenes por tipo y ≥10 audios cuando corresponda al corpus autorizado, audio largo real y su formato, cobertura de segmentos, embeddings de OCR/ASR/texto y representación visual explícita. No confundir embedding textual con visual. Medir threads sobre igual lote y exportar catálogo. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Consulta nueva con resultados vinculados a página/intervalo e interpretación de CER/WER; documentar activo fallido sin inventar texto. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Investigador multimedia con fuentes, métricas, modalidad, modelo y estado para TC2.

**Tiempo propuesto:** apertura 5 min; fundamentos 25; ejemplo/experimentación 25; pausa 10; práctica 60; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Preinstalar dependencias y pesos autorizados; separar muestra mínima y lote extendido; prueba limpia de Codespaces.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S12 · Taller de control 2
**Prioridad:** P1. **Diagnóstico verificable:** Cuaderno con seis desafíos y 24 controles; referencia de recuperación vuelve de E6 a E3, y la de entrega apunta a defensa. La ruta no debe sustituir orden del enunciado.

**Inventario:** 258 palabras breves nuevas; 10088 palabras markdown brutas, 111 celdas y 45 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Repaso de recuperación, relevancia, fusión, OCR, ASR, WER, ETL y evidencia según evaluación oficial. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Ejemplos no evaluativos, checklist por desafío, estado de activos y clínica de errores; no publicar respuestas. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Conservar E1–E6 y pesos, corregir navegación y preparar preflight de fuentes y motores; reservar trabajo individual; revisar contratos y relectura de entregables según rúbrica. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Estudiante verifica y corrige una discrepancia en su entrega; evaluación únicamente con rúbrica vigente. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** V2, evidencias individuales y estado de integración.

**Tiempo propuesto:** apertura 5 min; fundamentos 15; ejemplo/experimentación 15; pausa 10; práctica 75; autonomía/transferencia 20; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** No exigir tecnologías de S13/S14; no alterar las fechas ni requisitos de un taller ya anunciado.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S13 · HDFS, MapReduce y Dask
**Prioridad:** P0. **Diagnóstico verificable:** El material de ocho lotes y K-means debe conservarse. La ruta nueva no aporta clasificador/regresor entrenable sobre particiones; la celda 51 es transferencia, no prueba de exportación.

**Inventario:** 320 palabras breves nuevas; 3250 palabras markdown brutas, 55 celdas y 22 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** HDFS, MapReduce, CPU/hilos/workers, particiones, lazy, scheduler, shuffle, skew, escalamiento y ML distribuido. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Diagramas de bloques/réplicas, DAG y Gantt de tareas; Amdahl con supuestos; tablas de workers y métricas reales, no análisis del equipo personal del alumno. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Mantener ocho lotes SECOP y pruebas escalonadas 1k/10k/20k/50k u otras escalas seguras; comprobar equivalencia pandas, workers efectivos, tiempo y método de memoria; conservar K-means y añadir regresión/clasificador realmente compatible con Dask o entrenamiento incremental explícitamente identificado. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Cambiar particiones/workers y evaluar exactitud y costo; modificar modelo o configuración sin materializar matriz completa; registrar split. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Resultados y métricas con configuración y esquema comparables para Spark.

**Tiempo propuesto:** apertura 5 min; fundamentos 25; ejemplo/experimentación 25; pausa 10; práctica 65; autonomía/transferencia 10; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Codespace especializado; límites de cuota, datos abundantes sin descarga innecesaria, benchmark pesado manual.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S14 · Spark, Databricks y Delta
**Prioridad:** P0. **Diagnóstico verificable:** Cuaderno tiene joins P1–P4, planes, medallion y MLlib. La celda 70 es hoja de consulta, no evidencia de persistencia. No se verificó compatibilidad remota.

**Inventario:** 289 palabras breves nuevas; 9015 palabras markdown brutas, 71 celdas y 23 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Driver/executor, DAG, jobs/stages/tasks, planes, shuffle, join, broadcast, skew, Delta, medallion, SQL y MLlib. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Visualizar plan lógico/físico y tabla P1–P4; resaltar P4 nulo, Exchange y BroadcastHashJoin observados si existen; representar versiones Delta. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Reutilizar operaciones Dask sobre mismo universo; comprobar exceptAll en ambas direcciones, operadores reales, persistencia e historial cuando se soporte; fit MLlib sin collect masivo y evaluación test. Distinguir Databricks de Colab Spark local. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Modificar clave o hint y comparar plan, equivalencia y costo; interpretar métricas del modelo propio. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Gold, predicciones, planes, configuración y métricas para S15/S16.

**Tiempo propuesto:** apertura 5 min; fundamentos 25; ejemplo/experimentación 25; pausa 10; práctica 65; autonomía/transferencia 10; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Verificar APIs y permisos de Free Edition; no declarar garantías de hint ni compatibilidad universal.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S14A · Laboratorio opcional de escala
**Prioridad:** P0. **Diagnóstico verificable:** La ruta del cuaderno está bien ordenada por A0–A7, pero no hay evidencia persistida de fit a escala. Estimar 19 GiB no prueba entrenamiento.

**Inventario:** 293 palabras breves nuevas; 2386 palabras markdown brutas, 28 celdas y 9 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Generación distribuida, N×D×bytes, split, fuga, features, modelos, métricas, persistencia y escalamiento controlado. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Control de N y D con unidades; pipeline de estados; comparar límite inferior, tamaño efectivo y mediciones; matriz de confusión. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Preflight remoto y fit mínimo antes de aumentar N; generar por range sin listas gigantes, validar filas reales de train y 128 features, ejecutar dos modelos compatibles si se admite, guardar predicciones y métricas, relectura del producto. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Elegir escala siguiente o parada segura según cuota y evidencia; justificar si supera presupuesto local explícito sin forzar OOM. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Expediente sintético separado con N, D, modo, fit, tiempo, evaluación y límites.

**Tiempo propuesto:** apertura 5 min; fundamentos 20; ejemplo/experimentación 20; pausa 10; práctica 75; autonomía/transferencia 10; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Voluntario, sin nota; escalas grandes solo manuales y si la plataforma lo permite.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S15 · Pipelines confiables
**Prioridad:** P0. **Diagnóstico verificable:** Es el cuaderno más corto; el nuevo enlace de exportación (16) corresponde a ampliación de streaming, no observabilidad. Riesgo de tratar simulación como garantía de producción.

**Inventario:** 266 palabras breves nuevas; 864 palabras markdown brutas, 19 celdas y 6 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Idempotencia, offsets, checkpoints, versiones, esquema, cuarentena, tardanza, microbatch y observabilidad. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Diagrama de estados y eventos fuera de orden; controles de fallo y reintento; línea temporal de checkpoints y tabla de reconciliación. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Añadir lote base reproducible, fallo entre persistencia y checkpoint, recuperación, eventos tardíos y cambio de esquema, comparación con ejecución limpia, logs y exportación. Streaming Spark como ruta explícita opcional si soportada. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Cambiar momento de fallo y comprobar estado final idéntico, ausencia de duplicados y trazas. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** Manifiesto de actualización y estado versionado para integración.

**Tiempo propuesto:** apertura 5 min; fundamentos 25; ejemplo/experimentación 25; pausa 10; práctica 60; autonomía/transferencia 15; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** S15 sigue formativa; no atribuir exactly-once universal ni modificar criterios académicos.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## S16 · Proyecto y defensa
**Prioridad:** P0. **Diagnóstico verificable:** El cuaderno E0–E7 está orientado a Dask/Spark y producto. La pantalla de consulta apunta a Dask (12), recuperación a producto (28). No se deben convertir competencias de todo el curso en nuevos requisitos del proyecto.

**Inventario:** 265 palabras breves nuevas; 3534 palabras markdown brutas, 34 celdas y 16 de código. Sin salidas persistidas en archivo inspeccionado. No se certifica ejecución ni suficiencia de extensión.

**Objetivos de enseñanza y mecanismos:** Contratos, identidad, evaluación ML, linaje, integración, evidencia y defensa; alcance según rúbrica vigente. Formular objetivos con verbo observable y evidencia; definir terminología desde cero y vincular cada mecanismo a la pregunta de Compras Claras.

**Rediseño visual y práctica activa:** Mapa E0–E7 con estados y dependencias; recorrido de usuario, predicción y fuente, checklist de evaluación vigente. Incluir predicción antes de mostrar resultado, explicación del cambio y un contraejemplo. Integrar ejemplos resueltos y lecturas profundas en la presentación; no convertirla en lista de instrucciones.

**Laboratorio E2E (modificación concreta):** Ejecutar el producto desde entorno limpio con artefactos propios, verificar split y equivalencia Dask/Spark cuando sean requeridos, predicciones Delta cuando corresponda, acceso del docente y defensa. Mantener módulos adicionales como extensión no calificable. Identificar secciones por encabezado y cell ID estable cuando exista; no basarse exclusivamente en posición numérica. Para cada operación enseñar entrada, parámetros, código visible, salida real, comprobación y recuperación. Las ampliaciones de talleres respetan rúbrica y no revelan solución.

**Evaluación formativa y transferencia:** Demostración auténtica y justificación de un límite con evidencia, según modalidad oficial. Evidencia observable y retroalimentación específica; no agregar nota ni criterio de evaluación académica sin aprobación. **Producto:** V3 y manifiesto de artefactos; no declarar sistema de producción.

**Tiempo propuesto:** apertura 5 min; fundamentos 15; ejemplo/experimentación 20; pausa 10; práctica 50; autonomía/transferencia 40; cierre 10. Total 150 min. Ensayar preflight, primer resultado, transición y producto final. Si no cabe, reducir administración o mover ampliación a consulta, no sacrificar objetivo esencial.

**Riesgo/contingencia:** Distribución de defensa provisional: recalcular según cantidad real de equipos y modalidad oficial.

**Puerta específica:** confirmar en entorno apropiado el laboratorio descrito, el reto autónomo y el artefacto; conservar trazas, procedencia, versión y modo. Comprobar que la presentación original valiosa no fue degradada; verificar anclas y dos recursos. Acreditar individualmente 40.000 palabras elegibles, 25 diapositivas sustantivas y todas las puertas generales. Estado: pendiente de reconstrucción y aceptación.

## Plan de implementación y control de cambios
1. Congelar inventario y resolver referencias equivocadas con identificadores estables; el destino debe enseñar la actividad, no solo existir. Crear matriz objetivo–pantalla–sección–resultado–evaluación para las 17 sesiones.
2. Reconstruir S01 como estándar de contenido (no como nueva plantilla escueta). En paralelo priorizar P0 S11, S13, S14, S14A, S15 y S16 por complejidad, alcance técnico y defensa. Luego S02–S07 y S09; S10 junto a S11; S08/S12 con integridad de evaluación. Mantener S14A opcional y S15 formativa.
3. Cada sesión se desarrolla por unidades temáticas con revisión de originalidad; reservar tiempo de edición sustantiva y verificación de ejemplos, no fabricar palabras. Evitar duplicar texto entre HTML y notebook; el texto proyectado no es el total de la lectura.
4. Integrar experimentos de navegador con parámetros calculados, representación causal, tablas antes/después y explicaciones. Como propuesta de calidad, por sesión docente: ≥4 ejemplos resueltos, ≥4 controles o simuladores significativos (no solo revelar respuesta fija), ≥3 modificaciones guiadas, un reto autónomo y una salida formativa vinculada a objetivos. En talleres y defensa sustituir por casos no evaluativos y controles de evidencia; no aumentar obligaciones.
5. Probar notebook desde entorno limpio con datos congelados autorizados y ruta real de plataforma. Registrar tiempo, errores, estado, configuración, resultados y relectura. No guardar secretos ni datos de estudiantes. No afirmar ejecución externa por una simulación. No ejecutar benchmarks pesados en GitHub Actions; pruebas pequeñas y pertinentes, escalas grandes manuales y justificadas.
6. Proyección 1366×768 y 1920×1080, móvil 360×800, navegación por teclado, foco, contraste, gráficos con unidades y fuente, lectura ampliada sin recorte. Verificar que las pantallas de cálculo y casos no se apilen con scroll obligatorio en proyección; la lectura extensa sí admite scroll. Revisar visuales reales, no repetir diagrama Entrada→Misión→Evidencia en todas las pantallas.
7. Ensayar 150 minutos con docente y, cuando sea viable, un lector no familiarizado con el código. Medir tiempo de exposición, actividad, entorno, errores y cierre. Registrar evidencia observada, no asignar minutos uniformes para sumar. En evaluación, preservar formato y tiempos oficiales.
8. Medir aprendizaje con diagnóstico y salida equivalentes, desempeño en modificación autónoma, interpretación de evidencia y transferencia. Reportar N y denominadores, casos no completados, mediana de tiempo y diferencia entre desempeño con guía y sin ella. Umbrales propuestos para evaluación de material, no notas nuevas: ≥80% de participantes de una prueba piloto pueden completar producto mínimo y ≥70% resolver variante autónoma; con grupos pequeños reportar números absolutos y no inferir causalidad. Sin piloto, aprendizaje no medido. La revisión técnica no sustituye evaluación pedagógica.
9. Registrar por sesión extensión elegible, fuente y hash, pantallas, objetivos, resultados de ejecución, revisión visual, ensayo, rúbrica y bloqueos. Puertas críticas: extensión, profundidad y ausencia de relleno, alineación, práctica real o contingencia explícita, salida interpretable, autonomía, proyección y tiempo. Si una falla, no aceptar aunque promedio alto.
10. Reutilizar rama existente; no publicar ni fusionar a main hasta aprobación. Conservar rúbricas, fechas, cuadernos y ramas especializadas; no crear ramas adicionales sin necesidad. Esta auditoría no ejecuta la reconstrucción y no certifica ninguna sesión.
