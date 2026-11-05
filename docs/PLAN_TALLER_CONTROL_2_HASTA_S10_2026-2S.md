# TC2 · Plan editorial y técnico de publicación (S01–S10)
Universidad Central · Maestría en Analítica de Datos · Big Data 2026-2S

**Estado: PROPUESTA PARA REVISIÓN.** Este documento no es un taller publicado, no modifica el calendario ni abre entregas. Fecha de inicio y vencimiento pendientes de definir. No afirmar que cumple el PDA 2026: el único PDA comprobado en el repositorio corresponde a 2023-I. Su segundo taller tenía un temario distinto; la equivalencia académica y el peso del 25 % requieren confirmación docente/institucional.

## 1. Auditoría de referencia: Taller de Control 1, versión V9

Fuentes inspeccionadas: Cuadernos/Taller_Control_1.ipynb; utils/tc1_contrato.py; utils/validate_tc1_v9.py; assets/tutoriales/s08-secoppipeline.html; lms/session-08.html; AGENTS.md; docs/PDA_guia.md.

- TC1 tiene **81 celdas, 6 etapas y 22 controles que suman 100 puntos**. E1 adquisición/concurrencia 25; E2 MongoDB/documentos 25; E3 producto analítico 10; E4 Cassandra 15; E5 Neo4j 15; E6 decisiones/entrega 10. Es grupal o individual.
- Su mayor acierto es el hilo de Laura: el mismo RAW se reutiliza, cada etapa explica qué hace el estudiante, qué está provisto, checkpoint y evidencia, qué no se puede concluir, y la puntuación se recalcula desde archivos.
- Mantener el patrón de seis etapas, el enunciado único, la rúbrica anticipada, los cuatro rótulos interpretativos, las acciones EJECUTA/ELIGE/COMPLETA/ESCRIBE/PEGA, la identificación por equipo, una actividad propia y el manifest sellado.
- Reducir fricción: TC1 requiere Colab, Atlas, Astra y Aura, además de Drive y correo. TC2 no debe exigir tres servicios externos ni repetir NoSQL básico, concurrencia y consultas Cypher/CQL.
- TC1 pone Drive restringido + correo como entrega oficial; session-08.html mantiene código de formulario oculto y su backend rechaza manifiestos TC1. No crear una segunda ruta que prometa calificación oficial sin verificarla.
- Las capturas son controles de respaldo: mejor priorizar resultados recalculables. El fallo de una etapa no debe impedir calificar las siguientes; usar un artefacto de referencia etiquetado y descontar solo la etapa no superada.
- Calificación histórica TC1: puntaje 0–100; con entrega, nota = 1 + 4 × puntaje/100, redondeada a una décima; sin entrega, 0,0. Para TC2 conservar únicamente tras verificar regla institucional vigente.
- **Seguridad independiente del TC2:** docs/PENDIENTES.md señala posibles credenciales históricas de MongoDB en 8_NoSQL_Mongo.ipynb. Resolver rotación/revocación antes de habilitar nuevas prácticas y no repetir reglas 0.0.0.0/0 sobre servicios compartidos.

## 2. Enunciado propuesto para estudiantes

### TC2 · Compras Claras 2: del documento a la evidencia multimodal

Laura ya cuenta con un conjunto de procesos públicos organizado. Necesita recuperar procesos aunque la consulta no repita sus palabras, comparar la recuperación léxica con la semántica y crear un catálogo verificable de imágenes y audios. No busca demostrar irregularidades ni atribuir un audio o una imagen a un contrato sin evidencia de origen.

**Objetivo:** sobre un corpus reproducible, construir y comparar dos rankings (BM25 y embeddings E5), obtener un ranking híbrido con RRF y ejecutar un ETL de imágenes/audio que conserve originales, derivados, procedencia e integridad. Al cierre, elegir una estrategia para una consulta del equipo y declarar un límite con un dato específico faltante.

**Alcance:** sesiones 1–10 únicamente. No exigir Spark, Dask distribuido, Airflow, Kafka, MapReduce ejecutado, OCR productivo, Whisper/ASR obligatorio ni APIs de pago. La recuperación semántica sí utiliza el modelo intfloat/multilingual-e5-small (384 dimensiones), aprendido en S09.

