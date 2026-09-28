# Ruta docente S10–S15 · Big Data 2026-2S

## Decisión de secuencia

La ruta no intenta recuperar una sesión perdida acelerando explicaciones. Recupera el tiempo
**eliminando redundancias**: S03–S07 ya cubrieron modelos NoSQL, Cassandra, grafos y búsqueda
lexical con una profundidad que en el PDA antiguo aparecía más tarde.

El hilo vigente queda así:

```text
S01–S02  problema → grano → ingesta → arquitectura
      ↓
S03–S06  representar → servir → operacionalizar → relacionar
      ↓
S07      buscar texto lexicalmente
      ↓
S08      integrar lo aprendido en TC1
      ↓
S09      buscar por significado y combinar rankings
      ↓
S10      convertir texto/archivos en datos trazables
      ↓
S11      escalar el mismo pipeline con cómputo distribuido
      ↓
S12      persistirlo y optimizarlo en un lakehouse
      ↓
S13      orquestarlo como proceso recuperable
      ↓
S14      pasar de batch completo a procesamiento incremental/streaming
      ↓
S15      integrar arquitectura, calidad, observabilidad y serving
      ↓
S16      evaluación/proyecto final
```

## Cómo se recupera la sesión atrasada

No se crea una clase separada para Hadoop/MapReduce/YARN ni otra clase completa solo para Dask.
En **S11** se enseñan los conceptos distribuidos que todavía son necesarios —partición, worker,
scheduler, lazy execution, shuffle, fallo parcial y localidad— y Dask se usa como puente visible
desde pandas. Spark se anticipa al final de S11 y se trabaja de forma completa en S12.

Esto recupera una sesión sin borrar la idea fundamental. El estudiante aprende el modelo mental
y después observa dos implementaciones, en lugar de repetir la misma teoría tres veces.

## Plantilla común S10–S15 · 180 minutos

La estructura se repite para disminuir carga cognitiva y evitar que la clase se sienta acelerada.

| Min | Bloque | Regla |
|---:|---|---|
| 0–15 | Recuperación | 3–5 decisiones cerradas de la sesión anterior; sin preguntas abiertas. |
| 15–50 | Concepto mínimo | Definir todos los términos nuevos, siempre con ejemplo y contraejemplo. |
| 50–95 | Laboratorio guiado | La presentación contiene el laboratorio; el cuaderno ejecuta el caso real. |
| 95–105 | Pausa | 10 minutos. |
| 105–160 | Transferencia | Cambiar una condición del caso; comprobar salidas y errores. |
| 160–175 | Evidencia | Autocomprobación cerrada + artefacto verificable. |
| 175–180 | Puente | Una sola pregunta: qué problema nuevo obliga a la siguiente sesión. |

Reglas de diseño:
- 25–35 diapositivas como objetivo, no 60+.
- Cada término técnico se define antes de usarse.
- Cada mecanismo abstracto necesita gráfico/flujo o ejecución observable.
- El laboratorio está integrado en la presentación y enlaza al cuaderno.
- Las preguntas formativas del estudiante son cerradas; no hay cajas de texto de reflexión.
- La evidencia auténtica sale de la ejecución (conteos, hashes, planes, archivos, métricas).
- Máximo dos recursos visibles por sesión: presentación + cuaderno.
- El mismo caso SECOP/Compras Claras continúa siempre que ayude a comparar mecanismos.

---

# S10 · De texto crudo a datos trazables

**Fecha de trabajo:** 15 de octubre de 2026  
**Problema profesional:** S09 permite recuperar texto por significado, pero ¿cómo se construye
un corpus confiable cuando la fuente llega como HTML, PDF, JSON o texto libre?

### Conceptos
- dato estructurado, semiestructurado y no estructurado;
- extracción vs transformación;
- parser;
- normalización;
- deduplicación;
- chunking como decisión de ETL, no como truco de embeddings;
- metadata/provenance;
- schema-on-read;
- data quality para texto;
- JSONL y Parquet como artefactos intermedios.

### Laboratorio
Una pequeña colección de documentos de contratación/noticias:
1. ingerir 2–3 formatos;
2. conservar fuente y SHA-256;
3. extraer texto;
4. limpiar sin destruir evidencia;
5. detectar duplicados;
6. generar chunks con metadata;
7. escribir un dataset Parquet/JSONL;
8. comprobar conteos antes/después y trazabilidad.

### Evidencia
`manifest_s10.json` con archivos, hashes, filas/documentos, duplicados, chunks y reglas aplicadas.

### Puente
"Ya tengo un pipeline correcto. ¿Qué cambia cuando el volumen deja de caber cómodamente en un
solo proceso?"

---

