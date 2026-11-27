# Tercera auditoría pedagógica · Compras Claras como producto acumulativo

## Resultado y alcance
Misma escala y mismos cuatro criterios de la [segunda auditoría](auditoria-pedagogica-poslimpieza.md): C claridad, P práctica auténtica prevista, A autonomía progresiva, E evidencia verificable. Pesos iguales. 1 ausente, 2 inicial, 3 suficiente con limitaciones, 4 sólido, 5 referente interno. Esta es una **valoración de diseño provisional**, no una medición de aprendizaje ni certificación de plataformas. La meta global de diseño es 4,5; no todas las sesiones alcanzan ese nivel individualmente. Antes 3,91; valoración actual 4.50/5. La puntuación no sustituye las pruebas pendientes.

| S | C | P | A | E | Media | Evidencia de diseño | Pendiente |
|---|---:|---:|---:|---:|---:|---|---|
| 01 | 5 | 4 | 5 | 5 | 4.75 | Adquisición acotada, identidad, fuente, comparación de escalas y exportación independiente. | Consulta API y escalamiento real pendientes de QA externo. |
| 02 | 5 | 4 | 5 | 5 | 4.75 | Requisitos → arquitectura; elección y alternativa exportables sin instalar servicios. | Latencias supuestas; revisar PR del estudiante. |
| 03 | 4 | 4 | 4 | 4 | 4.00 | Expedientes del mismo corpus y explain controlado en motor real previsto. | Cuaderno extenso; comprobar explain real en Colab. |
| 04 | 5 | 4 | 4 | 4 | 4.25 | Bandeja persistible, recuperación local y ping de Atlas separado del respaldo. | Conectividad y disponibilidad real aún no comprobadas. |
| 05 | 5 | 4 | 4 | 5 | 4.50 | Grupos, clave alternativa y contrato CQL–pandas explícito. | Comprobar segunda consulta real con otra clave. |
| 06 | 4 | 4 | 4 | 5 | 4.25 | Relaciones trazables, referencia independiente y contraste de vecindario. | Material extenso; validar Aura y consistencia del NIT. |
| 07 | 5 | 4 | 5 | 5 | 4.75 | BM25 calculado, comparación de pesos en el motor y rankings exportables. | Validar Elasticsearch remoto y ampliar juicios de pertinencia. |
| 08 | 5 | 4 | 4 | 5 | 4.50 | Hito V1.0 verificable por integridad de IDs y manifiesto oficial intacto. | Validar preflight de las tres cuentas; no sustituir TC1. |
| 09 | 5 | 4 | 5 | 5 | 4.75 | Tres rankings locales, alternativa, evidencia E5 separada y estado Atlas declarado. | TF-IDF local no semántico; ejecutar Atlas/ANN real. |
| 10 | 5 | 4 | 5 | 5 | 4.75 | Inventario real, selección de muestra, transformación física y comparación de tamaños. | Ejecutar transformación en Colab y validar audio. |
| 11 | 4 | 4 | 4 | 4 | 4.00 | Catálogo con procedencia y texto real adjunto, sin fabricar OCR/ASR. | Rama especializada y modelos externos sin QA actual; falta incorporar más fuentes reales. |
| 12 | 5 | 4 | 4 | 5 | 4.50 | Hito V2.0, controles del catálogo y resumen de informe real previsto. | Validar el taller completo; no modificar rúbrica. |
| 13 | 5 | 4 | 5 | 5 | 4.75 | Particiones y reducción verificables; contraste de workers en cuaderno y evidencia independiente. | Dask real no ejecutado en esta revisión. |
| 14 | 5 | 4 | 4 | 5 | 4.50 | Tabla analítica, planes y MLlib del cuaderno diferenciados de agregación portable. | Confirmar Spark/Delta en Databricks. |
| 14A | 5 | 4 | 4 | 4 | 4.25 | Comparación de escala y presupuesto explícito, adjunto de entrenamiento si se ejecuta. | No existe nueva prueba de entrenamiento masivo remoto. |
| 15 | 5 | 5 | 5 | 5 | 5.00 | Pipeline incremental con repetición y rechazo comprobados; laboratorio SQLite previo real y transferencia autónoma. | Ampliación Spark Streaming no verificada. |
| 16 | 5 | 4 | 4 | 4 | 4.25 | Observatorio acumulativo y trazabilidad final; métricas locales y MLlib diferenciadas. | Integrar predicciones Spark reales y comprobar entrega final en su entorno. |

## Cambios que sustentan la valoración
- Claridad: la portada y el LMS enlazan a un observatorio único; cada sesión consume el entregable anterior y tiene problema, decisión, resultado, interpretación y siguiente paso. La consulta conceptual anterior se conserva como apoyo. Los materiales extensos de S03/S06/S11 aún limitan claridad.
- Práctica: se preservan laboratorios auténticos y se agregan 17 experimentos específicos. El navegador calcula BM25, coseno TF-IDF, RRF, relaciones documentadas, agregación e incrementalidad con datos reales de muestra. **No ejecuta MongoDB, Cassandra, Neo4j, Elasticsearch, Atlas, OCR/ASR, Dask ni Spark.** P evalúa diseño previsto; no acredita ejecución. S15 tiene una prueba local SQLite previa de rollback e idempotencia.
- Autonomía: comparar decisiones sin alterar el producto, reabrir etapa e invalidar dependencias, recuperar un estado, ejecutar demo de referencia y exportar artefactos; distinguir respaldo y trabajo propio. No hay respuestas abiertas obligatorias nuevas.
- Evidencia: huellas de continuidad, recálculo de estados importados, verificación SHA-256 de JSON de laboratorios, resultados específicos y separación de fuentes. SHA verifica integridad, no identidad del autor ni ejecución del motor.

## Verificaciones realizadas
- 153 ejecuciones de etapa en nueve recorridos (40/80/120 procesos, tres conjuntos de decisiones); 9 reimportaciones recalculadas; 306 comparaciones de alternativas. Ruta obligatoria sin S14A comprobada previamente.
- 17 interacciones de ejecución y comparación, seis vistas, reset y demostración probadas mediante DOM simulado en la versión precedente; no equivale a navegador real.
- SHA-256 contrastado con hashlib de Python (texto UTF-8 con acentos), verificación de un adjunto y rechazo de alteración.
- HTML autónomo sincronizado con generador, corpus de 200 procesos e inventario de 32 imágenes; 17 tarjetas con dos accesos principales.
- No se ejecutaron procesos pesados en Actions. No se fusionó la rama.

## Para cerrar la aceptación
1. QA visual real, móvil y desktop, y verificación de la URL de staging. El proxy de HTML externo no respondió desde este entorno; Codespaces está configurado para servidor estático en puerto 8000, no probado en sesión remota.
2. Ejecutar las 17 recetas de evidencia en sus entornos (especialmente S03, S04, S06, S11 y S14A). Corregir incompatibilidades detectadas antes de publicar.
3. Comprobar que los estudiantes pueden seguir el hilo sin asistencia; recoger evidencias de modificaciones y tiempos de trabajo.
4. Mantener intactas las condiciones de evaluación vigentes y no presentar modelos sintéticos, resultados portables o adjuntos como ejecuciones remotas verificadas.