**Modalidad:** parejas, con opción individual idéntica a TC1. No se penaliza a quienes no participaron exitosamente en TC1: el corpus y las entradas del TC2 se restauran sin necesitar la carpeta previa del taller 1. **Recursos visibles:** (1) cuaderno TC2 en Colab y (2) checklist web con el mapa de pasos y fallos. Los laboratorios S07/S09/S10 pueden enlazarse como referencias sin agregarse como recursos obligatorios. La presentación no ejecuta Python.

### Caso y fuentes sin mezclas falsas

1. **Corpus textual:** derivar un lote fijo, verificable y de hasta 120 documentos SECOP de Datos/s06_contexto_relacional.csv con las mismas columnas de S09: id_proceso, nombre_proceso, descripcion, entidad, url_secop. Antes de fijar el lote hay que validar IDs únicos, cobertura temática, longitud de textos y enlaces. Guardar manifest con versión, fecha de corte y SHA-256. No declarar aleatoriedad representativa: la muestra S09 tiene selección didáctica.
2. **Consultas evaluables:** crear un banco de al menos 12 consultas en español, con dos asignadas determinísticamente a cada equipo y juicios de relevancia por id_proceso (qrels). Etiquetarlas manualmente contra el lote definitivo ANTES de publicar. Probar que cada consulta tiene suficientes positivos y negativos para comparar Precision@5 y Recall@5, sin usar scores como verdad de relevancia. Registrar la versión del banco; cambios de la fuente invalidan los qrels.
3. **Multimedia:** imágenes de demostración del curso o archivo propio cuyo uso esté permitido; diez WAV humanos reales de PolyAI/MINDS14 es-ES, CC BY 4.0, con fuente, licencia, hash y referencia; incluir un respaldo licenciado para caída de red verificado con hashes. Las voces son consultas financieras, **no audios periodísticos de El Tiempo**. El inventario editorial de 32 imágenes/24 noticias solo puede usarse con atribución y derechos verificados; no inferir asociación con SECOP ni redistribuir binarios sin permiso.
4. Se permiten archivos propios autorizados como extensión, pero la rúbrica básica debe poder aprobarse usando el paquete de referencia. Para evitar confusión, campos source_kind, source_record_id, source_license, source_sha256, article_id opcional y relacion_verificada deben explicar exactamente qué se conoce.

## 3. Recorrido del estudiante

**Preparación, sin nota.** Colab: crear copia, inicializar alias de equipo (sin nombres o correos en artefactos públicos), obtener entradas oficiales con SHA-256, recuperar avance y ejecutar autodiagnóstico CPU/memoria/red. La descarga del modelo y el acceso a Atlas se prevalidan; hay ruta local de recuperación. No solicitar contraseña docente.

**E1 · Corpus y contrato (10 puntos).** Identificar unidad documental, verificar IDs únicos, construir texto de búsqueda y conservar snapshot firmado. Confirmar que la misma consulta usa la misma población en BM25 y E5. Evidencia: E1/corpus.parquet, E1/data_contract.json, E1/query_assignment.json y E1/qrels_version.json.

**E2 · Recuperación léxica BM25 (20 puntos).** Trabajar con una implementación BM25 provista o dependencias fijadas, inspeccionar tokenización y dos consultas asignadas, construir ranking Top-10 con desempate por ID y comparar efecto de un filtro real por entidad. El estudiante completa una decisión pequeña observable, no copia íntegra del motor. Exportar IDs, rangos, score, filtro y huella del corpus. Evidencia: E2/bm25_rankings.json y E2/bm25_experimento.json. Elastic Cloud no es obligatorio; sigue disponible como enlace de referencia de S07.

**E3 · Recuperación semántica y base vectorial (20 puntos).** Ejecutar E5 multilingual-e5-small con passage: y query:, guardar N × 384 float32 y demostrar coseno exacto en NumPy. Declarar claramente si hubo ping, upsert, índice queryable y consulta $vectorSearch REAL en Atlas; guardar resultados remotos por separado. La ruta Atlas Ephemeral Free es opcional en caso de indisponibilidad real; el validador nunca transforma NumPy en una pretendida ejecución Atlas. E3.4 da crédito íntegro por Atlas real o por contingencia de proveedor comprobada automáticamente y una alternativa local equivalente; una ruta local escogida sin contingencia puede obtener crédito parcial. Evidencia: E3/embeddings_meta.json, E3/sem_rankings.json, E3/vector_status.json, E3/atlas_evidencia.json cuando aplique. No exponer conexión ni enlace privado de reclamo.