# S11 · De pandas a cómputo distribuido: particiones, Dask y el costo del shuffle

**Fecha:** 22 de octubre de 2026  
**Sesión que absorbe la pérdida de calendario.**

### Conceptos
- proceso, scheduler y worker;
- partición;
- lazy evaluation;
- task graph;
- acción/materialización;
- narrow vs wide dependency;
- shuffle;
- localidad de datos;
- fallo parcial y retry;
- diferencia entre paralelismo local y distribución.

### Qué se condensa
HDFS, Hadoop, MapReduce y YARN aparecen en un bloque conceptual de 25–30 min para explicar de
dónde vienen las ideas de particionar, mover datos y coordinar workers. **No se construye un
cluster Hadoop** y no hay laboratorio MapReduce separado.

### Laboratorio
Misma transformación SECOP en:
1. pandas;
2. Dask DataFrame;
3. comparación de particiones y task graph;
4. operación que no exige shuffle;
5. operación que sí exige shuffle;
6. tiempo + memoria + corrección;
7. mini-preview equivalente en Spark para preparar S12.

El resultado se valida por igualdad de conteos/hashes/agregados, no por "quién fue más rápido"
en una ejecución aislada.

### Evidencia
`benchmark_s11.json`: filas, particiones, operación, shuffle sí/no, tiempos, resultado de control.

### Puente
"Dask distribuye el trabajo; Spark añade un motor/optimizador y Databricks un entorno de
ejecución y persistencia. ¿Cómo cambia la arquitectura?"

---

# S12 · Spark y Databricks: del DataFrame al lakehouse

**Fecha:** 29 de octubre de 2026

### Reutilización
Partir de `9_Databricks_Serverless_Completo.ipynb` y
`11_Spark_SECOP_Solucion_Taller.ipynb`, recortando toda introducción que S11 ya cubrió.

### Conceptos
- SparkSession;
- DataFrame distribuido;
- transformación y acción;
- Catalyst;
- physical plan / `explain()`;
- cache/persist;
- broadcast join y shuffle join;
- particionado;
- Parquet;
- Delta Lake;
- transaction log;
- `MERGE`;
- Bronze / Silver / Gold como patrón, no como dogma.

### Laboratorio
SECOP:
raw/bronze → limpieza/silver → indicador/gold.
Comparar Parquet vs tabla Delta; ejecutar `MERGE`; leer el plan; provocar un join costoso y
mejorarlo con una decisión verificable.

### Evidencia
Tabla Delta + `explain` capturado como texto/JSON + métricas de filas por capa + prueba de
idempotencia del `MERGE`.

### Puente
"Un notebook ejecuta el pipeline. ¿Quién decide cuándo corre, qué se reintenta y qué ocurre si
falla la mitad?"

---

# S13 · Orquestación: Airflow, idempotencia y recuperación

**Fecha:** 5 de noviembre de 2026

### Conceptos
- workflow/DAG;
- task;
- dependencia;
- schedule;
- data interval;
- retry;
- timeout;
- backfill;
- idempotencia;
- estado;
- sensor solo como concepto/uso puntual;
- separación entre orquestar y procesar.

### Laboratorio
Convertir una versión pequeña del pipeline S10/S12 en un DAG:
1. adquirir;
2. validar RAW;
3. transformar;
4. escribir artefacto;
5. ejecutar control de calidad.

Provocar un fallo controlado, reintentar y demostrar que no duplica resultados.

### Infraestructura
Reutilizar el material Airflow/DuckDB existente, pero corregir antes el montaje de
`Airflow/dw.duckdb` señalado en PENDIENTES. Si esa corrección no está lista, usar una ruta de
datos creada por el contenedor y no el archivo histórico versionado.

### Evidencia
estado de tareas + ejecución fallida + reintento exitoso + hash/conteo estable.

### Puente
"Airflow sabe cuándo ejecutar. Pero si llegan datos continuamente, ¿debemos reprocesar todo?"

---

# S14 · De batch a incremental y streaming

**Fecha:** 12 de noviembre de 2026

### Alcance deliberado
No introducir Kafka como requisito operativo en esta edición: el costo de configuración no paga
el aprendizaje que buscamos. Kafka se explica como arquitectura de eventos; el laboratorio usa
**Spark Structured Streaming con fuente de archivos o rate source**, de manera reproducible.

### Conceptos
- batch completo;
- incremental;
- micro-batch;
- evento;
- event time vs processing time;
- checkpoint;
- offset;
- watermark;
- late data;
- deduplicación;
- at-least-once / exactly-once como propiedades condicionadas, no slogans.

