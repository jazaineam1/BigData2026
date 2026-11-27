# Estándar de reconstrucción de Big Data · 150 minutos

No se considera que una guía de cinco bloques, un contador de palabras o una planificación de tiempos constituyan una sesión completa. Se reconstruye sesión por sesión y se conserva main. El mínimo solicitado es 20 diapositivas de enseñanza (la pausa no cuenta), 3.000 palabras de contenido pedagógico propio (20 palabras por minuto × 150 minutos), explicación desde cero de los términos, ejemplos resueltos con datos y resultados, prácticas ejecutables con el cuaderno y transferencia de una capacidad al producto. No contar código, navegación, títulos, relleno ni palabras repetidas automáticamente. Las palabras de enseñanza pueden distribuirse entre proyección y lectura ampliada por diapositiva; en móvil se muestra la lectura. No sacrificar legibilidad por densidad. Se conserva el cuaderno principal como segundo recurso. El panel de progreso queda fuera del modo proyección. No alterar rúbricas vigentes.

## Criterio de aceptación
- 20 o más diapositivas de enseñanza; 150 minutos incluyendo descanso; al menos 3.000 palabras de explicación, ejemplo, práctica y lectura de resultados.
- Cada concepto sigue problema, definición, intuición, ejemplo numérico/manual, aplicación, interpretación y error frecuente. No asumir familiaridad con motores nuevos.
- Al menos cuatro experimentos específicos del tema con parámetros modificables; varios resultados calculados con datos reales cuando exista fuente. Distinguir ejemplo sintético, cálculo didáctico, ejecución local y ejecución remota.
- Un laboratorio principal completo: instalación/conexión, entrada, código, resultado esperado, verificación, modificación autónoma, exportación y limitaciones. Sin nuevos costos obligatorios. No afirmar ejecución externa sin comprobarla.
- Auditoría con los cuatro criterios previos (claridad, práctica, autonomía, evidencia), más puertas de profundidad y legibilidad; no calificar una sesión como aceptada solo por cantidad. Meta 4,5 por sesión, no únicamente media global.
- QA ligero: referencias, esquemas, código y resultados locales; QA visual de proyección/móvil; pruebas externas manuales justificadas. No ejecutar benchmarks pesados automáticamente.

## Secuencia de reconstrucción
| Sesión | Núcleo de enseñanza y práctica | Producto |
|---|---|---|
| S01 | Cinco V, infraestructura, formatos, pandas, API, texto, paginación, fragmentación, calidad y trazabilidad | RAW de procesos |
| S02 | Requisitos, BPM, arquitectura, ciclo analítico, Git y contratos; comparar diseños y versionar | Arquitectura |
| S03 | JSON/BSON, modelo documental, CRUD, agregaciones, índices, consistencia; consultar y medir explain | Expedientes |
| S04 | Atlas, conexión, persistencia, réplica, vistas, faltantes; comprobar consultas | Bandeja |
| S05 | Cassandra, CQL, clave y clustering, distribución y concentración; dos patrones de consulta reales | Tabla operacional |
| S06 | Grafos, identidad, Cypher, caminos, grado, idempotencia y validación independiente | Contexto relacional |
| S07 | Tokenización, índice invertido, TF/DF/IDF, BM25, mapping, DSL, relevancia y ranking | Buscador |
| S08 | TC1: ingesta, concurrencia, tres motores, controles y diagnóstico; no alterar rúbrica | V1 |
| S09 | Vectores, coseno, E5, Atlas, ANN/ENN, filtros, RRF, relevancia | Recuperación |
| S10 | Píxeles, canales, histogramas, resolución, audio, FFT/RMS/espectrograma y ETL | Catálogo |
| S11 | OCR, PSM, ASR, WER, embeddings, extracción y recuperación trazable | Investigador multimedia |
| S12 | TC2: recuperar, medir, procesar activos y verificar ETL; rúbrica original | V2 |
| S13 | HDFS, MapReduce, Dask, procesos, workers, particiones, Amdahl y K-means | Motor distribuido |
| S14 | Spark, DAG, stages/tasks, shuffle, joins, SQL, Delta, Medallion y MLlib | Motor analítico |
| S14A | Escala sintética, memoria, split, dos modelos, evaluación y persistencia, opcional | Expediente de capacidad |
| S15 | Batch/microbatch/streaming, transacciones, idempotencia, rollback, checkpoint y cambios de esquema | Actualización fiable |
| S16 | Integración, evaluación, predicciones trazables, observatorio y defensa | V3 |

S01 es el piloto. S02–S16 y S14A todavía no están reconstruidas con este estándar. No fusionar hasta validar.