**E4 · Evaluación y búsqueda híbrida (15 puntos).** Evaluar BM25 y E5 con juicios externos curados, no con su propia puntuación. Calcular Precision@5 y Recall@5 con denominadores correctos, contar falsos positivos y recuperar IDs. Implementar/completar RRF con constante k=60, comparar Top-5 lexical, semántico e híbrido y conservar desempate estable. Elegir un ranking con una decisión cerrada, valor numérico propio, alternativa descartada y límite concreto. Evidencia: E4/evaluacion.json, E4/rrf_ranking.json y E4/decision_ranking.json.

**E5 · ETL multimodal (25 puntos).** Reutilizar el contrato S10: E extraer bytes autorizados y registrar procedencia; T conservar RAW inmutable, producir dos perfiles de imagen (lado y luminancia/histograma) y calcular duración/RMS/ZCR/centroide/ventana FFT sobre diez WAV reales; L escribir JSONL y Parquet, releer y verificar equivalencia. Elegir parámetros propios entre opciones válidas, contrastar el efecto en el resultado y detectar un derivado intencionalmente alterado SIN modificar el RAW. Verificar idempotencia al reejecutar. El número de filas se calcula a partir de los archivos, no se fuerza a 13 si hay activos extra. La herramienta web reactiva de S10 puede exportar un ZIP s10-asset-v2 e importarse en Colab, pero no debe crear un tercer recurso obligatorio. Evidencia: E5/raw/, E5/derived/, E5/assets.jsonl, E5/assets.parquet, E5/manifest_assets.json y E5/quality_gates.json.

**E6 · Defensa estructurada y entrega (10 puntos).** Generar reporte con dos decisiones ancladas a resultados propios: (a) estrategia de ranking para una consulta con métrica y limitación; (b) perfil multimedia elegido con sus tamaños, hashes y lo que un histograma/espectro NO permite concluir. Seleccionar alternativas y límites mediante opciones contextualizadas, IDs y números, no texto libre. Validar paquete desde archivos, sin confiar en estado del notebook, generar manifest y sello SHA-256.

## 4. Rúbrica de 22 controles, 100 puntos

| Control | Evidencia observable | Puntos | Verificación |
|---|---|---:|---|
| E1.1 | Fuente, campos, versión, hash y procedencia verificables | 4 | automática |
| E1.2 | IDs únicos, limpieza y grano correctos | 3 | automática |
| E1.3 | Dos consultas del equipo y qrels del mismo lote | 3 | automática |
| E2.1 | BM25 sobre el corpus firmado; tokenización y configuración reproducibles | 6 | automática |
| E2.2 | Dos rankings Top-10 con consulta/IDs/scores correctos | 5 | automática |
| E2.3 | Filtro y desempate estables, consecuencia observada | 5 | automática |
| E2.4 | Exportación reabierta y enlaces/identidad preservados | 4 | automática |
| E3.1 | E5 real, prefijos correctos, vectores finitos y N × 384 | 6 | automática |
| E3.2 | Top-k local por coseno consistente con referencia exacta | 5 | automática |
| E3.3 | Persistencia/upsert reproducible, sin duplicación | 5 | automática |
| E3.4 | Estado de Atlas honesto y consulta real o contingencia comprobada | 4 | automática + contingencia |
| E4.1 | Precision@5 y Recall@5 correctamente calculados con qrels | 6 | automática |
| E4.2 | Fusión RRF (k=60), IDs y ranking híbrido correctos | 5 | automática |
| E4.3 | Elección, alternativa y limitación vinculadas a IDs/métricas propias | 4 | automática |
| E5.1 | Fuentes, licencias, diez audios y originales con hashes | 5 | automática |
| E5.2 | Imagen RAW intacta, dos perfiles y comparación de resultados | 6 | automática |
| E5.3 | Métricas de diez WAV y experimento real de audio | 4 | automática |
| E5.4 | Catálogo JSONL/Parquet y manifiesto coinciden tras relectura | 6 | automática |
| E5.5 | Reejecución idempotente y corrupción detectada | 4 | automática |
| E6.1 | Dos decisiones sustentadas por resultados individuales | 4 | automática |
| E6.2 | Microdefensa estructurada con limitación específica | 3 | automática |
| E6.3 | ZIP/manifest íntegros, sin secretos y con hash final | 3 | automática |
| **Total** | **22 controles** | **100** | |