### Laboratorio
Simular llegada progresiva de eventos SECOP:
1. recibir micro-lotes;
2. transformar;
3. deduplicar por clave;
4. manejar evento tardío;
5. persistir checkpoint;
6. detener/reanudar;
7. comprobar que el resultado no se reinicia desde cero.

### Evidencia
checkpoint + conteos por micro-lote + duplicados descartados + evento tardío observado.

### Puente
"Ahora el pipeline funciona en el tiempo. ¿Cómo sabemos que sigue sano, cuánto cuesta y dónde
servimos el resultado?"

---

# S15 · Del notebook al sistema: integración, observabilidad y preparación del proyecto final

**Fecha:** 19 de noviembre de 2026

### Objetivo
No añadir otra herramienta. Integrar las decisiones del semestre en una arquitectura que pueda
defenderse y recuperarse.

### Conceptos
- data contract;
- lineage;
- quality gate;
- freshness;
- latency;
- throughput;
- observability;
- SLI/SLO a nivel introductorio;
- costo de cómputo/almacenamiento;
- RPO/RTO;
- serving model especializado.

### Reto integrado
Cada equipo recibe un escenario y selecciona, mediante decisiones justificadas por evidencia:
- ingesta;
- modelo de almacenamiento;
- procesamiento local/distribuido;
- batch/incremental;
- serving especializado: MongoDB, Cassandra, Neo4j, lexical/vectorial;
- controles de calidad;
- métrica operacional;
- estrategia de recuperación.

La entrega no es una caja de texto del LMS. Es un paquete estructurado generado por código:
`architecture_manifest.json`, diagrama y controles verificables.

### Función pedagógica
S15 es un **ensayo técnico de S16**. El feedback se usa para corregir antes de la evaluación
final; no se agrega contenido nuevo durante los últimos 45 minutos.

---

# S16 · Reserva

S16 debe quedar para evaluación/proyecto final y cierre. No usarla para "alcanzar temario".
Si una parte de S10–S14 no alcanza, convertirla en extensión opcional o eliminarla; no desplazar
la evaluación.

---

## Qué no repetir

- MongoDB básico: ya está en S03/S04.
- Cassandra básica: ya está en S04/S05.
- Neo4j básico: ya está en S06.
- Elasticsearch/BM25: ya está en S07.
- búsqueda vectorial: ya está en S09.
- "qué es Big Data": ya está en S01.
- arquitectura genérica sin caso: ya está en S02.

Las sesiones nuevas deben **usar** esas capacidades, no volver a presentarlas.

## Criterio para controlar el ritmo

Una sesión está sobrecargada si introduce más de:
- 6–8 términos realmente nuevos;
- 2 mecanismos internos nuevos;
- 1 plataforma nueva;
- 1 artefacto principal de laboratorio.

Lo que no cumpla esta regla se mueve a una lectura/extension opcional.

## Plan técnico para la lentitud del LMS

Medición de logs de Supabase del 28-09-2026:

| Endpoint | p50 aprox. | p95 aprox. |
|---|---:|---:|
| `bigdata-session` | 2.15 s | 3.32 s |
| `bigdata-lms-core` | 2.08 s | 2.51 s |
| `bigdata-learning` | 1.87 s | 3.20 s |

Los índices V56 ya eliminaron los avisos de FK sin índice, pero la latencia sigue porque una
petición Edge Function encadena múltiples consultas PostgREST. En los logs, varias consultas
internas individuales cuestan ~150–380 ms; cuatro o cinco capas secuenciales producen segundos.

### Antes de S08 (cambio de bajo riesgo)
1. No refactorizar S08 a otra arquitectura tres días antes del taller.
2. Evitar refresh completos después de eventos que no cambian la UI.
3. Agrupar telemetría no crítica y heartbeats.
4. Renderizar el último modelo válido mientras se revalida en segundo plano.
5. Medir `Server-Timing` por fases: auth, run, definition, progress.

### V57 después de S08
1. Crear un bootstrap SQL/RPC que resuelva en una sola llamada:
   sesión de autenticación + usuario + matrícula/run.
2. Para `session.html`, crear un RPC de lectura que devuelva:
   definición + recursos + progreso + catálogo en un solo round-trip.
3. Sustituir los bucles de `activeRun()` por un join/RPC.
4. Mantener escritura granular, pero agrupar eventos de telemetría.
5. Cache stale-while-revalidate de 30–60 s para catálogo/definición.
6. Instrumentar p50/p95 por acción, no solo por función.

### Meta
- bootstrap visible p50 < 900 ms;
- p95 < 1.5 s;
- navegación con datos cacheados perceptualmente inmediata;
- ningún evento formativo debe bloquear la interfaz esperando telemetría.

No mover de región el proyecto como primera medida: el patrón observado es principalmente de
**demasiados round-trips internos**, no de falta de índices.