Cada ítem se califica independientemente con 0 o puntos definidos (o subniveles explícitos si hay evidencia parcial documentada). La interfaz muestra antes de empezar cómo obtener todos los puntos. Las etapas no se califican por velocidad o por pagar servicios. Captura no equivale a ejecución. El manifiesto contiene por ítem: id, máximos, obtenidos, evidencia, resultado, motivo del fallo y sugerencia concreta.

## 5. Reglas de evaluación y honestidad

- Conservar propuesta de conversión TC1 (1 + 4 × puntos/100, un decimal; sin entrega 0) solo tras verificar la norma vigente. 25 % del componente TC2, si se confirma PDA actual.
- Evidencia del trabajo grupal con identidad restringida. No publicar nombres, códigos, cuentas, notas, llaves ni enlaces privados.
- Toda consulta tiene fuente y hash; cada ranking usa el mismo universo para hacer comparaciones válidas. El modelo de embeddings y la normalización no pueden cambiar entre documentos y consultas de forma oculta.
- Precision@k usa juicios de relevancia, nunca similitud ANN–ENN. Solapamiento de vecinos no equivale a relevancia.
- No usar tamaño de muestra de 120 para afirmar escalabilidad, ni un solo tiempo para declarar que un motor es más rápido. No concluir irregularidades de SECOP, ni emoción/semántica de un espectro, ni contenido de una foto de su histograma.
- Si un servicio falla, registrar estado verificable: NO EJECUTADO; el tutor ofrece diagnóstico, artefacto etiquetado para continuar y crédito parcial/contingencia según el control.
- Cada bloque tiene los cuatro rótulos: Cómo se lee; Qué nos dice; Qué NO permite concluir todavía; Qué error común.
- Cada bloque exige 1 decisión visible del estudiante; un botón de ejecutar todo, sin variación propia, no produce nota completa.
- Nada de respuestas académicas abiertas; sí se admite código, consultas, parámetros, archivos y controles cerrados, según AGENTS.md.

## 6. Diseño de los dos recursos de estudiante

1. **Cuadernos/Taller_Control_2.ipynb**, generado exclusivamente desde utils/build_taller_control_2.py: portada, objetivo y rúbrica completa, tabla de E1–E6, glosario contextual, preparación, fichas de etapa, celdas con verbos claros y una acción propia cada una, checkpoints, diagnóstico, interpretación, salida esperada, recuperación, hoja de trucos, cierre y entrega. Meta editorial: 35–50 celdas y un hilo corto; no perder definiciones por recortar.
2. **assets/tutoriales/tc2-paso-a-paso.html**, checklist mobile/desktop con evidencia concreta por paso, estados guardados localmente SOLO como comodidad y vínculo a celdas Colab. No recoger texto abierto ni afirmar progreso académico por marcar casillas.

El ETL reactivo S10 ya publicado se enlaza dentro de estos materiales como extensión integrada opcional y conserva su contrato s10-asset-v2. No duplicar la herramienta ni registrar un tercer recurso evaluable.

## 7. Entrega propuesta

Una sola entrega por equipo, compatible con la experiencia TC1 mientras no se verifique un canal privado LMS real:

- Carpeta Drive **restringida** accesible al docente, con exactamente TC2_EQUIPO.ipynb, TC2_EQUIPO.zip y manifest_tc2.json.
- Correo institucional con asunto normalizado, enlace restringido y SHA-256 del manifest. El timestamp de ese mensaje fija el cierre. NO declarar recepción LMS/Gradebook; una integración futura exige prueba autenticada de lectura/escritura y registro de nota.
- El ZIP contiene E1–E6, no contiene conexiones, contraseñas, tokens ni archivos privados de otros equipos. Reimportación en un proceso Python limpio debe producir el mismo puntaje (salvo controles con servicio remoto, cuyo estado queda firmado).
- Fecha y hora límite **pendientes de aprobación**; mostrar las mismas en notebook, checklist, portada, LMS y correo. No publicar una fecha inventada.

## 8. QA y puertas de publicación

**P0, seguridad:** resolver credenciales históricas del repositorio; escáner de secretos/PII sin excepciones ocultas; validar entradas ZIP contra traversal/bombas y MIME; nunca guardar URI MongoDB ni claimUrl. Los datasets solo con licencia/procedencia y hashes.

**P1, contratos y datos:** congelar corpus textual, 12 consultas y juicios de relevancia; probar asignación para todos los posibles equipos; comprobar que no haya consultas sin positivos, IDs huérfanos ni sesgo que vuelva trivial la respuesta. Validar fuente de MINDS14 real, ten WAV únicos con referencia, licencia, hash, conversión G.711 a PCM16, y espejo de contingencia.

**P2, corrección técnica:** unit tests BM25, coseno y RRF con ejemplos manuales; resultados ordenados de forma determinista; validación de N × 384 y no NaN; idempotencia en índices, catálogos y ZIP; corrupción de un byte rechazada; segundo ejecutable docente que calcule desde archivos, no desde variables de memoria. Pruebas de contingencia Atlas 429/sin red sin falsificar estado de producción.

**P3, autonomía pedagógica:** ejecución integral en Colab limpio CPU con un equipo de prueba y opciones reales (no solo mocks); reproducir la entrega en ambiente aislado; un estudiante de prueba recorre instrucciones desde cero. Contrastar tiempos de ejecución y bloqueos antes de fijar fecha de entrega. Documentar la salida esperada de cada etapa; no pedir instalar VS Code, pagar un servicio ni configurar credenciales del docente.

**P4, interfaz:** Playwright en móvil y escritorio (390, 768, 1366 px); sin desbordes ni errores JS; navegación por teclado, foco, contraste AA, tema oscuro de Colab y salida legible; pantalla de evaluación no revela respuestas correctas sin ejecución. Un recurso de notebook y un checklist en LMS, sin duplicar tareas.

**P5, control editorial:** ejecutar validadores existentes y nuevos para rúbrica 22/100, preguntas no abiertas, enlaces, secretos, corpus, S07/S09/S10 sin regresiones, y GitHub Pages. PR con CI en verde y evidencia de ejecución real antes de fusionar; prueba pública HTTP después del deploy. En LMS publicar como actividad visible solo cuando se aprueben fecha, porcentaje y canal de entrega.

## 9. Orden de implementación por PR

- PR-A: corpus/conjunto de consultas y relevancia, hash y prueba de licencia.
- PR-B: generador y notebook TC2 E1–E4, validador docente y tests de recuperación.
- PR-C: ETL E5, integración S10, ZIP y manifest.
- PR-D: E6, rúbrica, checklist, pruebas adversariales, accesibilidad y flujo limpio en Colab.
- PR-E: integrar el LMS y publicar después de aprobar PDA, fecha, controles y entrega.

No hacer merge de un plan editorial como si fuera un cuaderno ejecutable. Mantener TC1 y S07–S10 intactos hasta completar pruebas.

## 10. Sesión de lanzamiento de 180 minutos

- 0–15: reconstruir la historia y contraste TC1–TC2.
- 15–40: identidad, corpus, qrels y contrato.
- 40–90: BM25 y variación de consulta/filtro con salidas propias.
- 90–100: receso.
- 100–145: embeddings E5, similitud y Atlas/alternativa.
- 145–165: métricas y RRF con interpretación.
- 165–180: explicar ETL multimedia, checkpoints, entrega y trabajo autónomo.
- La ejecución íntegra de E5, decisiones y validación final continúa fuera del encuentro, con una carga estimativa a verificar en piloto. No tratar seis etapas evaluables como si cupieran completas en 180 minutos.

**Criterio de listo para estudiantes:** un participante nuevo completa sin ayuda P1–P5, reabre su ZIP, obtiene puntaje reproducible, distingue Atlas real de NumPy local y entiende por qué su ranking/histograma no demuestran hechos externos.

---
**Referencias internas:** AGENTS.md; README.md; docs/PDA_guia.md; docs/PENDIENTES.md; lms/data/course.json; Cuadernos/Taller_Control_1.ipynb; utils/validate_tc1_v9.py; Cuadernos/7_Elasticsearch_BM25_Compras_Claras.ipynb; Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb; Cuadernos/10_Imagenes_Audio.ipynb; Datos/s10_audio_reales/README.md; assets/s10/etl-reactivo.html.
